# arcgis_dashboard_extract.py
# Purpose: Discover FeatureServer layers used by an ArcGIS Experience dashboard
#          and download their attributes to CSV.

import re
import json
import time
from urllib.parse import urlparse
import requests
import pandas as pd

DASHBOARD_URL = "https://experience.arcgis.com/experience/cdc36bd2902447288b262fc983f4013d/page/Page?views=Legend#data_s=id%3AdataSource_2-19613c0263a-layer-4%3A5031229%2Cid%3AdataSource_2-1eb1e374add8449a9bbb082f69668ce0%3A2"  # e.g. https://experience.arcgis.com/experience/....../page/....

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def find_featureserver_urls(html: str):
    """
    Find ArcGIS FeatureServer URLs referenced in the page source.
    """
    # Common patterns:
    # https://services.arcgis.com/.../arcgis/rest/services/.../FeatureServer
    # https://<something>.arcgis.com/.../FeatureServer
    pattern = re.compile(
        r"https?://[^\s\"']+?/arcgis/rest/services/[^\s\"']+?/FeatureServer",
        re.IGNORECASE
    )
    urls = sorted(set(pattern.findall(html)))
    return urls

def list_layers(featureserver_url: str):
    """
    Get service metadata to list layers/tables.
    """
    url = featureserver_url.rstrip("/") + "?f=pjson"
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    meta = r.json()
    layers = meta.get("layers", [])
    tables = meta.get("tables", [])
    return layers, tables

def fetch_all_rows(layer_url: str, out_fields="*", where="1=1", chunk_size=2000):
    """
    Pull all rows from a FeatureServer layer/table using pagination (resultOffset).
    Returns a pandas DataFrame of attributes.
    """
    all_rows = []
    offset = 0

    while True:
        params = {
            "f": "json",
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "false",
            "resultRecordCount": chunk_size,
            "resultOffset": offset,
        }
        r = requests.get(layer_url.rstrip("/") + "/query", params=params, headers=HEADERS, timeout=120)
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            raise RuntimeError(f"ArcGIS error: {data['error']}")

        features = data.get("features", [])
        if not features:
            break

        # Extract attributes
        for f in features:
            all_rows.append(f.get("attributes", {}))

        offset += len(features)

        # Stop if server says no more
        if not data.get("exceededTransferLimit", False) and len(features) < chunk_size:
            break

        time.sleep(0.1)

    return pd.DataFrame(all_rows)

def safe_name(s: str):
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", s).strip("_")

def main():
    if "PASTE_YOUR" in DASHBOARD_URL:
        raise ValueError("https://experience.arcgis.com/experience/cdc36bd2902447288b262fc983f4013d/page/Page?views=Legend#data_s=id%3AdataSource_2-19613c0263a-layer-4%3A5031229%2Cid%3AdataSource_2-1eb1e374add8449a9bbb082f69668ce0%3A2")

    print(f"Opening dashboard page:\n  {DASHBOARD_URL}\n")
    r = requests.get(DASHBOARD_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    html = r.text

    fs_urls = find_featureserver_urls(html)
    if not fs_urls:
        print("❌ Could not find FeatureServer URLs in the initial HTML.")
        print("✅ Try this workaround:")
        print("   - Open the dashboard in your browser")
        print("   - Ctrl+U (View Page Source)")
        print("   - Search for: 'FeatureServer' or '/arcgis/rest/services/'")
        print("   - Copy any FeatureServer URL you find and paste it into this script directly.")
        return

    print("✅ Found FeatureServer(s):")
    for u in fs_urls:
        print("  -", u)

    for fs in fs_urls:
        print(f"\n--- Inspecting service: {fs}")
        layers, tables = list_layers(fs)

        targets = []
        for lyr in layers:
            targets.append(("layer", lyr["id"], lyr.get("name", f"layer_{lyr['id']}")))
        for tbl in tables:
            targets.append(("table", tbl["id"], tbl.get("name", f"table_{tbl['id']}")))

        if not targets:
            print("  (No layers/tables listed on this service.)")
            continue

        print("  Available layers/tables:")
        for kind, lid, name in targets:
            print(f"   - {kind} {lid}: {name}")

        # Download EVERYTHING by default (you can comment out ones you don’t need)
        for kind, lid, name in targets:
            layer_url = fs.rstrip("/") + f"/{lid}"
            print(f"\n  ⬇ Downloading {kind} {lid}: {name}")
            df = fetch_all_rows(layer_url)

            if df.empty:
                print("   (No rows returned)")
                continue

            out_csv = f"{safe_name(urlparse(fs).path.split('/')[-3])}_{safe_name(name)}.csv"
            df.to_csv(out_csv, index=False)
            print(f"   ✅ Saved {len(df):,} rows to: {out_csv}")

if __name__ == "__main__":
    main()

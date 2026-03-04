import os
from run_examples import run_scenarios

if __name__ == "__main__":
    scs_path = os.path.join(os.path.dirname(__file__), "studies", "rockingham_study", "scenarios")

    cc = os.path.join(scs_path, "constant_config_pool.csv")
    sc = os.path.join(scs_path, "rockingham_res7.csv")

    run_scenarios(cc, sc, n_parallel_sim=1, n_cpu_per_sim=1, log_level="info")
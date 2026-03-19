# ----------------------------------------------------------------------------- 
# Imports
# ----------------------------------------------------------------------------- 

# Standard library
import logging
import os
from typing import Any, Dict, Tuple
import copy

# Third-party libraries
import numpy as np

# Local imports
from data_loader import(
    load_validate_data,
    add_batches_to_data
)

from utils import (
    evaluate_batches
)

from solver_models import (
    run_batching,
    run_picking,
    run_main_model
)

from heuristics import (
    run_greedy,
    run_local_search_swap
)

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

def main():
    BASE_DIR = os.path.dirname(__file__)
    matrix_path = os.path.join(BASE_DIR, "toy_data", "matrix.txt")
    orders_path = os.path.join(BASE_DIR, "toy_data", "orders.txt")
    constraints_path = os.path.join(BASE_DIR, "toy_data", "constraints.txt")

    data = load_validate_data(matrix_path, orders_path, constraints_path)
    tests = {
        "model_picking": run_picking,
        "model_batching" : run_batching,
        "greedy_batching": run_greedy,
        "local_search_swap": run_local_search_swap,
        "main_model": run_main_model
    }
    # --- MAIN MODEL ---
    data_base1 = data
    travel1, objective1, time = tests["main_model"](data)

    # --- MODEL BATCHING ---
    data_base = data
    batches, pickers_locations = tests["model_batching"](data)
    score = evaluate_batches(batches, data["common_locations"])
    new_batches = tests["local_search_swap"](batches, data)
    score_new = evaluate_batches(new_batches, data["common_locations"])
    data_model = add_batches_to_data(data, new_batches, pickers_locations)

    travel, objective = tests["model_picking"](data_model)

    logger.info("=== MODEL BATCHING ===")
    logger.info("travel=%s", travel)
    logger.info("objective=%s", objective)
    logger.info("=== MAIN MODEL ===")
    logger.info("travel=%s", travel1)
    logger.info("objective=%s", objective1)
    logger.info("time=%s secondes", time)

    """
    # --- GREEDY BATCHING ---
    batches2, pickers_locations2 = tests["greedy_batching"](data_base)
    score2 = evaluate_batches(batches2, data_base["common_locations"])
    new_batches2 = tests["local_search_swap"](batches2, data_base)
    score_new2 = evaluate_batches(new_batches2, data_base["common_locations"])
    data_greedy = add_batches_to_data(data_base, new_batches2, pickers_locations2)

    travel2, objective2 = tests["model_picking"](data_greedy)

    ### vis

    logger.info("=== MODEL BATCHING ===")
    logger.info("batches=%s", batches)
    logger.info("pickers_locations=%s", pickers_locations)
    logger.info("travel=%s", travel)
    logger.info("objective=%s", objective)

    logger.info("=== GREEDY BATCHING ===")
    logger.info("batches=%s", batches2)
    logger.info("pickers_locations=%s", pickers_locations2)
    logger.info("travel=%s", travel2)
    logger.info("objective=%s", objective2)

    print("\n===== SUMMARY =====")
    print(f"Model batching + local search swap + Model Picking, cost : {objective}")
    print(f"Greedy batching + local search swap + Model Picking, cost: {objective2}")

    if objective <= objective2:
        print("Best method: model batching")
    else:
        print("Best method: greedy batching")"""

if __name__ == "__main__":
    main()
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
    run_local_search_swap,
    run_local_search_move
)

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
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
        "1": ("Main Model", run_main_model),
        "2": ("Model Batching + Model Picking", run_batching),
        "3": ("Greedy Batching + Model Picking", run_picking),
        "0": ("Exit", None)
    }

    while True:
        print("\n===== BATCHING & PICKING MENU =====")
        for key, (name, _) in tests.items():
            print(f"{key}: {name}")
        choice = input("Select an option to run: ").strip()

        if choice not in tests:
            print("Invalid choice, please try again.")
            continue
        if choice == "0":
            print("Exiting program.")
            break

        name, func = tests[choice]
        print(f"\n--- Running {name} ---")

        if choice == "1":  # Main Model
            batches1, travel1, objective1, time = func(data)
            logger.info("=== MAIN MODEL ===")
            logger.info("travel=%s", travel1)
            logger.info("objective=%s", objective1)
            logger.info("time=%s seconds", time)

        elif choice == "2":  # Model Batching + Model Picking
            batches, pickers_locations = run_batching(data)
            data_model = add_batches_to_data(data, batches, pickers_locations)
            travel, objective = run_picking(data_model)
            logger.info("=== MODEL BATCHING + MODEL PICKING ===")
            logger.info("travel=%s", travel)
            logger.info("objective=%s", objective)

        elif choice == "3":  # Greedy Batching + Model Picking
            batches, pickers_locations = run_greedy(data)
            data_model = add_batches_to_data(data, batches, pickers_locations)
            travel, objective = run_picking(data_model)
            logger.info("=== GREEDY BATCHING + MODEL PICKING ===")
            logger.info("travel=%s", travel)
            logger.info("objective=%s", objective)

if __name__ == "__main__":
    main()
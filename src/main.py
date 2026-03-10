# ----------------------------------------------------------------------------- 
# Imports
# ----------------------------------------------------------------------------- 

# Standard library
import logging
import os
from typing import Any, Dict, Tuple

# Third-party libraries
import numpy as np

# Local imports
from data_loader import(
    load_validate_data,
    add_batches_to_data
)

from checker.solution_checker import (
    check_batching_solution,
    check_picking_solution
)

from solver_models import (
    model_batching,
    model_picking
)

from utils import (
    get_picker_locations_from_ifloc
)

from heuristics import greedy_order_batching

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

def test_batching(data):
    batches = model_batching(data)
    check_batching = check_batching_solution(batches, data)
    logger.debug("Check batching solution: %s", check_batching)
    print(check_batching)
    if not check_batching[0]:
        logger.critical("Batching solution is INVALID. Erros: %s", check_batching[1])
        raise ValueError(f"Batching solution is INVALID: {check_batching[1]}")
    # get locations for each picker
    locations_pickers = get_picker_locations_from_ifloc(batches, data["loc_in_order"], data["num_locations"])
    return batches, locations_pickers

def test_greedy(data):
    batches = greedy_order_batching(data)
    check_batching = check_batching_solution(batches, data)
    logger.debug("Check batching solution: %s", check_batching)
    if not check_batching[0]:
        logger.critical("Batching solution is INVALID. Erros: %s", check_batching[1])
        raise ValueError(f"Batching solution is INVALID: {check_batching[1]}")
    # get locations for each picker
    locations_pickers = get_picker_locations_from_ifloc(batches, data["loc_in_order"], data["num_locations"])
    return batches, locations_pickers

def test_picking(data):
    travel, objective = model_picking(data)
    check_picking = check_picking_solution(travel, data["num_locations"])
    logger.debug("Check batching solution: %s", check_picking)
    if not check_picking[0]:
        logger.critical("Picking solution is INVALID. Erros: %s", check_picking[1])
        raise ValueError(f"Picking solution is INVALID: {check_picking[1]}")
    return travel, objective

def main():
    BASE_DIR = os.path.dirname(__file__)
    matrix_path = os.path.join(BASE_DIR, "toy_data", "matrix.txt")
    orders_path = os.path.join(BASE_DIR, "toy_data", "orders.txt")
    constraints_path = os.path.join(BASE_DIR, "toy_data", "constraints.txt")

    data = load_validate_data(matrix_path, orders_path, constraints_path)
    tests = {
        "model_picking": test_picking,
        "model_batching" : test_batching,
        "greedy_batching": test_greedy
    }

    # --- MODEL BATCHING ---
    batches, pickers_locations = tests["model_batching"](data)
    data_model = add_batches_to_data(data, batches, pickers_locations)

    travel, objective = tests["model_picking"](data_model)

    # --- GREEDY BATCHING ---
    batches2, pickers_locations2 = tests["greedy_batching"](data)
    data_greedy = add_batches_to_data(data, batches2, pickers_locations2)

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
    print(f"Model batching + Model Picking, cost : {objective}")
    print(f"Greedy batching + Model Picking, cost: {objective2}")

    if objective <= objective2:
        print("Best method: model batching")
    else:
        print("Best method: greedy batching")

if __name__ == "__main__":
    main()
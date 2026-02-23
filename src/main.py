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
from checker.instance_checker import (
    check_distance_matrix,
    check_orders,
    check_constraints,
)

from checker.solution_checker import (
    check_batching_solution,
    check_picking_solution
)

from data_loader import (
    load_matrix,
    load_orders,
    load_constraints
)

from solver_models import (
    model_batching,
    model_picking
)

from utils import (
    get_locations_and_orders_counts,
    max_pickers_bounds,
    is_loc_in_order,
    common_elements,
    get_picker_locations_from_ifloc
)

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------

def load_validate_data(adj_matrix_path: str, orders_path: str, constraints_path: str) -> Dict[str, Any]:
    """
    Load and validate all input data required for the batching model.

    Args:
        adj_matrix_path (str): Path to adjacency matrix file
        orders_path (str): Path to orders file
        constraints_path (str): Path to constraints file

    Returns:
        dict: A dictionary containing all data needed for the batching model
    """

    logger.info("Loading Data...")

    # --- Load and validate adjacency matrix ---
    adj_matrix = load_matrix(adj_matrix_path)
    check_mat = check_distance_matrix(adj_matrix)
    logger.debug("Check matrix %s: %s", adj_matrix_path, check_mat)
    if not check_mat[0]:
        logger.critical("Distance matrix %s is INVALID. Errors: %s", adj_matrix_path, check_mat[1])
        raise ValueError(f"Distance matrix {adj_matrix_path} is invalid: {check_mat[1]}")

    # --- Load and validate orders ---
    orders = load_orders(orders_path)
    check_ord = check_orders(orders)
    logger.debug("Check orders %s: %s", orders_path, check_ord)
    if not check_ord[0]:
        logger.critical("Orders %s are INVALID. Errors: %s", orders_path, check_orders[1])
        raise ValueError(f"Orders file {orders_path} is invalid: {check_orders[1]}")

    # --- Load and validate constraints ---
    constraints = load_constraints(constraints_path)
    check_constr = check_constraints(constraints)
    logger.debug("Check constraints %s: %s", constraints_path, check_constr)
    if not check_constr[0]:
        logger.critical("Constraints %s are INVALID. Erros: %s", constraints_path, check_constraints[1])
        raise ValueError(f"Constraints file {constraints_path} is invalid: {check_constraints[1]}")
    
    # --- Compute derived information from raw inputs ---
    # Number of locations and number of orders
    num_locations, num_orders = get_locations_and_orders_counts(adj_matrix, orders)

    # Maximum orders per batch and maximum batch volume
    max_nb_orders, max_vol = constraints

    # Volume of each order
    order_volumes = [orders[number]["volume"] for number in range(num_orders)]

    # Compute the bounds for the number of pickers required.
    lower_bound, upper_bound = max_pickers_bounds(orders, num_orders, max_nb_orders, max_vol, order_volumes)
    min_pickers = lower_bound
    max_pickers = upper_bound

    # Binary matrix: 1 if location is included in order, 0 otherwise
    loc_in_order = is_loc_in_order(num_locations, orders)

    # Count of shared locations between each pair of orders
    common_locations = common_elements(loc_in_order, num_orders, num_locations)

    # --- Build data dictionary ---
    data = {
        "adj_matrix": adj_matrix,
        "loc_in_order": loc_in_order,
        "order_volumes": order_volumes,
        "num_locations": num_locations,
        "num_orders": num_orders,
        "min_pickers": min_pickers,
        "max_pickers": max_pickers,
        "max_nb_orders": max_nb_orders,
        "max_vol": max_vol,
        "common_locations": common_locations
    }
    return data

def add_data_for_picking_model(data, batches, pickers_locations):
    """
    Add batching solution and picker locations to the data dictionary.

    Args:
        data (dict): Original data dictionary
        batches (np.ndarray): Batching solution
        locations_pickers (np.ndarray): Picker location assignments

    Returns:
        dict: Updated data dictionary
    """
    data["batches"] = batches
    data["pickers_locations"] = pickers_locations
    return data

def test_batching(data):
    batches = model_batching(data)
    check_batching = check_batching_solution(batches, data["order_volumes"], data["max_nb_orders"], data["max_vol"])
    logger.debug("Check batching solution: %s", check_batching)
    if not check_batching[0]:
        logger.critical("Batching solution is INVALID. Erros: %s", check_batching[1])
        raise ValueError(f"Batching solution is INVALID: {check_batching[1]}")
    # get locations for each picker
    locations_pickers = get_picker_locations_from_ifloc(batches, data["loc_in_order"], data["num_locations"])
    return batches, locations_pickers

def test_picking(data):
    travel = model_picking(data)
    check_picking = check_picking_solution(travel, data["num_locations"])
    logger.debug("Check batching solution: %s", check_picking)
    if not check_picking[0]:
        logger.critical("Picking solution is INVALID. Erros: %s", check_picking[1])
        raise ValueError(f"Picking solution is INVALID: {check_picking[1]}")
    return travel

def main():
    BASE_DIR = os.path.dirname(__file__)
    matrix_path = os.path.join(BASE_DIR, "toy_data", "matrix.txt")
    orders_path = os.path.join(BASE_DIR, "toy_data", "orders.txt")
    constraints_path = os.path.join(BASE_DIR, "toy_data", "constraints.txt")

    data = load_validate_data(matrix_path, orders_path, constraints_path)
    tests = {
        "picking": test_picking,
        "batching" : test_batching
    }

    # test model batching
    batches, pickers_locations = tests["batching"](data)
    data = add_data_for_picking_model(data, batches, pickers_locations)

    # test model picking
    travel = tests["picking"](data)

if __name__ == "__main__":
    main()
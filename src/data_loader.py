# ----------------------------------------------------------------------------- 
# Imports
# ----------------------------------------------------------------------------- 

# Standard library
import logging
from typing import List, Dict, Any
from pathlib import Path

# Third-party libraries
import numpy as np

# Local imports
from checker.instance_checker import (
    check_distance_matrix,
    check_orders,
    check_constraints,
)

from utils import (
    get_locations_and_orders_counts,
    max_pickers_bounds,
    is_loc_in_order,
    common_elements,
)

logger = logging.getLogger(__name__)

def load_matrix(path: str | Path) -> np.ndarray:
    """
    Load a square adjacency matrix from a file.
    Supports text (.txt) with a header line, or NumPy binary (.npy).

    Text format expected:
        - First line: number of locations (optional, can be used for verification)
        - Remaining lines: square matrix (space, tab, or comma separated)

    Args:
        path (str | Path): Path to the matrix file.

    Returns:
        np.ndarray: Loaded square matrix.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the matrix is not square or size doesn't match header.
    """

    # Convert string paths to Path objects for cross-platform safety
    if isinstance(path, str):
        path = Path(path)

    # Ensure the file exists
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    if path.suffix == ".npy":
        # Binary format: fast and exact
        adj_mat = np.load(path)

        if adj_mat.ndim != 2 or adj_mat.shape[0] != adj_mat.shape[1]:
            raise ValueError("Loaded matrix must be 2D and square")
        
        adj_mat = adj_mat.tolist()
        return adj_mat
    
    # Text format: handle header line
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Boolean for
    header = False

    # Get number of location
    try:
        nb_loc = int(lines[0].strip())
        if nb_loc == len(lines) - 1:
            header = True
    except ValueError:
        pass

    
    # Initialize an empty NumPy array
    adj_mat = np.zeros((nb_loc, nb_loc), dtype=float)

    if header == True:
        # Fill in the matrix
        for i in range(nb_loc):
            row = [float(x) for x in lines[i + 1].strip().split()]
            adj_mat[i] = row

        adj_mat = adj_mat.tolist()
        return adj_mat

    else: 
        for i in range(nb_loc):
            row = [float(x) for x in lines[i].strip().split()]
            adj_mat[i] = row
        
        adj_mat = adj_mat.tolist()
        return adj_mat

def load_orders(path: str | Path):
    """
    Load orders from a text file.

    Expected file format:
        - First line: number of orders
        - Then for each order (2 lines):
            line 1: order_id volume number_of_locations
            line 2: list of location IDs

    Args:
        path (str | Path): Path to the orders file.

    Returns:
        list[dict]: List of orders with the following structure:
            {
                "id": int,
                "volume": int,
                "nb_locations": int,
                "locations_list": list[int],
                "locations_set": set[int]
            }

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the number of parsed orders does not match the header.
    """
    
    # Convert string paths to Path objects for safer filesystem handling
    if isinstance(path, str):
        path = Path(path)

    # Check that the file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Read file and remove empty lines
    with path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # First line indicates the number of orders
    nb_orders = int(lines[0])

    orders = []

    # Each order is described by two lines
    #   line i   -> order information
    #   line i+1 -> list of locations
    for i in range(1, len(lines), 2):

        # Parse order metadata
        info = lines[i].split()
        number = int(info[0])
        volume = int(info[1])
        nb_locations = int(info[2])

        # Parse the list of locations
        spots = list(map(int, lines[i+1].split()))

        # Store the order in a structured dictionary
        orders.append({
            "id": number,
            "volume": volume,
            "nb_locations": nb_locations,
            "locations_list": spots[:nb_locations],  # ordered list
            "locations_set": set(spots[:nb_locations])  # set for fast lookup
        })

    # Verify consistency with the header
    if len(orders) != nb_orders:
        raise ValueError("Number of orders does not match header")

    return orders

def load_constraints(path: str | Path):
    """
    Load constraints from a text file.

    Expected file format:
        - One line with maximum number of orders for a picker and maximum volume for a picker

    Args:
        path (str | Path): Path to the orders file.

    Returns:
        list[int]: List containing the maximum number of orders for a picker
                   and the maximum volume for a picker.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    constraints = []

    if isinstance(path, str):
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found : {path}")
    
    # Text format: handle header line
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    line = lines[0].strip().split()
    constraints.append(int(line[0]))
    constraints.append(int(line[1]))

    return constraints

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
        logger.critical("Orders %s are INVALID. Errors: %s", orders_path, check_ord[1])
        raise ValueError(f"Orders file {orders_path} is invalid: {check_ord[1]}")

    # --- Load and validate constraints ---
    constraints = load_constraints(constraints_path)
    check_constr = check_constraints(constraints)
    logger.debug("Check constraints %s: %s", constraints_path, check_constr)
    if not check_constr[0]:
        logger.critical("Constraints %s are INVALID. Erros: %s", constraints_path, check_constr[1])
        raise ValueError(f"Constraints file {constraints_path} is invalid: {check_constr[1]}")
    
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

def add_batches_to_data(data, batches, pickers_locations):
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
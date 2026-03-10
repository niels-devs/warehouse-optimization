from typing import List, Dict, Tuple

def check_distance_matrix(matrix: List[List[float]]) -> Tuple[bool, List[str]]:
    """
    Check that a distance matrix is valid.
    Assumes matrix is a list of lists (loaded by load_matrix).
    
    Checks:
      - Square matrix
      - All rows same length
      - Non-negative distances
      - Diagonal is zero

    Args:
        matrix (list[list[float]]): The loaded adjacency matrix

    Returns:
        tuple[bool, list[str]]: (True, ["valid"]) or (False, [errors])
    """
    errors = []

    # Check matrix is not empty
    if not matrix:
        return False, ["File is empty"]

    n = len(matrix)

    # Check all rows have same length as n
    for i, row in enumerate(matrix):
        if len(row) != n:
            errors.append(f"Row {i} has {len(row)} elements, expected {n}")
    
    if errors:
        return False, errors

    # Check values
    for i in range(n):
        for j in range(n):
            val = matrix[i][j]
            if val < 0:
                errors.append(f"Negative distance at ({i},{j})")
            if i == j and val != 0:
                errors.append(f"Diagonal at ({i},{j}) is not zero")

    if errors:
        return False, errors
    return True, ["Distance matrix is valid"]

def check_orders(orders: List[Dict[str, object]]) -> Tuple[bool, List[str]]:
    """
    Check that orders are valid

    Checks:
    - Orders list is not empty
    - Each order has required keys
    - nb_locations matches length of locations_list
    - No duplicate locations
    """
    errors: List[str] = []

    if not orders:
        return False, ["No orders loaded"]

    for idx, order in enumerate(orders):
        # Required keys
        required_keys = {"id", "volume", "nb_locations", "locations_list", "locations_set"}
        missing = required_keys - order.keys()
        if missing:
            errors.append(f"Order {order.get('id', idx)}: missing keys {missing}")
            continue

        # Basic consistency checks
        if len(order["locations_list"]) != order["nb_locations"]:
            errors.append(f"Order {order['id']}: nb_locations mismatch")

        if len(order["locations_list"]) != len(order["locations_set"]):
            errors.append(f"Order {order['id']}: duplicate locations detected")

    if not errors:
        return True, ["Orders are valid"]
    else:
        return False, errors
        
def check_constraints(constraints: List[int]) -> Tuple[bool, List[str]]:
    """
    Check that the file constraints is valid
    """

    errors = []

    if not constraints:
        errors.append("File is empty")
        return False, errors

    if not isinstance(constraints[0], int):
        errors.append("Maximum number of orders that a picker can do must be an integer")
    if not isinstance(constraints[1], int):
        errors.append("Maximum volume that a picker can carry must be an integer")
    
    if len(errors) != 0:
        return False, errors
    else:
        return True, ["Constraints are valid"]

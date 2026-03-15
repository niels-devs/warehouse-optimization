from collections import defaultdict
from typing import List, Dict, Set
from math import ceil
import numpy as np

def get_locations_and_orders_counts(adj_matrix: np.ndarray, orders: List[Dict[str, object]]):
    """
    This function returns the number of warehouse locations and the
    number of orders in the instance.

    Args:
        adj_matrix (list[list[float]]): Adjacency matrix representing
            the travel distances between warehouse locations.
        orders (List[Dict[str, object]]): List of orders, where each
            order contains information such as locations to visit,
            volume, and order ID.

    Returns:
        Tuple[int, int]:
            - Number of locations in the warehouse.
            - Number of orders in the instance.
    """
    nb_locations = len(adj_matrix)
    nb_orders = len(orders)

    return nb_locations, nb_orders

def max_pickers_bounds(orders, nb_orders, max_nb_orders, max_vol, vol):
    """
    Returns a lower and an upper bound on the number of pickers.

    Lower bound respects:
    - the capacity constraint on the number of orders
    - the capacity constraint on volume

    Upper bound is:
        - worst case: one picker per order
    """

    min_pickers_constr_max_nb_orders = ceil(nb_orders/max_nb_orders)

    total_vol = sum(vol)

    min_pickers_constr_max_vol = ceil(total_vol/max_vol)

    lower_bound = max(min_pickers_constr_max_nb_orders, min_pickers_constr_max_vol)

    upper_bound = nb_orders

    return lower_bound, upper_bound

def is_loc_in_order(nb_locations: int, orders: List[Dict[str, object]]):
    """
    Build a dictionary data[location, order] = 1 if location is visited in order, 0 otherwise
    """
    if_loc_in_ord = {}
    for loc in range(nb_locations):
        for order_number in range(len(orders)):
            visited = orders[order_number]["locations_set"]
            if_loc_in_ord[loc, order_number] = 1 if loc in visited else 0
    return if_loc_in_ord

def common_elements(if_loc_in_ord, nb_orders, nb_locations):
    """
    Compute the number of common locations between each pair of orders.

    For every pair of orders (o1, o2), the function counts how many
    warehouse locations appear in both orders. The result is stored in
    a dictionary where each key is a pair of orders and the value is
    the number of shared locations.

    Args:
        if_loc_in_ord : Binary matrix indicating whether
            location `loc` is included in order `o`.
            Value is 1 if the location is part of the order, 0 otherwise.
        nb_orders (int): Total number of orders.
        nb_locations (int): Total number of warehouse locations.

    Returns:
        Dict[Tuple[int, int], int]:
            Dictionary mapping each pair of orders (o1, o2) to the
            number of common locations they share.
    """
    result = defaultdict(int)
    for o1 in range(nb_orders):
        for o2 in range(o1 + 1, nb_orders):
            for loc in range(nb_locations):
                if if_loc_in_ord[loc, o1] == 1 and if_loc_in_ord[loc, o2] == 1:
                    result[o1, o2] += 1
                    result[o2, o1] += 1   # add symmetric value

    return result

def get_picker_locations_from_ifloc(
    batches: Dict[int, List[int]],
    if_loc_in_ord: Dict[tuple, int],
    nb_locations: int
) -> Dict[int, List[int]]:
    """
    Convert batches of orders into actual locations for each picker.

    Args:
        batches: dictionary {picker_id: list of orders}
        if_loc_in_ord: dictionary {(location, order): 1 if order requires location else 0}
        nb_locations: total number of locations

    Returns:
        picker_locations: dictionary {picker_id: sorted list of locations}
                          Only pickers with at least one location are returned.
    """
    picker_locations = {}

    for picker, orders in batches.items():
        locations = set()

        for loc in range(nb_locations):
            # Check if any of this picker's orders require this location
            if any(if_loc_in_ord.get((loc, order_number), 0) == 1 for order_number in orders):
                locations.add(loc)

        # Only add pickers that actually have locations
        if locations:
            picker_locations[picker] = sorted(locations)

    return picker_locations

def evaluate_batches(batches: Dict[int, list], common_locations) -> int:
    """
    Compute the total number of shared locations between orders in the same batch.

    Args:
        batches (Dict[int, list]): Dictionary mapping batch_id → list of order indices
        common_locations (2D array/matrix): common_locations[o1, o2] = number of shared locations

    Returns:
        int: total score of the batching solution
    """
    score = 0

    for batch in batches.values():
        for i in range(len(batch)):
            for j in range(i+1, len(batch)):
                o1 = batch[i]
                o2 = batch[j]
                score += common_locations[o1, o2]

    return score
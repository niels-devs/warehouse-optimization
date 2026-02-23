from collections import defaultdict
from typing import List, Dict, Set
from math import ceil

def get_locations_and_orders_counts(adj_matrix, orders: List[Dict[str, object]]):
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
    resultat = defaultdict(int)
    for order_number in range(nb_orders):
        for order_number2 in range(order_number + 1, nb_orders):
            for loc in range(nb_locations):
                if if_loc_in_ord[loc, order_number] == 1 and if_loc_in_ord[loc, order_number2] == 1:
                    resultat[order_number, order_number2] += 1
    return resultat

def get_picker_locations_from_ifloc(batches: Dict[int, List[int]], if_loc_in_ord: Dict[tuple, int], nb_locations: int):
    picker_locations = {}

    for picker, orders in batches.items():
        locations = set()

        for loc in range(nb_locations):
            for order_number in orders:
                if if_loc_in_ord.get((loc, order_number), 0) == 1:
                    locations.add(loc)
                    break

        picker_locations[picker] = sorted(locations)

    return picker_locations
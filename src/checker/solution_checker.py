from typing import List, Dict, Tuple, Any

def check_batching_solution(batches: Dict[int, List[int]], data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check that a batching solution is valid.

    Args:
        batches (Dict): {picker: list of assigned orders}
        vol (List[int]): volumes of each order
        max_nb_orders (int): maximum orders a picker can handle
        max_vol (int): maximum volume a picker can carry

    Returns:
        tuple[bool, List[str]]: (True, ["Valid"]) or (False, [errors])
    """
    order_volumes = data["order_volumes"]
    max_nb_orders = data["max_nb_orders"] 
    max_vol = data["max_vol"]

    errors = []
    assigned_orders = set()

    for p, orders in batches.items():
        # Check max orders per picker
        if len(orders) > max_nb_orders:
            errors.append(f"Picker {p} assigned {len(orders)} orders > max {max_nb_orders}")

        # Check max volume per picker
        total_vol = sum(order_volumes[o] for o in orders)
        if total_vol > max_vol:
            errors.append(f"Picker {p} carries volume {total_vol} > max {max_vol}")

        # Check each order assigned only once
        for o in orders:
            if o in assigned_orders:
                errors.append(f"Order {o} assigned to multiple pickers")
            assigned_orders.add(o)
        
    if not errors:
        return True, ["Valid solution"]
    else: 
        return False, errors

def check_picking_solution(travel: Dict[int, List[Tuple[int, int]]], num_locations: int) -> Tuple[bool, List[str]]:
    """
    Check that a picking solution is valid.

    Args:
        travel: arcs taken by each picker
        nb_locations: number of locations

    Returns:
        tuple[bool, List[str]]: (True, ["Valid"]) or (False, [errors])
    """
    errors = []
    last_location = num_locations - 1

    for p, arcs in travel.items():
        if not arcs:
            continue
        if sum(1 for arc in arcs if arc[0] == 0) != 1:
            errors.append(f"picker {p} must depart exactly once from 0")
        if sum(1 for arc in arcs if arc[1] == last_location) != 1:
            errors.append(f"picker {p} must arrive exactly once to {last_location}")
    
        # Check that there are no subtours
        next_loc = {i:j for i,j in arcs}
        current = 0
        visited = set([current])

        while current in next_loc:
            current = next_loc[current]
            if current in visited:
                errors.append(f"picker {p} has a subtour at location {current}")
                break
            visited.add(current)

        # Check that all arcs are used
        if len(visited) - 1 != len(arcs):
            errors.append(f"picker {p} has disconnected arcs (subtour or missing link)")

    if not errors:
        return True, ["Solution is valid"]
    return False, errors
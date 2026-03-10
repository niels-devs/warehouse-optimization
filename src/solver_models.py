import pulp as pl
from typing import List, Dict, Set

def model_batching(data, time_limit=300) -> Dict:
    """
    Solve the order batching problem using a mixed-integer linear programming model.

    The model assigns orders to pickers (batches) while maximizing the number of
    common picking locations between orders in the same batch. The assignment
    must satisfy capacity constraints on both the number of orders and the
    total volume handled by each picker.

    Decision variables:
        y[p,o] = 1 if order o is assigned to picker p, 0 otherwise
        z[p,o,o2] = 1 if orders o and o2 are assigned to the same picker p

    Objective:
        Maximize the total number of shared locations between orders assigned
        to the same picker.

    Constraints:
        - Each order must be assigned to exactly one picker.
        - Each picker can handle at most `max_nb_orders` orders.
        - The total volume assigned to a picker cannot exceed `max_vol`.
        - Linking constraints ensure that z[p,o,o2] = 1 only if both orders
          o and o2 are assigned to picker p.

    Args:
        data (dict): Dictionary containing the instance data with the following keys:
            - "order_volumes": list[int], volume of each order
            - "num_orders": int, total number of orders
            - "max_pickers": int, maximum number of pickers (batches)
            - "max_nb_orders": int, maximum number of orders per picker
            - "max_vol": int, maximum volume capacity per picker
            - "common_locations": 2D matrix where a[o,o2] is the number of
              common picking locations between orders o and o2

        time_limit (int, optional): Maximum solving time in seconds.
            Default is 300 seconds.

    Returns:
        Dict[int, List[int]]:
            Dictionary where keys are picker IDs and values are the list of
            orders assigned to that picker. Empty batches are removed.
    """
     
    vol = data["order_volumes"]
    nb_orders = data["num_orders"]
    max_pickers = data["max_pickers"]
    max_nb_orders = data["max_nb_orders"]
    max_vol = data["max_vol"]
    a = data["common_locations"]

    # Maximization problem
    model = pl.LpProblem("model_batching", pl.LpMaximize)

    # Decision variables
    y = pl.LpVariable.dicts(
        "y",
        [(p,o) for p in range(max_pickers) for o in range(nb_orders)],
        cat="Binary")
    z = pl.LpVariable.dicts(
        "z", 
        [(p,o,o2) for p in range(max_pickers) for o in range(nb_orders) for o2 in range(o+1, nb_orders)], 
        cat="Binary"
    )

    # Objective function
    model += pl.lpSum(z[p,o,o2] * a[o,o2] for p in range(max_pickers) for o in range(nb_orders) for o2 in range(o+1, nb_orders))

    # Constraints
    # Each order must be done exactly once
    for o in range(nb_orders):
        model += pl.lpSum(y[p,o] for p in range(max_pickers)) == 1

    # Each picker constraints: max orders and max volume
    for p in range(max_pickers):
        model += pl.lpSum(y[p,o] for o in range(nb_orders)) <= max_nb_orders
        model += pl.lpSum(y[p,o] * vol[o] for o in range(nb_orders)) <= max_vol

    # Linking z and y: z[p,o,o2] = y[p,o] * y[p,o2]
    for p in range(max_pickers):
        for o in range(nb_orders):
            for o2 in range(o+1, nb_orders):
                model += z[p,o,o2] <= y[p,o]
                model += z[p,o,o2] <= y[p,o2]
                model += z[p,o,o2] >= y[p,o] + y[p,o2] - 1

    # Set a time limit of 5 minutes
    solver = pl.PULP_CBC_CMD(timeLimit=time_limit, msg=True)

    # Solve the model
    status = model.solve(solver)
    print("Solver status:", pl.LpStatus[status])

    # Extract solution
    batches = {
        p: [o for o in range(nb_orders) if (y[p,o].varValue or 0) > 0.5]
        for p in range(max_pickers)
    }

    # Remove empty batches
    batches = {p: orders for p, orders in batches.items() if orders}

    return batches

def model_picking(data, time_limit=300):
    """
    Solve the picker routing problem using a mixed-integer linear programming model.

    For each picker, the model determines the optimal route through the set of
    assigned picking locations. The objective is to minimize the total travel
    distance based on the warehouse adjacency matrix.

    Decision variables:
        x[i,j,p] = 1 if picker p travels from location i to location j
        u[i,p] = order of visit of location i by picker p (MTZ formulation)

    Objective:
        Minimize the total travel distance of all pickers.

    Constraints:
        - Each location (except the starting point) must be entered exactly once.
        - Each location (except the ending point) must be left exactly once.
        - No arc can leave the final location.
        - Miller–Tucker–Zemlin (MTZ) constraints eliminate sub-tours.
        - The starting location is fixed at position 0 and the ending location
          at the last position in the route.

    Args:
        data (dict): Dictionary containing the instance data with the following keys:
            - "adj_matrix": 2D matrix representing travel distances between locations
            - "pickers_locations": dict[int, list[int]] mapping each picker to
              the list of locations they must visit

        time_limit (int, optional): Maximum solving time in seconds.
            Default is 300 seconds.

    Returns:
        Tuple[Dict[int, List[Tuple[int, int]]], float]:
            - Dictionary where each key is a picker ID and the value is the list
              of arcs (i, j) traveled by that picker.
            - Objective value corresponding to the total travel distance.
    """
    
    adj_matrix = data["adj_matrix"]

    pickers_locations = data["pickers_locations"]

    # minimization problem creation
    model = pl.LpProblem("modele_picking", pl.LpMinimize)

    ## Variables

    # Decision variable indicating whether picker p travels from location i to location j
    x = {}
    for p, locs in pickers_locations.items():  # seulement les pickers avec des locations
        for i in locs:
            for j in locs:
                if i != j:
                    x[(i,j,p)] = pl.LpVariable(f"x_{i}_{j}_{p}", cat="Binary")

    # Continuous variables: MTZ for sub-tour elimination
    u = {}
    for p, locs in pickers_locations.items():
        for i in locs:
            u[(i,p)] = pl.LpVariable(f"u_{i}_{p}", lowBound=0, upBound=len(locs)-1, cat="Integer")

    ## Objective function
    model += pl.lpSum(
        adj_matrix[i][j] * x[i,j,p]
        for (i,j,p) in x
    )

    ## Constraints

    for p, locs in pickers_locations.items():
        start = locs[0]
        end = locs[-1]

        # picker p must enter location j from exactly one other location i within their assigned batch
        for j in locs:
            if j != start:
                model += pl.lpSum(x[i,j,p] for i in locs if i != j) == 1

        # Each location (except end) must be left exactly once
        for i in locs:
            if i != end:
                model += pl.lpSum(x[i,j,p] for j in locs if i != j) == 1

        # No arcs leaving the arrival point
        for j in locs:
            if end != j:
                model += x[end,j,p] == 0

        # Sub-tour elimination (Miller-Tucker-Zemlin)
        for i in locs:
            for j in locs:
                if i != j and j != start and i != end:
                    model += u[i,p] - u[j,p] + x[i,j,p] * len(locs) <= len(locs)-1

        # Fix start and end in u variables
        model += u[start,p] == 0
        model += u[end,p] == len(locs)-1

    # Set a time limit of 5 minutes
    solver = pl.PULP_CBC_CMD(timeLimit=time_limit, msg=True)

    # Solve the model
    status = model.solve(solver)
    print("Solver status:", pl.LpStatus[status])

    objective = pl.value(model.objective)

    sol={}
    solution = {}
    for p, loc in pickers_locations.items():
        for i in pickers_locations[p]:
            sol[i,p] = u[i,p].varValue
            for j in pickers_locations[p]:
                if i != j:
                    solution[i,j,p] = x[i,j,p].varValue
    travel = {
        p: [(i, j)
            for i in locs
            for j in locs
            if i != j and solution.get((i,j,p), 0) > 0.5]
        for p, locs in pickers_locations.items()
        if any(solution.get((i,j,p), 0) > 0.5 for i in locs for j in locs if i != j)
    }
    """u_values = {
    p: [sol[i,p] for i in locations_pickers[p]]
    for p in range(max_pickers) if locations_pickers[p]
    }"""

    return travel, objective
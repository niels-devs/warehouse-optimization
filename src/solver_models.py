import pulp as pl
from typing import List, Dict, Set

def model_batching(data) -> Dict:
    vol = data["order_volumes"]

    nb_orders = data["num_orders"]

    max_pickers = data["max_pickers"]
    max_nb_orders = data["max_nb_orders"]
    max_vol = data["max_vol"]

    a = data["common_locations"]

    # maximization problem creation
    model = pl.LpProblem("model_batching", pl.LpMaximize)

    ## Variables

    # decison variable that is equal to 1 if the picker p handles the order o
    y = pl.LpVariable.dicts("y", [(p,o) for p in range(max_pickers) for o in range(nb_orders)], cat="Binary")

    # Decision variable equal to the product of y_po and y_po'
    z = pl.LpVariable.dicts("z", [(p,o,o2) for p in range(max_pickers) for o in range(nb_orders) for o2 in range(nb_orders) if o<o2], cat="Binary")

    ## Objective function
    model += sum(z[p,o,o2] * a[o,o2] for p in range(max_pickers) for o in range(nb_orders) for o2 in range(nb_orders) if o<o2)

    ## Constraints

    # a minimum of nb_orders must be done
    model += sum(y[p,o] for p in range(max_pickers) for o in range(nb_orders)) >= nb_orders

    # An order can only be done once
    for o in range(nb_orders):
        model += sum(y[p,o] for p in range(max_pickers)) == 1

    # A picker can't do more than max_nb_ord
    for p in range(max_pickers):
        model += sum(y[p,o] for o in range(nb_orders)) <= max_nb_orders

    # A picker can't carry more than max_vol
    for p in range(max_pickers):
        model += sum(y[p,o] * vol[o] for o in range(nb_orders)) <= max_vol

    # z[p, o, o2] is the product between y[p, o] and y[p, o2]
    for p in range(max_pickers):
        for o in range(nb_orders):
            for o2 in range(o+1, nb_orders):
                model += z[p,o,o2] <= y[p,o]
                model += z[p,o,o2] <= y[p,o2]
                model += z[p,o,o2] >= y[p,o] + y[p,o2] - 1
    
    status = model.solve()
    print("Solver status:", pl.LpStatus[status])

    solution = {}
    for p in range(max_pickers):
        for o in range(nb_orders):
            solution[p,o] = y[p,o].varValue or 0

    batches = {
        p : [o for o in range(nb_orders) if (solution[p,o] or 0) > 0.5]
        for p in range(max_pickers)
    }

   # Remove batches that do not contain any orders
    batches = {p: orders for p, orders in batches.items() if orders}

    return batches

def model_picking(data):
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

    model.solve()

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
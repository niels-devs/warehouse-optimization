from typing import Dict, Any, List
import copy
import random
import time

from utils import(
    evaluate_batches
)

def greedy_order_batching(data: Dict[str, Any]) -> Dict[int, List[int]]:
    """
    Greedy order batching algorithm.

    Builds batches iteratively:
    1. Select a seed order that shares the most locations with remaining orders.
    2. Greedily add compatible orders while respecting capacity constraints.

    Returns:
        Dictionary where each key is a batch ID and value is the list of order indices in that batch.
    """

    # Extract input data
    num_orders = data["num_orders"]
    common_locations = data["common_locations"]   # matrix: shared locations between orders
    volumes = data["order_volumes"]               # volume of each order
    max_orders = data["max_nb_orders"]            # max orders per batch
    max_vol = data["max_vol"]                     # max volume per batch

    # Orders that still need to be assigned to a batch
    unassigned = list(range(num_orders))

    # Dictionary to store final batches: batch_id → list of orders
    batches = {}
    batch_id = 0  # Counter to assign batch IDs

    # Continue until all orders are assigned
    while unassigned:

        # 1. Choose a seed order for the new batch
        # Select the order that shares the most locations
        # with the remaining unassigned orders
        # --------------------------------------------------
        first = max(
            unassigned,
            key=lambda i: sum(common_locations[i, j] for j in unassigned)
        )

        # Initialize the new batch with the seed order
        unassigned.remove(first)
        batch = [first]
        batch_volume = volumes[first]

        # --------------------------------------------------
        # 2. Greedily grow the batch
        # Try to add the most compatible orders while respecting
        # the maximum number of orders and volume constraints
        # --------------------------------------------------
        while True:

            best_candidate = None  # Candidate order to add
            best_score = -1        # Compatibility score of the candidate

            for candidate in unassigned:

                # Check capacity constraints
                if len(batch) >= max_orders:
                    continue
                if batch_volume + volumes[candidate] > max_vol:
                    continue

                # Compute compatibility score:
                # total number of shared locations with orders already in the batch
                score = sum(common_locations[candidate, b] for b in batch)

                # Keep the candidate with the highest score
                if score > best_score:
                    best_score = score
                    best_candidate = candidate

            # Stop growing the batch if no suitable candidate is found
            if best_candidate is None or best_score == 0:
                break

            # Add the best candidate to the batch
            batch.append(best_candidate)
            batch_volume += volumes[best_candidate]
            unassigned.remove(best_candidate)

        # Save the completed batch in the dictionary
        batches[batch_id] = batch
        batch_id += 1

    return batches

def local_search_swap(
    batches: Dict[int, List[int]],
    data: Dict[str, Any],
    time_limit: float = 300.0
) -> Dict[int, List[int]]:
    """
    Local Search metaheuristic for Order Batching using swap moves.

    This function improves an initial batching solution by iteratively swapping
    two orders between two batches if the swap increases the total score.
    The objective is to maximize the number of shared locations within batches.
    The search stops when the specified time limit is reached.

    Args:
        batches (Dict[int, List[int]]): Initial solution mapping batch_id → list of order indices.
        common_locations (2D array/matrix): common_locations[o1, o2] = number of shared locations.
        max_orders (int): Maximum number of orders allowed in a batch.
        max_volumes (List[int]): Maximum allowed total volume for each batch.
        volumes (List[int]): List of volumes for each order.
        time_limit (float, optional): Maximum allowed runtime in seconds (default: 300).

    Returns:
        Dict[int, List[int]]: Improved batching solution mapping batch_id → list of order indices.
    """

    common_locations = data["common_locations"]
    max_volume = data["max_vol"]
    volumes = data["order_volumes"]

    current_solution = copy.deepcopy(batches)
    best_solution = copy.deepcopy(current_solution)
    best_score = evaluate_batches(best_solution, common_locations)

    batch_ids = list(current_solution.keys())
    start_time = time.time()

    while time.time() - start_time < time_limit:

        # Randomly pick two distinct batches
        if len(batch_ids) < 2:
            break  # not enough batches to swap
        b1, b2 = random.sample(batch_ids, 2)

        if not current_solution[b1] or not current_solution[b2]:
            continue

        # Randomly pick one order from each batch
        o1 = random.choice(current_solution[b1])
        o2 = random.choice(current_solution[b2])

        # Check volume constraints after swap
        vol_b1 = sum(volumes[o] for o in current_solution[b1]) - volumes[o1] + volumes[o2]
        vol_b2 = sum(volumes[o] for o in current_solution[b2]) - volumes[o2] + volumes[o1]

        if vol_b1 > max_volume or vol_b2 > max_volume:
            continue  # swap not feasible

        # Perform the swap
        new_solution = copy.deepcopy(current_solution)
        new_solution[b1].remove(o1)
        new_solution[b2].remove(o2)
        new_solution[b1].append(o2)
        new_solution[b2].append(o1)

        # Evaluate new solution
        new_score = evaluate_batches(new_solution, common_locations)

        # Accept only if it improves the objective
        if new_score > best_score:
            best_solution = new_solution
            best_score = new_score
            current_solution = new_solution

    return best_solution
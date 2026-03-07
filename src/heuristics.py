from typing import Any, List, Dict

from typing import Dict, Any, List

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
# Order Picking and Batching Optimization

## 1. Project Overview

This project addresses the optimization of order picking and batching in a warehouse environment.  
Each order consists of a set of storage locations to visit and an associated volume.  
The objective is to assign orders to pickers while respecting capacity constraints, aiming to minimize the pickers total distance.

Key objectives:
- Respect maximum number of orders per picker.
- Respect maximum volume per picker.
- Allow flexible batching strategies.
- Keep solutions aligned with warehouse layout and locations.

---

## 2. Data Structure

All information is stored in a single Python dictionary called `data`.  
This dictionary contains all relevant information for order batching and picker assignment optimization, including orders, warehouse layout, and operational constraints.

- **`data` dictionary** contains:

```python
data = {
    "adj_matrix": adj_matrix,           # warehouse adjacency matrix
    "loc_in_order": loc_in_order,       # indicates if a location is part of a given order
    "num_locations": num_locations,     # total number of locations
    "num_orders": num_orders,           # total number of orders
    "min_pickers": min_pickers,         # minimum number of available pickers
    "max_pickers": max_pickers,         # maximum number of available pickers
    "max_nb_orders": max_nb_orders,     # maximum number of orders per picker
    "max_vol": max_vol,                 # maximum volume a picker can carry
    "common_locations": common_locations # number of locations shared between two orders

---

## 3. Preprocessing Steps

Before running the optimization model, the following preprocessing is performed:

1. Compute the number of orders (`nb_orders`) and number of locations (`nb_locations`).
2. Build the binary assignment matrix `a_io` (`if_loc_in_order` in code).
3. Compute **lower and upper bounds** for the number of pickers:
   - **Lower bound**: minimum number of pickers required based solely on capacity constraints (number of orders and volume).
   - **Upper bound**: worst-case scenario assuming minimal work per picker.
4. Extract order volumes (`vol`) for constraint calculations.
5. Compute common elements between orders (number of shared locations) for batching heuristics.

---

## 4. Project Structure

```text
.
├── main.py              # Entry point and test functions
├── utils.py             # Preprocessing and helper functions
├── solver_models.py     # Optimization model(s)
├── data_loader.py       # Functions to load input data
├── data/                # Input data files (orders, adjacency matrix, constraints)
└── README.md            # This file

```
---

## 5. Running the Project

To run the picking test:

```bash
python main.py
Tests are organized in main() as a dictionary:

tests = {
    "picking": test_picking,
    "batching": test_batching
    }
Call a test by key:

tests["picking"]()
Once ready, you can uncomment the model call in main():

# sm.model_picking(data)
```

---

## 6. Notes and Assumptions

- The number of pickers is **bounded** (minimum and maximum) but not fixed.
- Lower bounds are computed **solely from capacity constraints** (number of orders and total volume).
- Upper bounds are calculated as a worst-case scenario, assuming minimal work per picker.
- Data structures follow the **mathematical model**:
  - `a_io[i, o]` matches \(a_{i,o}\) in the formulation.
  - `if_loc_in_order` alias is provided for clarity for non-RO users.
- Preprocessing ensures all constraints are easily applied by the solver.
- The order of visits within batches is **flexible**, to be optimized by the model.

---

## 7. Future Work

- Integrate routing optimization for each picker's path.
- Implement more advanced batching heuristics.
- Extend the model for dynamic orders or real-time picking scenarios.
- Improve computation of lower and upper bounds for pickers using smarter reasoning beyond simple worst-case estimates.

---

## 8. References / Developer Notes

- Variables and functions align with **mathematical notation** wherever possible.
- Code is structured to allow easy testing and modification:
  - `utils.py` → preprocessing and helper functions
  - `data_loader.py` → loading input data
  - `solver_models.py` → contains optimization models
  - `main.py` → testing, assembling data, calling models
- Typing is added for clarity (`List`, `Dict`, `int`, etc.) and ensures consistency in development.

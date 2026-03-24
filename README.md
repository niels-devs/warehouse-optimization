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
```
---

## 3. Project Structure

The project is organized as follows, showing all source code, data, and supporting files for the order batching and picker assignment optimization.

```text
.
├── src                           # Project source code
│   ├── main.py                   # Main entry point and test functions
│   ├── data_loader.py            # Functions to load and prepare input data
│   ├── heuristics.py             # Heuristic algorithms for batching
│   ├── solver_models.py          # Optimization models
│   ├── checker                   # Folder to validate instances and solutions
│   │   ├── instance_checker.py   # Checks input files (orders, matrix, constraints)
│   │   └── solution_checker.py   # Checks that generated solutions meet all constraints
│   ├── toy_data                  # Small dataset for quick testing
│   │   ├── constraints.txt       # Constraints on pickers: max volumes and max number of orders
│   │   ├── matrix.txt            # Adjacency matrix representing the warehouse
│   │   └── orders.txt            # Definition of orders (locations and volumes)
│   └── utils.py                  # Utility and preprocessing functions
├── .gitignore                    # Files/folders ignored by Git
├── README.md                     # Project documentation
└── warehouse-optimization.pdf    # Additional documentation in PDF

```
---

## 4. Running the Project

To run the tests, open a terminal in the project directory and run:

```bash
python main.py
```

You will see the interactive menu:

```bash
===== BATCHING & PICKING MENU =====
1: Main Model
2: Model Batching + Model Picking
3: Greedy Batching + Model Picking
0: Exit
```
Enter the number corresponding to the test you want to run:
```bash
Option	Strategy	Description
1	Main Model	Runs the full main model and prints objective, travel distance, and execution time.
2	Model Batching + Model Picking	Performs model-based batching then runs picking.
3	Greedy Batching + Model Picking	Performs greedy batching then runs picking.
0	Exit	Exits the program.
```
After selecting a test, results will be displayed in the terminal and logged via Python’s logging module.

Example output for the Main Model:
```bash
--- Running Main Model ---
2026-03-24 19:37:40,342 | INFO | __main__ | === MAIN MODEL ===
2026-03-24 19:37:40,342 | INFO | __main__ | travel={0: [(0, 6), (1, 8), (2, 9), (3, 1), (5, 3), (6, 5), (8, 2)],
1: [(0, 7), (1, 4), (2, 1), (3, 2), (4, 6), (6, 9), (7, 8), (8, 3)], 3: [(0, 4), (1, 8), (4, 5), (5, 6), (6, 1), (8, 9)]}
2026-03-24 19:37:40,342 | INFO | __main__ | objective=524.0
2026-03-24 19:37:40,342 | INFO | __main__ | time=68.57191460000467 seconds
```
For Model Batching + Model Picking or Greedy Batching + Model Picking, the output may look like:
```bash
--- Running Model Batching + Model Picking ---
2026-03-24 19:34:15,696 | INFO | __main__ | === MODEL BATCHING ===
2026-03-24 19:34:15,697 | INFO | __main__ | travel={1: [(0, 6), (1, 8), (2, 9), (3, 1), (5, 3), (6, 5), (8, 2)],
3: [(0, 4), (1, 8), (4, 5), (5, 6), (6, 1), (8, 9)], 5: [(0, 7), (1, 4), (2, 1), (3, 2), (4, 6), (6, 9), (7, 8), (8, 3)]}
2026-03-24 19:34:15,697 | INFO | __main__ | objective=524.0
```
Use option 0 in the menu to exit the program.

## 5. Notes and Assumptions

- The number of pickers is **bounded** (minimum and maximum) but not fixed.
- Lower bounds are computed **solely from capacity constraints** (number of orders and total volume).
- Upper bounds are calculated as a worst-case scenario, assuming minimal work per picker.
- Data structures follow the **mathematical model**:
  - `a_io[i, o]` matches \(a_{i,o}\) in the formulation.
  - `loc_in_order` alias is provided for clarity for non-RO users.
- Preprocessing ensures all constraints are easily applied by the solver.
- The order of visits within batches is **flexible**, to be optimized by the model.


---

## 6. Future Work

- Implement more advanced picking heuristics.
- Extend the model for dynamic orders or real-time picking scenarios.
- Improve computation of lower and upper bounds for pickers using smarter reasoning beyond simple worst-case estimates.

---

## 7. References / Developer Notes

- Variables and functions align with **mathematical notation** wherever possible.
- Code is structured to allow easy testing and modification:
  - `utils.py` → preprocessing and helper functions
  - `data_loader.py` → loading input data
  - `solver_models.py` → contains optimization models
  - `main.py` → testing
- Typing is added for clarity (`List`, `Dict`, `int`, etc.) and ensures consistency in development.

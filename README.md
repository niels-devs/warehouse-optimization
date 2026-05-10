# Order Batching and Picking Optimization

## 1. Project Overview
This project provides a comprehensive optimization framework for the **Joint Order Batching and Picker Routing Problem (JOBPRP)**. In high-volume fulfillment centers, travel time accounts for over 50% of total picking time; this repository implements a tiered approach to minimize total travel distance while strictly adhering to picker capacity and warehouse topological constraints.

By combining exact mathematical modeling with high-speed local search heuristics, the framework enables both theoretical benchmarking and real-time operational deployment.

> [!IMPORTANT]
> **Technical Documentation:** For an in-depth analysis, please refer to the [**Warehouse_Optimization.pdf**](./Warehouse_Optimization.pdf) included in this repository. This document provides:
> * **Problem Formalization:** A detailed definition of the Joint Order Batching and Picker Routing Problem (JOBPRP).
> * **Data & Model Logic:** An explanation of the graph-based data structures and the exact Mixed-Integer Programming (MIP) formulations.
> * **Heuristic Suite:** A deep dive into the tiered logic of the Greedy, Swap/Move, and 2-Opt algorithms.
> * **Comprehensive Benchmarks:** A full breakdown of performance metrics and optimality gap analysis across various warehouse scales.

### Core Objectives
* **Integrated Global Optimization:**
    * **Main Model (Relax):** A Mixed-Integer Programming (MIP) formulation that solves batching and routing simultaneously to identify the global optimum or theoretical lower bound.
* **Decoupled Mathematical Modeling:**
    * **Order Batching Model:** Optimally groups orders into clusters based on location similarity and capacity limits.
    * **Picking Routing Model:** Computes the exact shortest path for pickers once batches are assigned.
* **Tiered Heuristic Pipeline:**
    A suite of algorithms designed for industrial-scale instances where exact solvers become computationally intractable:
    * **Greedy Initialization:** Rapidly generates a feasible baseline solution.
    * **Local Search (Swap & Move):** Iterative operators that redistribute orders between batches to improve cluster density.
    * **Routing Refinement (2-Opt):** Post-processing algorithm that "untangles" routes to minimize travel distance within each batch.
* **Operational Intelligence:**
    * **Capacity-Aware:** Ensures strict adherence to picker volume limits and maximum order counts.
    * **Graph-Based Navigation:** Respects warehouse layout constraints using an adjacency matrix, allowing for non-Euclidean pathfinding.

---

## 2. Data Structure

All information is stored in a single Python dictionary called `data`.  
This dictionary contains all relevant information for order batching and picker assignment optimization, including orders, warehouse layout, and operational constraints.

- **`data` dictionary** contains:

```python
data = {
    "adj_matrix": adj_matrix,            # warehouse adjacency matrix
    "loc_in_order": loc_in_order,        # indicates if a location is part of a given order
    "num_locations": num_locations,      # total number of locations
    "num_orders": num_orders,            # total number of orders
    "min_pickers": min_pickers,          # minimum number of available pickers
    "max_pickers": max_pickers,          # maximum number of available pickers
    "max_nb_orders": max_nb_orders,      # maximum number of orders per picker
    "max_vol": max_vol,                  # maximum volume a picker can carry
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
2026-03-24 19:34:15,696 | INFO | __main__ | === MODEL BATCHING + MODEL PICKING ===
2026-03-24 19:34:15,697 | INFO | __main__ | travel={1: [(0, 6), (1, 8), (2, 9), (3, 1), (5, 3), (6, 5), (8, 2)],
3: [(0, 4), (1, 8), (4, 5), (5, 6), (6, 1), (8, 9)], 5: [(0, 7), (1, 4), (2, 1), (3, 2), (4, 6), (6, 9), (7, 8), (8, 3)]}
2026-03-24 19:34:15,697 | INFO | __main__ | objective=524.0
```
Use option 0 in the menu to exit the program.

## 5. Results & Benchmarks

To evaluate the performance of the tiered heuristic pipeline against the exact mathematical model, experiments were conducted across two warehouse configurations of varying scales.

### 5.1 Performance Comparison
| Metric | Main Model (Relax) | Heuristic Pipeline |
| :--- | :--- | :--- |
| **Execution Time (Small Scale)** | ~15.4 seconds | **< 0.01 seconds** |
| **Execution Time (Large Scale)** | ~5,200+ seconds | **~0.03 seconds** |
| **Scalability** | Low (Exponential) | **High (Linear/Polynomial)** |

The performance divergence between the two approaches is rooted in their underlying complexity classes. The **Main Model (MIP)** addresses the JOBPRP as an **NP-Hard** problem; as the number of orders and warehouse locations increases, the solution space expands exponentially, leading to the "computational wall" observed in larger instances. In contrast, the **Heuristic Pipeline** is designed to achieve high-quality solutions within **Empirical Polynomial Time**. By utilizing a Greedy constructive phase followed by local search operators (**Swap**, **Move**, and **2-Opt**), the algorithm avoids an exhaustive search of the solution space. Instead, it navigates toward a local optimum through a finite number of iterative improvements, ensuring that execution time remains manageable—scaling near-linearly in practice—even as the operational volume grows.

### 5.2 Key Observations
* **The Scalability Wall:** The exact model provides the theoretical lower bound but becomes operationally unfeasible as the number of orders exceeds 30, due to the combinatorial explosion of the JOBPRP.
* **Real-time Viability:** The sub-second response time of the heuristic allows for dynamic re-batching, a critical requirement for modern, high-velocity fulfillment centers.v

## 6. Conclusion

This study successfully developed and evaluated a tiered optimization pipeline for the Joint Order Batching and Picker Routing Problem (JOBPRP). The results demonstrate a clear trade-off between mathematical rigor and computational efficiency: while exact formulations define the optimal baseline, they are practically restricted to small-scale instances due to exponential growth in processing time.

The implementation of a sequential heuristic strategy—utilizing **Swap** and **Move** operators alongside **2-Opt** refinement—effectively bridged this gap. The pipeline produced feasible, high-quality solutions in milliseconds, maintaining stability even as warehouse dimensions increased. Consequently, this research confirms that for high-volume logistics environments, a tiered heuristic approach provides the necessary responsiveness for real-time decision-making, offering a favorable trade-off between computational speed and absolute optimality..

---

## 7. Future Perspectives

While the current heuristic suite provides a robust framework for static batching, several avenues for future evolution remain:

* **Dynamic Order Integration:** Adapting the **Move** operator to handle "live" order arrivals, inserting new picks into active routes in real-time.
* **Congestion Awareness:** Modifying the adjacency matrix to include dynamic edge weights that penalize high picker density, avoiding physical bottlenecks in high-traffic aisles.

## 8. References / Developer Notes

- Variables and functions align with **mathematical notation** wherever possible.
- Code is structured to allow easy testing and modification:
  - `utils.py` → preprocessing and helper functions
  - `data_loader.py` → loading input data
  - `solver_models.py` → contains optimization models
  - `main.py` → testing
- Typing is added for clarity (`List`, `Dict`, `int`, etc.) and ensures consistency in development.

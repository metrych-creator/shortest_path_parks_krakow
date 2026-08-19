# Krakow Parks TSP Router

A Python application that solves the Travelling Salesperson Problem (TSP) for 78 parks in Kraków using Simulated Annealing (`python-tsp`) and geodesic distance calculations (`geopy`).

Example solution is attached in the `best_route.txt`.

The algorithm searches the shortest path between two points. 

```
Note that these calculations use direct (straight-line) geodesic distance rather than actual walking paths or road networks.
```

## Setup & Installation

### 1. Create a Virtual Environment

Open your terminal in the project directory and run:

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate

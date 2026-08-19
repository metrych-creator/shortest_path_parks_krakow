# Krakow Parks TSP Router

A Python application that solves the Travelling Salesperson Problem (TSP) for 78 parks in Kraków using Simulated Annealing (`python-tsp`) and geodesic distance calculations (`geopy`).

The algorithm searches the shortest path between two points. 

```
Note that these calculations use direct (straight-line) geodesic distance rather than actual walking paths or road networks.
```

## The results
The results contains:
- `[No. X]` - a number of the park in the list in [Odkrywca Krakowskich Parków](https://zzm.krakow.pl/images/bibliotekazzm/gryizabawy/OKP/POLSKI%20-%20Ksiazeczka%20-%20drukuj%20w%20a4%20dwustronnie%20z%20odbiciem%20krotkim%20bokiem.pdf)
- Name of the park
- Distance between current point and the next closest park

Example result:
```
1. [No. 1] Park im. Wisławy Szymborskiej -> 1.00 km to next stop
2. [No. 3] Park Jalu Kurka -> 0.82 km to next stop
3. [No. 20] Park Kleparski -> 0.87 km to next stop
4. [No. 22] Park przy ul. Łokietka -> 0.77 km to next stop
5. [No. 13] Park im. Stanisława Wyspiańskiego -> 0.43 km to next stop
```

## Setup & Installation

### 1. Create a Virtual Environment

Open your terminal in the project directory and run:

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Run application

Execute the main script to calculate the optimal route. The results will be displayed in your terminal and saved to `best_route.txt`:

```bash
python main.py
```

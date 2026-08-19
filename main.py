import numpy as np
from geopy.distance import geodesic
from geopy.point import Point
from python_tsp.heuristics import solve_tsp_simulated_annealing

# Import dictionary from external file
from locations import parks

# 1. Convert dictionary items to lists for indexing
locations = list(parks.items())
geodesic_points = [Point.from_string(coords) for coords, _ in locations]

# 2. Build the distance matrix
n = len(locations)
matrix = [[0.0] * n for _ in range(n)]

for i in range(n):
    for j in range(n):
        if i != j:
            matrix[i][j] = geodesic(
                geodesic_points[i], geodesic_points[j]
            ).km

# Convert list matrix to a NumPy array for python-tsp
distance_matrix = np.array(matrix)

# 3. Solve TSP using simulated annealing
path_indices, total_distance = solve_tsp_simulated_annealing(
    distance_matrix, alpha=0.995, max_processing_time=10
)

# 4. Display results with simplified output format
output_lines = [
    f"--- OPTIMAL TSP ROUTE (Estimated distance: {total_distance:.2f} km) ---\n"
]

num_stops = len(path_indices)

for step in range(num_stops):
    current_idx = path_indices[step]
    next_idx = path_indices[(step + 1) % num_stops]

    _, info = locations[current_idx]
    leg_distance = distance_matrix[current_idx][next_idx]

    line = f"{step + 1}. [No. {info['nr']}] {info['name']} -> {leg_distance:.2f} km to next stop"
    output_lines.append(line)

output_text = "\n".join(output_lines)
print(output_text)

filename = "best_route.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"\nRoute saved successfully to '{filename}'.")
import numpy as np
from geopy.distance import geodesic
from geopy.point import Point
from python_tsp.heuristics import solve_tsp_simulated_annealing

from locations import parks


def prepare_locations():
    locations = list(parks.items())
    geodesic_points = [Point.from_string(coords) for coords, _ in locations]
    return locations, geodesic_points


def build_distance_matrix(locations, geodesic_points):
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = geodesic(
                    geodesic_points[i], geodesic_points[j]
                ).km

    return np.array(matrix)


def solve_route(distance_matrix):
    return solve_tsp_simulated_annealing(
        distance_matrix, alpha=0.995, max_processing_time=10
    )


def find_park_index(locations, park_nr):
    for index, (_, info) in enumerate(locations):
        if info["nr"] == park_nr:
            return index
    return None


def rotate_path_to_start(path_indices, start_idx):
    path = list(path_indices)
    if len(path) > 1 and path[0] == path[-1]:
        path = path[:-1]
    position = path.index(start_idx)
    return path[position:] + path[:position]


def format_route(locations, distance_matrix, path_indices, total_distance):
    output_lines = []

    num_stops = len(path_indices)

    for step in range(num_stops):
        current_idx = path_indices[step]
        next_idx = path_indices[(step + 1) % num_stops]

        _, info = locations[current_idx]
        leg_distance = distance_matrix[current_idx][next_idx]

        output_lines.append(
            f"{step + 1}. {info['name']} (Nr. {info['nr']})"
            f"-> {leg_distance:.2f} km to next stop"
        )

    output_lines.append(
        f"\n--- Estymowana odległość: {total_distance:.2f} km ---\n"
    )

    return "\n".join(output_lines)


def save_route(output_text, filename="best_route.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output_text)
    return filename


def list_parks(locations, *, key, title):
    print(f"\n--- {title} ---")
    for _, info in sorted(locations, key=key):
        print(f"[No. {info['nr']}] {info['name']}")
    print(f"\nŁącznie: {len(locations)} parków")


def ask_start_park_nr(locations):
    valid_numbers = {info["nr"] for _, info in locations}
    min_nr = min(valid_numbers)
    max_nr = max(valid_numbers)

    while True:
        raw = input(
            f"\nPodaj numer parku startowego ({min_nr}-{max_nr}): "
        ).strip()
        try:
            park_nr = int(raw)
        except ValueError:
            print("To nie jest liczba. Spróbuj ponownie.")
            continue

        if park_nr not in valid_numbers:
            print(f"Nie ma parku o numerze {park_nr}. Spróbuj ponownie.")
            continue

        return park_nr


def compute_and_show_route(locations, distance_matrix, start_nr):
    start_idx = find_park_index(locations, start_nr)
    start_name = locations[start_idx][1]["name"]

    print(f"\nSzukam trasy od: [No. {start_nr}] {start_name}...")
    path_indices, total_distance = solve_route(distance_matrix)
    path_indices = rotate_path_to_start(path_indices, start_idx)

    output_text = format_route(
        locations, distance_matrix, path_indices, total_distance
    )
    print(output_text)
    filename = save_route(output_text)
    print(f"\nTrasa zapisana do '{filename}'.")


def print_menu():
    print("\n=== Trasa po parkach Krakowa ===")
    print("1. Oblicz trasę (wybierz park startowy)")
    print("2. Pokaż wszystkie parki (wg numeru)")
    print("3. Pokaż wszystkie parki (alfabetycznie)")
    print("0. Wyjście")


def main():
    print("Przygotowuję lokalizacje i macierz odległości...")
    locations, geodesic_points = prepare_locations()
    distance_matrix = build_distance_matrix(locations, geodesic_points)
    print("Gotowe.")

    while True:
        print_menu()
        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            start_nr = ask_start_park_nr(locations)
            compute_and_show_route(locations, distance_matrix, start_nr)
        elif choice == "2":
            list_parks(
                locations,
                key=lambda item: item[1]["nr"],
                title="Lista parków (wg numeru)",
            )
        elif choice == "3":
            list_parks(
                locations,
                key=lambda item: item[1]["name"].casefold(),
                title="Lista parków (alfabetycznie)",
            )
        elif choice == "0":
            print("Do widzenia.")
            break
        else:
            print("Nieznana opcja. Wybierz 1, 2, 3 albo 0.")


if __name__ == "__main__":
    main()

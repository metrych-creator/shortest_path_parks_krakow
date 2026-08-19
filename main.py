import html
import webbrowser
from pathlib import Path

import folium
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


def build_route_sidebar_html(
    locations, geodesic_points, distance_matrix, path_indices
):
    coords = [(point.latitude, point.longitude) for point in geodesic_points]
    num_stops = len(path_indices)
    total_distance = 0.0
    items = []

    for step in range(num_stops):
        current_idx = path_indices[step]
        next_idx = path_indices[(step + 1) % num_stops]
        _, info = locations[current_idx]
        lat, lon = coords[current_idx]
        leg_distance = float(distance_matrix[current_idx][next_idx])
        total_distance += leg_distance
        start_class = " start" if step == 0 else ""
        items.append(
            "<li class=\"park-item"
            f"{start_class}\" data-lat=\"{lat}\" data-lon=\"{lon}\">"
            f"<span class=\"step\">{step + 1}.</span>"
            f"<span class=\"details\">"
            f"<span class=\"name\">{html.escape(info['name'])}</span>"
            f"<span class=\"meta\">(Nr. {info['nr']}) · {leg_distance:.2f} km</span>"
            f"</span></li>"
        )

    items_html = "\n".join(items)
    return f"""
<style>
  html, body {{
    margin: 0;
    height: 100%;
    overflow: hidden;
  }}
  .folium-map {{
    position: absolute !important;
    top: 0;
    left: 0;
    right: 380px;
    width: auto !important;
    height: 100% !important;
  }}
  #route-sidebar {{
    position: fixed;
    top: 0;
    right: 0;
    width: 380px;
    height: 100%;
    overflow-y: auto;
    background: #0f172a;
    color: #e2e8f0;
    z-index: 10000;
    font-family: system-ui, -apple-system, sans-serif;
    box-shadow: -8px 0 24px rgba(15, 23, 42, 0.35);
  }}
  #route-sidebar h2 {{
    margin: 0;
    padding: 18px 18px 8px;
    font-size: 18px;
  }}
  #route-sidebar .total {{
    margin: 0 18px 12px;
    color: #93c5fd;
    font-size: 13px;
  }}
  #route-sidebar ol {{
    list-style: none;
    margin: 0;
    padding: 0 0 24px;
  }}
  #route-sidebar .park-item {{
    display: flex;
    gap: 8px;
    padding: 8px 18px;
    cursor: pointer;
    border-left: 3px solid transparent;
  }}
  #route-sidebar .park-item:hover {{
    background: #1e293b;
  }}
  #route-sidebar .park-item.start {{
    border-left-color: #22c55e;
    background: #14532d33;
  }}
  #route-sidebar .step {{
    min-width: 28px;
    color: #94a3b8;
    font-variant-numeric: tabular-nums;
  }}
  #route-sidebar .details {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}
  #route-sidebar .name {{
    font-size: 13px;
    line-height: 1.3;
  }}
  #route-sidebar .meta {{
    font-size: 12px;
    color: #94a3b8;
  }}
</style>
<aside id="route-sidebar">
  <h2>Trasa po parkach</h2>
  <p class="total">Estymowana odległość: {total_distance:.2f} km</p>
  <ol>
    {items_html}
  </ol>
</aside>
<script>
  document.querySelectorAll("#route-sidebar .park-item").forEach(function (item) {{
    item.addEventListener("click", function () {{
      const lat = parseFloat(this.dataset.lat);
      const lon = parseFloat(this.dataset.lon);
      const map = Object.values(window).find(function (value) {{
        return value && value.flyTo && value._container;
      }});
      if (map) {{
        map.flyTo([lat, lon], 15);
      }}
    }});
  }});
  setTimeout(function () {{
    const map = Object.values(window).find(function (value) {{
      return value && value.invalidateSize && value._container;
    }});
    if (map) {{
      map.invalidateSize();
    }}
  }}, 250);
</script>
"""


def draw_route_map(
    locations,
    geodesic_points,
    distance_matrix,
    path_indices,
    filename="route_map.html",
):
    coords = [(point.latitude, point.longitude) for point in geodesic_points]
    route_coords = [coords[index] for index in path_indices]
    route_coords.append(route_coords[0])

    route_map = folium.Map(
        location=route_coords[0],
        tiles="OpenStreetMap",
        width="100%",
        height="100%",
    )
    folium.PolyLine(
        route_coords,
        color="#2563eb",
        weight=4,
        opacity=0.85,
        tooltip="Najkrótsza trasa",
    ).add_to(route_map)

    for step, index in enumerate(path_indices):
        _, info = locations[index]
        is_start = step == 0
        folium.CircleMarker(
            location=coords[index],
            radius=8 if is_start else 5,
            color="#16a34a" if is_start else "#1d4ed8",
            fill=True,
            fill_opacity=0.9,
            popup=folium.Popup(
                f"{step + 1}. {info['name']} (Nr. {info['nr']})",
                max_width=300,
            ),
            tooltip=f"{step + 1}. {info['name']}",
        ).add_to(route_map)

    route_map.fit_bounds(route_coords)
    route_map.get_root().html.add_child(
        folium.Element(
            build_route_sidebar_html(
                locations, geodesic_points, distance_matrix, path_indices
            )
        )
    )
    map_path = Path(filename).resolve()
    route_map.save(str(map_path))
    webbrowser.open(map_path.as_uri())
    return map_path.name


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


def compute_and_show_route(
    locations, geodesic_points, distance_matrix, start_nr
):
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

    map_filename = draw_route_map(
        locations, geodesic_points, distance_matrix, path_indices
    )
    print(f"Mapa otwarta w przeglądarce ({map_filename}).")
    return path_indices


def print_menu():
    print("\n=== Trasa po parkach Krakowa ===")
    print("1. Oblicz trasę (wybierz park startowy)")
    print("2. Pokaż ostatnią trasę na mapie")
    print("3. Pokaż wszystkie parki (wg numeru)")
    print("4. Pokaż wszystkie parki (alfabetycznie)")
    print("0. Wyjście")


def main():
    print("Przygotowuję lokalizacje i macierz odległości...")
    locations, geodesic_points = prepare_locations()
    distance_matrix = build_distance_matrix(locations, geodesic_points)
    last_path_indices = None
    print("Gotowe.")

    while True:
        print_menu()
        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            start_nr = ask_start_park_nr(locations)
            last_path_indices = compute_and_show_route(
                locations, geodesic_points, distance_matrix, start_nr
            )
        elif choice == "2":
            if last_path_indices is None:
                print("Najpierw oblicz trasę (opcja 1).")
                continue
            map_filename = draw_route_map(
                locations, geodesic_points, distance_matrix, last_path_indices
            )
            print(f"Mapa otwarta w przeglądarce ({map_filename}).")
        elif choice == "3":
            list_parks(
                locations,
                key=lambda item: item[1]["nr"],
                title="Lista parków (wg numeru)",
            )
        elif choice == "4":
            list_parks(
                locations,
                key=lambda item: item[1]["name"].casefold(),
                title="Lista parków (alfabetycznie)",
            )
        elif choice == "0":
            print("Do widzenia.")
            break
        else:
            print("Nieznana opcja. Wybierz 1, 2, 3, 4 albo 0.")


if __name__ == "__main__":
    main()

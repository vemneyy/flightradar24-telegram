import io
import logging
from datetime import datetime
from typing import Dict, Any, List

import folium
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def create_graph(flight_details: Dict[str, Any], path: str = "graph.png") -> str:
    timestamps: List[str] = [
        datetime.fromtimestamp(point["ts"]).strftime("%Y-%m-%d %H:%M:%S")
        for point in flight_details["trail"]
    ][::-1]
    speeds = [point["spd"] for point in flight_details["trail"]][::-1]
    altitudes = [point["alt"] for point in flight_details["trail"]][::-1]

    fig, ax1 = plt.subplots()
    color = "tab:red"
    ax1.set_ylabel("Speed (spd)", color=color)
    ax1.plot(timestamps, speeds, color=color)
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_xticks([])

    ax2 = ax1.twinx()
    color = "tab:blue"
    ax2.set_ylabel("Altitude (alt)", color=color)
    ax2.plot(timestamps, altitudes, color=color)
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    plt.savefig(path)
    plt.close(fig)
    logger.debug("Graph saved to %s", path)
    return path


def create_map(flight_details: Dict[str, Any], current_flight: Any, path: str = "flight_map.png") -> str:
    trail_coordinates = [(point["lat"], point["lng"]) for point in flight_details["trail"]]
    lats, lons = zip(*trail_coordinates)

    try:
        latitude = current_flight.destination_airport_latitude
        longitude = current_flight.destination_airport_longitude
        all_lats = np.append(lats, [latitude, lats[0]])
        all_lons = np.append(lons, [longitude, lons[0]])
        flight_map = folium.Map(location=[all_lats.mean(), all_lons.mean()], zoom_start=10)
        folium.CircleMarker(location=[latitude, longitude], radius=5, color="red", fill=True).add_to(flight_map)
    except Exception:
        all_lats = np.append(lats, [lats[0]])
        all_lons = np.append(lons, [lons[0]])
        flight_map = folium.Map(location=[all_lats.mean(), all_lons.mean()], zoom_start=10)

    flight_path = folium.PolyLine(locations=trail_coordinates, color="blue")
    flight_path.add_to(flight_map)

    for i, point in enumerate(trail_coordinates):
        radius = 0.1 if i not in (0, len(trail_coordinates) - 1) else 5
        color = "blue" if i != len(trail_coordinates) - 1 else "red"
        if i == 0:
            folium.Marker(location=[point[0], point[1]], icon=folium.Icon(color="green", icon="plane", fill=True)).add_to(
                flight_map
            )
        folium.CircleMarker(location=[point[0], point[1]], radius=radius, color=color, fill=True).add_to(flight_map)

    flight_map.options.update({"zoomControl": False, "attributionControl": False})
    flight_map.fit_bounds([(all_lats.min(), all_lons.min()), (all_lats.max(), all_lons.max())])

    img_data = flight_map._to_png()
    img = Image.open(io.BytesIO(img_data))
    img.save(path)
    logger.debug("Map saved to %s", path)
    return path

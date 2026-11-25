from pathlib import Path
import json
import geopandas as gpd
from shapely.geometry import Point


class PuenteAcelMap:
    def __init__(self, shp_path: str | Path, mapa_path: str | Path | None = None):
        self.shp_path = Path(shp_path)
        self.gdf = gpd.read_file(self.shp_path)

        if self.gdf.crs is None:
            self.gdf = self.gdf.set_crs("EPSG:4326")
        elif str(self.gdf.crs) != "EPSG:4326":
            self.gdf = self.gdf.to_crs("EPSG:4326")

        self.mapa_id: dict[int, dict] = {}
        if mapa_path is not None:
            with open(Path(mapa_path), "r", encoding="utf-8") as f:
                raw = json.load(f)
                self.mapa_id = {int(k): v for k, v in raw.items()}

    def consultar(self, lat: float, lon: float) -> dict:
        punto = Point(float(lon), float(lat))
        exactos = self.gdf[self.gdf.contains(punto)]

        if not exactos.empty:
            ids = sorted(exactos["Id"].astype(int).unique().tolist())
            modo = "contiene"
            distancia_grados = 0.0
        else:
            dists = self.gdf.geometry.distance(punto)
            distancia_grados = float(dists.min())
            cercanos = self.gdf[dists == distancia_grados]
            ids = sorted(cercanos["Id"].astype(int).unique().tolist())
            modo = "mas_cercano"

        return {
            "lat": round(float(lat), 6),
            "lon": round(float(lon), 6),
            "modo": modo,
            "distancia_grados": distancia_grados,
            "ids": ids,
            "mapeo": {i: self.mapa_id.get(i) for i in ids},
        }

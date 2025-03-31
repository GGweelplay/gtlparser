"""Main module."""

import ipyleaflet
import xyzservices


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenStreetMap", **kwargs):

        try:
            xyzservices_return = eval(f"ipyleaflet.basemaps.{basemap}")
            if type(xyzservices_return) == xyzservices.lib.TileProvider:
                url = xyzservices_return.build_url()
            elif type(xyzservices_return) == xyzservices.lib.Bunch:
                subset = kwargs.get("subset")
                if subset is None:
                    subset = list(xyzservices_return.keys())[0]
                url = eval(f"ipyleaflet.basemaps.{basemap}.{subset}").build_url()
            layer = ipyleaflet.TileLayer(url=url, name=basemap + subset)
            self.add(layer)
        except:
            raise ValueError(f"Basemap '{basemap}' not found in ipyleaflet basemaps.")

    def add_layer_control(self):
        layer_control = ipyleaflet.LayersControl(position="topright")
        self.add_control(layer_control)

    def add_vector(self, gdf, layer_name, **kwargs):
        geodata = ipyleaflet.GeoData(geo_dataframe=gdf, name=layer_name, **kwargs)
        self.add(geodata)

    def add_google_maps(self, map_type="ROADMAP"):

        map_types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "HYBRID": "y",
            "TERRAIN": "p",
        }
        map_type = map_types[map_type.upper()]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = ipyleaflet.TileLayer(url=url, name="Google Maps")
        self.add(layer)

"""Main module."""

import ipyleaflet
import xyzservices


class Map(ipyleaflet.Map):
    """
    A custom Map class that inherits from ipyleaflet.Map and adds additional
    functionalities for basemap support, layer control, and vector data handling.
    """

    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """
        Initializes the Map object, inherits from ipyleaflet.Map.

        Args:
            center (list): Initial center of the map [latitude, longitude].
            zoom (int): Initial zoom level of the map.
            height (str): Height of the map in CSS units (e.g., "600px").
            **kwargs: Additional keyword arguments to pass to ipyleaflet.Map.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenStreetMap", **kwargs):
        """
        Adds a basemap to the map.

        Args:
            basemap_name (str): The name of the basemap to be added.
                Examples: 'OpenStreetMap', 'Esri.WorldImagery', 'OpenTopoMap'.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.TileLayer.

        Raises:
            ValueError: If the provided basemap_name is not found.

        Returns:
            None: Adds the basemap to the map.
        """
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
        """
        Adds a layer control widget to the map to manage different layers.

        Args:
            None

        Returns:
            None: Adds a layer control widget to the map.
        """
        layer_control = ipyleaflet.LayersControl(position="topright")
        self.add_control(layer_control)

    def add_vector(self, gdf, layer_name, **kwargs):
        """
        Adds vector data (GeoJSON/Shapefile) to the map.

        Args:
            gdf (GeoDataFrame): A GeoDataFrame containing the vector data.
            layer_name (str): The name of the layer to be added.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.GeoData.

        Returns:
            None: Adds the vector data to the map as a LayerGroup.
        """
        geodata = ipyleaflet.GeoData(geo_dataframe=gdf, name=layer_name, **kwargs)
        self.add(geodata)

    def add_google_maps(self, map_type="ROADMAP"):
        """
        Adds Google Maps basemap to the map.

        Args:
            map_type (str): The type of Google Maps to be added.
                Options: 'ROADMAP', 'SATELLITE', 'HYBRID', 'TERRAIN'.

        Returns:
            None: Adds the Google Maps basemap to the map.
        """
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

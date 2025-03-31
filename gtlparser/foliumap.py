"""This module provides a custom Map class that extends folium.Map"""

import folium


class Map(folium.Map):
    """
    A custom Map class that inherits from folium.Map and adds additional
    functionalities for basemap support, layer control, and vector data handling.
    """

    def __init__(self, location=[20, 0], zoom_start=2, height="100%", **kwargs):
        """
        Initializes the Map object, inherits from folium.Map.

        Args:
            location (list): Initial location of the map [latitude, longitude].
            zoom_start (int): Initial zoom level of the map.
            height (str): Height of the map in CSS units (e.g., "100%").
            **kwargs: Additional keyword arguments to pass to folium.Map.
        """
        super().__init__(location=location, zoom_start=zoom_start, **kwargs)
        self._height = height

    def add_basemap(self, basemap="OpenStreetMap"):
        """
        Adds a basemap to the map.

        Args:
            basemap_name (str): The name of the basemap to be added.
                Examples: 'OpenStreetMap', 'Esri.WorldImagery', 'OpenTopoMap'.

        Returns:
            None: Adds the basemap to the map.
        """
        folium.TileLayer(basemap).add_to(self)

    def add_vector(self, gdf, **kwargs):
        """
        Adds vector data (GeoJSON/Shapefile) to the map.

        Args:
            gdf (GeoDataFrame): The vector data to be added to the map.
            **kwargs: Additional keyword arguments to pass to folium.GeoJson.

        Returns:
            None: Adds the vector data to the map.
        """
        gjson = folium.GeoJson(gdf, **kwargs)
        gjson.add_to(self)

    def add_layer_control(self):
        """
        Adds a layer control widget to the map to manage different layers.

        Args:
            None

        Returns:
            None: Adds a layer control widget to the map.
        """
        folium.LayerControl().add_to(self)

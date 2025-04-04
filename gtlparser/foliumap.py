"""This module provides a custom Map class that extends folium.Map"""

import folium


class Map(folium.Map):
    """
    A custom Map class that inherits from folium.Map and adds additional
    functionalities for basemap support, layer control, and vector data handling.
    """

    def __init__(self, location=[20, 0], zoom_start=2, **kwargs):
        """
        Initializes the Map object, inherits from folium.Map.

        Args:
            location (list): Initial location of the map [latitude, longitude].
            zoom_start (int): Initial zoom level of the map.
            **kwargs: Additional keyword arguments to pass to folium.Map.
        """
        super().__init__(location=location, zoom_start=zoom_start, **kwargs)

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

    def add_vector(self, data, **kwargs):
        """
        Adds vector data (GeoJSON/Shapefile) to the map.

        Args:
            data (str or GeoDataFrame): The vector data to be added to the map.
                Can be a file path (str) or a GeoDataFrame.
            **kwargs: Additional keyword arguments for the GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Invalid data type.")

    def add_layer_control(self):
        """
        Adds a layer control widget to the map to manage different layers.

        Args:
            None

        Returns:
            None: Adds a layer control widget to the map.
        """
        folium.LayerControl().add_to(self)

    def add_geojson(self, data, **kwargs):
        """
        Adds GeoJSON data to the map.

        Args:
            data (str or dict): The GeoJson data. Can be a file path (str) or a dictionary.
            **kwargs: Additinoal keyword arguments for the ipyleaflet.GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid
        """
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data

        geojson = folium.GeoJson(data=geojson, **kwargs)
        geojson.add_to(self)

    def add_shp(self, data, **kwargs):
        """
        Adds shapefile data to the map.

        Args:
            data (str): The path to the shapefile.
            **kwargs: Additional keyword arguments for folium.GeoJson.

        Returns:
            None: Adds the shapefile data to the map.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """
        Adds a GeoDataFrame to the map.

        Args:
            gdf (GeoDataFrame): The GeoDataFrame to be added to the map.
            **kwargs: Additional keyword arguments for folium.GeoJson.

        Returns:
            None: Adds the GeoDataFrame to the map.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_split_map(self, left="openstreetmap", right="cartodbpositron", **kwargs):
        """
        Adds a split map to the map.

        Args:
            left (folium.Map): The left map to be added.
            right (folium.Map): The right map to be added.
            **kwargs: Additional keyword arguments for folium.SplitMap.

        Returns:
            None: Adds the split map to the map.
        """

        # Directly pass the 'left' and 'right' arguments (URLs or file paths) 
        # to get_leaflet_tile_layer

        from localtileserver import  get_folium_tile_layer
        from folium import plugins

        if left == "openstreetmap":
          left_tile_layer = folium.TileLayer(left)
        else:
          left_tile_layer = get_folium_tile_layer(left, name="Left Layer")

        if right == "cartodbpositron":
          right_tile_layer = folium.TileLayer(right)
        else:
          right_tile_layer = get_folium_tile_layer(right, name="Right Layer")

        left_tile_layer.add_to(self)
        right_tile_layer.add_to(self)

        side_by_side = plugins.SideBySideLayers(left_tile_layer, right_tile_layer)
        side_by_side.add_to(self)

        self.add_child(folium.LayerControl())
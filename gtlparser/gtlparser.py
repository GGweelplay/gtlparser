"""Main module."""

import ipyleaflet


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
        self.scroll_wheel_zoom = True

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
        import xyzservices

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

    def add_geojson(self, data, hover_style=None, **kwargs):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str or dict): The GeoJson data. Can be a file path (str) or a dictionary.
            hover_style (dict, optional): Style to apply when hovering over features. Defaults to {"color": "yellow", "fillOpacity": 0.2}
            **kwargs: Additinoal keyword arguments for the ipyleaflet.GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add(layer)

    def add_shp(self, data, **kwargs):
        """Adds a shapefile layer to the map.

        Args:
            data (str): Path to the shapefile.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Adds a GeoDataFrame layer to the map.

        Args:
            gdf (GeoDataFrame): The GeoDataFrame to be added to the map.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_raster(self, filepath, colormap="RdYlBu_11", opacity=1.0, **kwargs):
        """Adds a raster layer to the map.

        Args:
            filepath (str): Path to the raster file.
            **kwargs: Additional keyword arguments for the ipyleaflet.ImageOverlay layer.
        """
        from localtileserver import TileClient, get_leaflet_tile_layer

        client = ipyleaflet.TileLayer(filepath)
        tile_layer = get_leaflet_tile_layer(
            client, colormap=colormap, opacity=opacity, **kwargs
        )

        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds=None, opacity=1.0, **kwargs):
        """Adds an image overlay to the map.

        Args:
            image (str): Path to the image file.
            bounds (list): Bounds of the image in the format [[lat1, lon1], [lat2, lon2]].
            **kwargs: Additional keyword arguments for the ipyleaflet.ImageOverlay layer.

        Raises:
            ValueError: If the bounds are not provided.
        """
        from ipyleaflet import ImageOverlay

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        layer = ImageOverlay(url=image, bounds=bounds, opacity=opacity, **kwargs)
        self.add(layer)

    def add_video(self, video, bounds=None, opacity=1.0, **kwargs):
        """Adds a video overlay to the map.

        Args:
            video (str): Path to the video file.
            bounds (list): Bounds of the video in the format [[lat1, lon1], [lat2, lon2]].
            **kwargs: Additional keyword arguments for the ipyleaflet.VideoOverlay layer.

        Raises:
            ValueError: If the bounds are not provided.
        """
        from ipyleaflet import VideoOverlay

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        layer = VideoOverlay(url=video, bounds=bounds, opacity=opacity, **kwargs)
        self.add(layer)

    def add_WMS_layer(
        self, url, layers, name, format="image/png", transparent=True, **kwargs
    ):
        """Adds a WMS layer to the map.

        Args:
            WMSLayer (str): URL of the WMS layer.
            **kwargs: Additional keyword arguments for the ipyleaflet.WMSLayer layer.

        Raises:
            ValueError: If the WMSLayer is not found.
        """
        from ipyleaflet import WMSLayer

        try:
            layer = WMSLayer(
                url=url,
                layers=layers,
                name=name,
                format=format,
                transparent=transparent,
                **kwargs,
            )
            self.add(layer)
        except:
            raise ValueError(f"WMS Layer '{layer}' not found.")

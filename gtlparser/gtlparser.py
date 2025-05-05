"""Main module."""

import os
import ipyleaflet
import ipywidgets as widgets


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

        self.output_widget = widgets.Output()

        self.info_control = ipyleaflet.WidgetControl(
            widget=self.output_widget, position="bottomright"
        )

        self.add_control(self.info_control)

        self._setup_hover_handler()

    def _setup_hover_handler(self):
        """
        Defines the internal hover handler method.
        This method is called when a feature is hovered over on the map.
        It displays the properties of the hovered feature in an output widget.
        """
        from IPython.display import display

        def hover_handler(event=None, feature=None, **kwargs):
            """
            Handles the hover event on the map.
            event: The event object containing information about the hover event.
            feature: The feature being hovered over.
            kwargs: Additional keyword arguments.
            """
            self.output_widget.clear_output()

            with self.output_widget:
                if feature:
                    properties = feature["properties"]

                    info_html = """
                    <div style="padding: 5px; background-color: white; border: 1px solid grey;">
                    """
                    info_html += "<b>Properties:</b><br>"
                    if properties:
                        for key, value in properties.items():
                            if key.lower() not in [
                                "geometry",
                                "shape_length",
                                "shape_area",
                            ]:
                                info_html += f"<b>{key}:</b> {value}<br>"
                    else:
                        info_html += "No properties available."

                    info_html += "</div>"
                    display(widgets.HTML(info_html))
                else:
                    display(widgets.HTML("Hover over a feature"))

        self.hover_handler_method = hover_handler

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

    def add_basemap_gui(self, options=None, position="topright"):
        """
        Adds a GUI for selecting basemaps to the map.
        Args:
            options (list): List of available basemaps to choose from.
                If None, defaults to a predefined list.
            position (str): Position of the widget on the map.
                Options: 'topleft', 'topright', 'bottomleft', 'bottomright'.

        Behavior:
            - A toggle button to show/hide the dropdown and close button.
            - A dropdown menu to select the basemap.
            - A close button to remove the widget from the map.

        Events handlers:
            - `on_toggle_change`: Toggles the visibility of the dropdown and close button.
            - `on_button_click`: Closes the widget when the close button is clicked.
            - `on_dropdown_change`: Changes the basemap when a new option is selected.
        """
        if options is None:
            options = [
                "OpenStreetMap.Mapnik",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "CartoDB.DarkMatter",
            ]

        toggle = widgets.ToggleButton(
            value=True,
            button_style="",
            tooltip="Click me",
            icon="map",
        )
        toggle.layout = widgets.Layout(width="38px", height="38px")

        dropdown = widgets.Dropdown(
            options=options,
            value=options[0],
            description="Basemap: ",
            style={"description_width": "initial"},
        )
        dropdown.layout = widgets.Layout(width="250px", height="38px")

        button = widgets.Button(
            icon="times",
        )
        button.layout = widgets.Layout(width="38px", height="38px")

        hbox = widgets.HBox([toggle, dropdown, button])

        def on_toggle_change(change):
            if change["new"]:
                hbox.children = [toggle, dropdown, button]
            else:
                hbox.children = [toggle]

        toggle.observe(on_toggle_change, names="value")

        def on_button_click(b):
            hbox.close()
            toggle.close()
            dropdown.close()
            button.close()

        button.on_click(on_button_click)

        def on_dropdown_change(change):
            if change["new"]:
                self.layers = self.layers[:-2]
                self.add_basemap(change["new"])

        dropdown.observe(on_dropdown_change, names="value")

        control = ipyleaflet.WidgetControl(widget=hbox, position=position)
        self.add(control)

    def add_search_control(self, position="topleft", **kwargs):
        """
        Adds a search control to the map.

        Args:
            position (str): Position of the search control on the map.
                Options: 'topleft', 'topright', 'bottomleft', 'bottomright'.
            **kwargs: Additional keyword arguments for ipyleaflet.SearchControl.

        Returns:
            None: Adds the search control to the map.
        """
        url = "https://nominatim.openstreetmap.org/search?format=json&q={s}"
        search_control = ipyleaflet.SearchControl(
            position=position, url=url, zoom=12, marker=None, **kwargs
        )
        self.add_control(search_control)

    def add_widget(self, widget, position="topright", **kwargs):
        """
        Adds a widget to the map.

        Args:
            widget (ipywidgets.Widget): The widget to be added to the map.
            position (str): Position of the widget on the map.
                Options: 'topleft', 'topright', 'bottomleft', 'bottomright'.
            **kwargs: Additional keyword arguments for ipyleaflet.WidgetControl.
        """
        control = ipyleaflet.WidgetControl(widget=widget, position=position, **kwargs)
        self.add(control)

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

    def add_geojson(self, data, layer_style=None, hover_style=None, **kwargs):
        """Adds a GeoJSON layer to the map with automatic hover inspection.

        Args:
            data (str or dict): The GeoJson data. Can be a file path (str) or a dictionary.
            layer_style (dict, optional): Style to apply to the layer.
                                         Defaults to {"color": "blue", "fillOpacity": 0.5} for polygons,
                                        {"color": "blue", "weight": 3, "opacity": 0.8} for lines,
                                        {"radius": 5, "color": "blue", 'fillColor': '#3388ff', 'fillOpacity': 0.8, 'weight': 1} for points.
            hover_style (dict, optional): Style to apply when hovering over features.
                                         Defaults to {"color": "yellow", "fillOpacity": 0.2} for polygons,
                                         {"color": "yellow", "weight": 4} for lines,
                                         {"radius": 7, "color": "yellow", "fillColor": "yellow", "fillOpacity": 0.8} for points.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.
        """
        import geopandas as gpd

        if isinstance(data, str):
            try:
                gdf = gpd.read_file(data)
                geojson_data = gdf.__geo_interface__
                geometry_type = (
                    gdf.geometry.iloc[0].geom_type if not gdf.empty else None
                )
            except Exception as e:
                print(f"Error reading GeoJSON file: {e}")
                return
        elif isinstance(data, dict):
            geojson_data = data
            geometry_type = (
                geojson_data["features"][0]["geometry"]["type"]
                if geojson_data.get("features")
                else None
            )
        else:
            raise ValueError("Data must be a file path (str) or a dictionary.")
        print(geometry_type)

        if layer_style is None:
            if geometry_type == "Polygon":
                layer_style = {"color": "blue", "fillOpacity": 0.5}
            elif geometry_type == "LineString":
                layer_style = {"color": "blue", "weight": 3, "opacity": 0.8}
            elif geometry_type == "Point":
                layer_style = {
                    "radius": 5,
                    "color": "blue",
                    "fillColor": "#3388ff",
                    "fillOpacity": 0.8,
                    "weight": 1,
                }
            else:
                layer_style = {}

        if hover_style is None:
            if geometry_type == "Polygon":
                hover_style = {"color": "yellow", "fillOpacity": 0.2}
            elif geometry_type == "LineString":
                hover_style = {"color": "yellow", "weight": 4, "opacity": 1}
            elif geometry_type == "Point":
                hover_style = {"fillColor": "red", "fillOpacity": 1}
            else:
                hover_style = {}

        print(layer_style, hover_style)

        if geometry_type == "Point":
            layer = ipyleaflet.GeoJSON(
                data=geojson_data,
                point_style=layer_style,
                hover_style=hover_style,
                **kwargs,
            )
        elif geometry_type == "LineString":
            layer = ipyleaflet.GeoJSON(
                data=geojson_data, style=layer_style, hover_style=hover_style, **kwargs
            )
        elif geometry_type == "Polygon":
            layer = ipyleaflet.GeoJSON(
                data=geojson_data, style=layer_style, hover_style=hover_style, **kwargs
            )
        layer.on_hover(self.hover_handler_method)
        self.add_layer(layer)

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

    def add_raster(self, filepath, colormap="viridis", opacity=1.0, **kwargs):
        """Adds a raster layer to the map.

        Args:
            filepath (str): Path to the raster file.
            colormap (str): Colormap to be applied to the raster data.
            opacity (float): Opacity of the raster layer (0.0 to 1.0).
            **kwargs: Additional keyword arguments for the ipyleaflet.ImageOverlay layer.
        """
        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(filepath)
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
            opacity (float): Opacity of the image overlay (0.0 to 1.0).
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
            opacity (float): Opacity of the video overlay (0.0 to 1.0).
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
            url (str): URL of the WMS layer.
            layers (str): Comma-separated list of layer names.
            name (str): Name of the layer.
            format (str): Format of the layer (default: "image/png").
            transparent (bool): Whether the layer is transparent (default: True).
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

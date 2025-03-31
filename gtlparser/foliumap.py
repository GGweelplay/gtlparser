import folium


class Map(folium.Map):
    def __init__(self, location=[20, 0], zoom_start=2, height="100%", **kwargs):
        super().__init__(location=location, zoom_start=zoom_start, **kwargs)
        self._height = height

    def add_basemap(self, basemap="OpenStreetMap"):
        folium.TileLayer(basemap).add_to(self)

    def add_vector(self, gdf, **kwargs):
        gjson = folium.GeoJson(gdf, **kwargs)
        gjson.add_to(self)

    def add_layer_control(self):
        folium.LayerControl().add_to(self)

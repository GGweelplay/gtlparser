# Welcome to gtlparser


[![image](https://img.shields.io/pypi/v/gtlparser.svg)](https://pypi.python.org/pypi/gtlparser)


**A python package for Google Time Line data analysis**


-   Free software: MIT License
-   Documentation: <https://GGweelplay.github.io/gtlparser>


## Introduction

The gtlparser addresses the challenge of converting raw location data downloaded from Google Timeline into a standardized and easily usable format for spatial analysis and visualization. Google Timeline provides a rich source of spatiotemporal information, capturing detailed latitude, longitude, and timestamp data of a user's movements. However, the native JSON format can be cumbersome to work with directly in many geospatial tools.

This package provides a convenient solution by transforming the Google Timeline JSON data into the GeoJSON format. GeoJSON is a widely supported standard for encoding geographic data structures, making it ideal for representing trajectories and points of interest. By converting your timeline data to GeoJSON, you can seamlessly integrate it with various mapping and Geographic Information System (GIS) software, enabling you to visualize your space-time trajectory, perform spatial analysis, and gain insights from your location history.

## Target Audience
This package is designed for researchers, data analysts, educators, and individuals who wish to explore, visualize, and analyze their personal Google Timeline data using standard geospatial tools.
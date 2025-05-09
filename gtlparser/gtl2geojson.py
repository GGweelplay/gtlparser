from argparse import ArgumentParser
import datetime
from datetime import datetime
import json
import os
from os.path import join as osjoin, splitext
from geojson import Point, LineString, Feature, FeatureCollection, dump


def parse_point_latlong(subset_visit):
    """
    Parse the latitude and longitude from the subset_visit dictionary.

    Args:
        subset_visit (dict): The subset visit dictionary containing the location information.

    Returns:
        The latitude and longitude as floats.
    """

    temp_subset = subset_visit.get("topCandidate")
    temp_lat, temp_long = (
        temp_subset["placeLocation"]["latLng"].replace("°", "").split(", ")
    )
    return float(temp_lat), float(temp_long)


def parse_hierarchyLevel(subset_visit):
    """
    Parse the hierarchy level from the subset_visit dictionary.

    Args:
        subset_visit (dict): The subset visit dictionary containing the hierarchy level.

    Returns:
        str: The hierarchy level of the visit.
    """
    return subset_visit["hierarchyLevel"]


def parse_probability(subset_visit):
    """
    Parse the probability from the subset_visit dictionary.

    Args:
        subset_visit (dict): The subset visit dictionary containing the probability.

    Returns:
        float: The probability of the visit.
    """
    return subset_visit["probability"]


def parse_topCadidate_placeId(subset_visit):
    """
    Parse the place ID from the subset_visit dictionary.

    Args:
        subset_visit (dict): The subset visit dictionary containing the place ID.

    Returns:
        str: The place ID of the visit.
    """
    return subset_visit["topCandidate"]["placeId"]


def parse_topCadidate_semanticType(subset_visit):
    """
    Parse the semantic type from the subset_visit dictionary.

    Args:
        subset_visit (dict): The subset visit dictionary containing the semantic type.

    Returns:
        str: The semantic type of the visit.
    """
    return subset_visit["topCandidate"]["semanticType"]


def parse_topCadidate_probability(subset_visit):
    """
    Parse the top candidate probability from the subset_visit dictionary.

    Args:
        subset_visit (dict): The subset visit dictionary containing the top candidate probability.

    Returns:
        float: The top candidate probability of the visit.
    """
    return subset_visit["topCandidate"]["probability"]


def read_json_from_url(url):
    """
    Read JSON data from a URL.

    Args:
        url (str): The URL to read the JSON data from.

    Returns:
        dict: The JSON data as a dictionary.
    """

    import requests
    import json

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.decoder.JSONDecodeError as e:
        print(f"JSON Decode error: {e}")
        return None


def parse_visitPoint(in_json, flag_allField=0):
    """
    Parse the visit point from the json_data dictionary.

    Args:
        json_data (dict): The JSON data containing the visit point information.
        flag_allField (int): Flag to indicate whether to include all fields in the output.

    Returns:
        FeatureCollection: A collection of point features extracted from the JSON data.
    """
    if in_json.startswith("http://") or in_json.startswith("https://"):
        json_data = read_json_from_url(in_json)
    elif os.path.exists(in_json):
        json_data = json.loads(open(in_json, encoding="utf8").read())

    point_features = []
    for item in json_data["semanticSegments"]:
        try:
            item_keys = list(
                item.keys()
            )  # visit, timelinePath, timelineMemory, activity
            if "visit" in item_keys:
                # print("processing point...")
                temp_startTime = item.get("startTime")
                temp_endTime = item.get("endTime")
                subset_visit = item.get("visit")
                temp_lat, temp_long = parse_point_latlong(subset_visit)
                temp_point = Point((temp_long, temp_lat))
                if flag_allField == 1:
                    point_output = {
                        "startTime": temp_startTime,
                        "endTime": temp_endTime,
                        "hierarchyLevel": parse_hierarchyLevel(subset_visit),
                        "probability": parse_probability(subset_visit),
                        "placeId": parse_topCadidate_placeId(subset_visit),
                        "semanticType": parse_topCadidate_semanticType(subset_visit),
                        "topCadidate_probability": parse_topCadidate_probability(
                            subset_visit
                        ),
                    }
                    point_features.append(
                        Feature(geometry=temp_point, properties=point_output)
                    )
                else:
                    point_output = {
                        "startTime": temp_startTime,
                        "endTime": temp_endTime,
                    }
                    point_features.append(
                        Feature(geometry=temp_point, properties=point_output)
                    )
        except Exception as e:
            raise Exception(e)
    feature_collection_point = FeatureCollection(point_features)
    return feature_collection_point


def parse_timelinePath(in_json):
    """
    Parse the timeline path from the json_data dictionary.

    Args:
        json_data (dict): The JSON data containing the timeline path information.

    Returns:
        FeatureCollection: A collection of line features extracted from the JSON data.
    """
    if in_json.startswith("http://") or in_json.startswith("https://"):
        json_data = read_json_from_url(in_json)
    elif os.path.exists(in_json):
        json_data = json.loads(open(in_json, encoding="utf8").read())

    line_features = []
    for item in json_data["semanticSegments"]:
        try:
            item_keys = list(
                item.keys()
            )  # visit, timelinePath, timelineMemory, activity
            if "timelinePath" in item_keys:
                temp_startTime = item.get("startTime")
                temp_endTime = item.get("endTime")
                list_points = []
                for timeline_path in item["timelinePath"]:
                    latitude, longitude = (
                        timeline_path["point"].replace("°", "").split(", ")
                    )
                    time = datetime.strptime(
                        timeline_path["time"], "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                    list_points.append((float(longitude), float(latitude)))
                if len(list_points) > 1:
                    temp_line = LineString(list_points)
                    line_features.append(
                        Feature(
                            geometry=temp_line,
                            properties={
                                "startTime": temp_startTime,
                                "endTime": temp_endTime,
                            },
                        )
                    )
        except Exception as e:
            raise Exception(e)
    feature_collection_line = FeatureCollection(line_features)
    return feature_collection_line


def create_geojson_file(output_path, output_name, feature_collection, flag_point=True):
    """
    Create a GeoJSON file from the feature collection.

    Args:
        output_path (str): The path where the GeoJSON file will be saved.
        output_name (str): The name of the output GeoJSON file.
        feature_collection (FeatureCollection): The feature collection to be saved.
        flag_point (bool): Flag to indicate whether the features are points or lines.

    Returns:
        None
    """
    if flag_point:
        with open(f"{output_path}/point_{output_name}.geojson", "w") as f:
            dump(feature_collection, f)
    else:
        with open(f"{output_path}/line_{output_name}.geojson", "w") as f:
            dump(feature_collection, f)

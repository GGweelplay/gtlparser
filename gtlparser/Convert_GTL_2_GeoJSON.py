from argparse import ArgumentParser
import datetime
import json
import os
from os.path import join as osjoin, splitext
from osgeo import ogr
from osgeo.ogr import Feature, FieldDefn, Geometry, GetDriverByName, wkbPoint
from osgeo.osr import SpatialReference
from geojson import Point, LineString, Feature, FeatureCollection, dump


def make_reader(in_json):
    # Open location history data
    json_data = json.loads(open(in_json, encoding="utf8").read())
    return json_data


# Get value (either placeVisit or activitySegment) from input json
def create_point_file(input_json, output_folder, output_name):
    point_features = []
    failed_features = []
    for item in input_json["timelineObjects"]:
        try:
            if list(item.keys())[0] == "placeVisit":
                placeVisit = item
                point_output = parse_placeVisit_items(placeVisit)
                try:
                    point = Point(
                        (point_output["centerLngE7"], point_output["centerLatE7"])
                    )
                except:
                    point = Point(
                        (point_output["longitudeE7"], point_output["latitudeE7"])
                    )
                point_features.append(Feature(geometry=point, properties=point_output))
        except:
            failed_features.append(item)
    feature_collection_point = FeatureCollection(point_features)

    with open(f"{output_folder}/point_{output_name}.geojson", "w") as f:
        dump(feature_collection_point, f)
    with open(f"{output_folder}/failed_point_{output_name}.geojson", "w") as f:
        json.dump(failed_features, f)


def create_line_file(input_json, output_folder, output_name):
    line_features = []
    failed_features = []
    for item in input_json["timelineObjects"]:
        try:
            if list(item.keys())[0] == "activitySegment":
                activitySegment = item
                line_output = parse_activitySegment_items(activitySegment)
                line = LineString(line_output["waypoints"])
                line_features.append(Feature(geometry=line, properties=line_output))
        except:
            failed_features.append(item)
    feature_collection_line = FeatureCollection(line_features)

    with open(f"{output_folder}/line_{output_name}.geojson", "w") as f:
        dump(feature_collection_line, f)
    with open(f"{output_folder}/failed_line_{output_name}.geojson", "w") as f:
        json.dump(failed_features, f)


# -------------------------------------


def parse_coordinate(inputCoordinate):
    return inputCoordinate / 10000000


def parse_sourceInfo(inputDict, temp_allFields_dict, withPrefix=False, prefix="start"):
    if withPrefix == 0:
        for subfield in inputDict:
            temp_allFields_dict["sourceInfo"] = subfield
            temp_allFields_dict[subfield] = inputDict.get(subfield)
    else:
        for subfield in inputDict:
            temp_allFields_dict[f"{prefix}_sourceInfo"] = subfield
            temp_allFields_dict[f"{prefix}_" + subfield] = inputDict.get(subfield)


# -------------------------------------


def parse_placeVisit_items(placeVisit):
    # Get values (dict) from input placeVisit
    subset_placeVisit = placeVisit.get("placeVisit")
    # Create temporary dict
    temp_allFields_dict = {}
    # Get values (aggregated fields) from input
    for aggregatedFields in subset_placeVisit:
        if aggregatedFields == "location":
            parse_placeVisit_location(
                subset_placeVisit.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "childVisits":
            parse_placeVisit_childVisits(
                subset_placeVisit.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "duration":
            parse_placeVisit_duration(
                subset_placeVisit.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "otherCandidateLocations":
            parse_placeVisit_location(
                subset_placeVisit.get(aggregatedFields),
                temp_allFields_dict,
                otherCandidateLocation=True,
            )
        elif aggregatedFields == "centerLatE7" or aggregatedFields == "centerLngE7":
            temp_allFields_dict[aggregatedFields] = parse_coordinate(
                subset_placeVisit.get(aggregatedFields)
            )
        else:
            temp_allFields_dict[aggregatedFields] = subset_placeVisit.get(
                aggregatedFields
            )
    return temp_allFields_dict


def parse_placeVisit_location(
    inputDict, temp_allFields_dict, otherCandidateLocation=False, childVisit=False
):
    if otherCandidateLocation == 0:
        for subfield in inputDict:
            if subfield == "latitudeE7" or subfield == "longitudeE7":
                temp_allFields_dict[subfield] = parse_coordinate(
                    inputDict.get(subfield)
                )
            elif subfield == "name":
                if childVisit:
                    temp_allFields_dict[subfield] = (
                        inputDict.get(subfield) + " " + temp_allFields_dict[subfield]
                    )
                else:
                    temp_allFields_dict[subfield] = inputDict.get(subfield)
            elif subfield == "sourceInfo":
                sourceInfo_dict = inputDict.get(subfield)
                parse_sourceInfo(sourceInfo_dict, temp_allFields_dict)
            else:
                temp_allFields_dict[subfield] = inputDict.get(subfield)
    else:  # to be continue
        temp_allFields_dict["otherCandidateFields"] = inputDict


def parse_placeVisit_childVisits(inputList, temp_allFields_dict):
    childVisitDict = inputList[0]
    for aggregatedFields in childVisitDict:
        if aggregatedFields == "location":
            parse_placeVisit_location(
                childVisitDict.get(aggregatedFields),
                temp_allFields_dict,
                childVisit=True,
            )
        elif aggregatedFields == "duration":
            parse_placeVisit_duration(
                childVisitDict.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "otherCandidateLocations":
            parse_placeVisit_location(
                childVisitDict.get(aggregatedFields),
                temp_allFields_dict,
                otherCandidateLocation=True,
            )
        else:
            temp_allFields_dict[aggregatedFields] = childVisitDict.get(aggregatedFields)


# can customize the time zone
def parse_placeVisit_duration(inputDict, temp_allFields_dict):
    for subfield in inputDict:
        temp_time_string = datetime.datetime.fromisoformat(
            inputDict.get(subfield)
        ).strftime("%Y-%m-%d %H:%M:%S")
        temp_time = datetime.datetime.strptime(temp_time_string, "%Y-%m-%d %H:%M:%S")
        ETZ_datetime = temp_time - datetime.timedelta(hours=5)
        temp_allFields_dict[subfield + "recordDate"] = ETZ_datetime.strftime("%Y-%m-%d")
        temp_allFields_dict[subfield + "recordTime"] = ETZ_datetime.strftime("%H:%M:%S")


# ----------------------------------------


def parse_activitySegment_items(activitySegment):
    # Get values (dict) from input activitySegment
    subset_activitySegment = activitySegment.get("activitySegment")
    # Create temporary dict
    temp_allFields_dict = {}
    # Get values (aggregated fields) from input
    for aggregatedFields in subset_activitySegment:
        if aggregatedFields == "startLocation":
            parse_activitySegment_startLocation(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "endLocation":
            parse_activitySegment_endLocation(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "duration":
            parse_activitySegment_duration(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "activities":
            parse_activitySegment_activities(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "waypointPath":
            parse_activitySegment_waypointPath(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "simplifiedRawPath":
            parse_activitySegment_simplifiedRawPath(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        elif aggregatedFields == "parkingEvent":
            parse_activitySegment_parkingEvent(
                subset_activitySegment.get(aggregatedFields), temp_allFields_dict
            )
        else:
            temp_allFields_dict[aggregatedFields] = subset_activitySegment.get(
                aggregatedFields
            )
    return temp_allFields_dict


def parse_activitySegment_startLocation(inputDict, temp_allFields_dict):
    for subfield in inputDict:
        if subfield == "latitudeE7":
            temp_allFields_dict["start_latitudeE7"] = parse_coordinate(
                inputDict.get(subfield)
            )
        elif subfield == "longitudeE7":
            temp_allFields_dict["start_longitudeE7"] = parse_coordinate(
                inputDict.get(subfield)
            )
        elif subfield == "sourceInfo":
            sourceInfo_dict = inputDict.get(subfield)
            parse_sourceInfo(sourceInfo_dict, temp_allFields_dict, withPrefix=True)


def parse_activitySegment_endLocation(inputDict, temp_allFields_dict):
    for subfield in inputDict:
        if subfield == "latitudeE7":
            temp_allFields_dict["end_latitudeE7"] = parse_coordinate(
                inputDict.get(subfield)
            )
        elif subfield == "longitudeE7":
            temp_allFields_dict["end_longitudeE7"] = parse_coordinate(
                inputDict.get(subfield)
            )
        elif subfield == "sourceInfo":
            sourceInfo_dict = inputDict.get(subfield)
            parse_sourceInfo(
                sourceInfo_dict, temp_allFields_dict, withPrefix=True, prefix="end"
            )


def parse_activitySegment_duration(inputDict, temp_allFields_dict):
    for subfield in inputDict:
        temp_time_string = datetime.datetime.fromisoformat(
            inputDict.get(subfield)
        ).strftime("%Y-%m-%d %H:%M:%S")
        temp_time = datetime.datetime.strptime(temp_time_string, "%Y-%m-%d %H:%M:%S")
        ETZ_datetime = temp_time - datetime.timedelta(hours=5)
        temp_allFields_dict[subfield + "recordDate"] = ETZ_datetime.strftime("%Y-%m-%d")
        temp_allFields_dict[subfield + "recordTime"] = ETZ_datetime.strftime("%H:%M:%S")


def parse_activitySegment_activities(inputDict, temp_allFields_dict):
    temp_allFields_dict["activities"] = inputDict


def parse_activitySegment_waypointPath(inputDict, temp_allFields_dict):
    for subfield in inputDict:
        if subfield == "waypoints":
            temp_allFields_dict["waypoints"] = parse_activitySegment_waypoints(
                inputDict.get(subfield), temp_allFields_dict
            )
        elif subfield == "roadSegment":
            continue
        elif subfield == "confidence":
            temp_allFields_dict["travelMode_confidence"] = inputDict.get(subfield)
        else:
            temp_allFields_dict[subfield] = inputDict.get(subfield)


def parse_activitySegment_waypoints(inputDict, temp_allFields_dict):
    temp_points_list = []
    for point_dict in inputDict:
        temp_points_list.append(
            (
                parse_coordinate(point_dict["lngE7"]),
                parse_coordinate(point_dict["latE7"]),
            )
        )
    return temp_points_list


def parse_activitySegment_simplifiedRawPath(inputDict, temp_allFields_dict):
    temp_allFields_dict["simplifiedRawPath"] = inputDict


def parse_activitySegment_parkingEvent(inputDict, temp_allFields_dict):
    for subfield in inputDict:
        if subfield == "location":
            subDict = inputDict.get(subfield)
            temp_allFields_dict["parkingEvent_point"] = (
                parse_coordinate(subDict["longitudeE7"]),
                parse_coordinate(subDict["latitudeE7"]),
            )
            temp_allFields_dict["parkingEvent_accuracyMetres"] = subDict[
                "accuracyMetres"
            ]
        elif subfield == "method":
            temp_allFields_dict["parkingEvent_method"] = inputDict.get(subfield)
        elif subfield == "locationSource":
            temp_allFields_dict["parkingEvent_locationSource"] = inputDict.get(subfield)
        elif subfield == "timestamp":
            temp_allFields_dict["parkingEvent_timestamp"] = (
                datetime.datetime.fromisoformat(inputDict.get(subfield)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


# ----------------------------------------


def init_parser():

    parser = ArgumentParser(description="Convert Google Takeout Data")
    parser.add_argument(
        "location_history_file",
        type=str,
        help="Path to location history file to analyze.",
    )
    parser.add_argument(
        "output_location", type=str, help="Path to folder to write output"
    )
    parser.add_argument("output_name_point", type=str, help="Name of output Point file")
    parser.add_argument("output_name_line", type=str, help="Name of output Line file")
    return parser


def main():
    parser = init_parser()
    args = parser.parse_args()
    reader = make_reader(args.location_history_file)
    create_point_file(reader, args.output_location, args.output_name_point)
    create_line_file(reader, args.output_location, args.output_name_line)


if __name__ == "__main__":
    main()


# Sameple command: python ./Src/Convert_GTL_2_GeoJSON.py C:/Users/tiger/OneDrive/PhD/Spring_2024/GEOG517/Final_Project/GTL_CSV/GTL_2023_NOVEMBER.json C:/Users/tiger/OneDrive/PhD/Spring_2024/GEOG517/Final_Project/GeoJSON 2023_Nov 2023_Nov

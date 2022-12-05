import json
from webapp.db_models import GeoData


# function to put the geojson file into the database
def geojson_to_mongo():

    with open('webapp/static/util/geodata.json', encoding="utf-8") as json_file:
        geojson = json.load(json_file)

    for entry in geojson["features"]:
        new_geodata = GeoData(
            id=entry["id"],
            name=entry["properties"]["name"],
            lon=entry["properties"]["lon"],
            lat=entry["properties"]["lat"],
        )
        new_geodata.save()

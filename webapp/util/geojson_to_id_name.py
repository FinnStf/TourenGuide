import json


#
# create a file that contains all district ids and names
#
def geojson_to_id_name():
    id_name_list = []
    with open('webapp/static/util/geodata.json', encoding="utf-8") as json_file:
        geojson = json.load(json_file)

    for entry in geojson["features"]:
        id_name_list.append(dict({"id": entry["id"], "name": entry["properties"]["name"]}))

    with open('webapp/static/util/district_id_name.json', 'w', encoding="utf-8") as fout:
        json.dump(id_name_list, fout, ensure_ascii=False)

import json

from webapp.db_models import DailyData, MonthlyData, SavedMaps


#
# get the domestic traffic for the given dataset_type, start_date and end_date
#
def get_domestic_traffic(dataset_type, start_date, end_date):
    domestic_traffic = []
    datasets = get_datasets_from_db(dataset_type, start_date, end_date)

    # choose the entries where the start is equal to the end
    for entry in datasets:
        if entry["startName"] == entry["endName"]:
            domestic_traffic = sum_all_modes_of_transport(entry, domestic_traffic)
    return domestic_traffic


#
# get the outgoing traffic for the given dataset_type, start_date and end_date
#
def get_outgoing_traffic(dataset_type, start_date, end_date):
    datasets = get_datasets_from_db(dataset_type, start_date, end_date)
    with open("webapp/static/util/district_id_name.json", 'r', encoding="utf-8") as j:
        district_id_name = json.loads(j.read())
    for entry in district_id_name:
        count = 0
        for dataset in datasets:
            # check if start is selected district and start is not same as end
            if dataset["startName"] == entry["name"] and dataset["startName"] != dataset["endName"]:
                count += dataset["count"]
        entry["count"] = count
    return district_id_name


#
# get the incoming traffic for the given dataset_type, start_date and end_date
#
def get_incoming_traffic(dataset_type, start_date, end_date):
    datasets = get_datasets_from_db(dataset_type, start_date, end_date)
    with open("webapp/static/util/district_id_name.json", 'r', encoding="utf-8") as j:
        district_id_name = json.loads(j.read())
    for entry in district_id_name:
        count = 0
        for dataset in datasets:
            # check if start is selected district and start is not same as end
            if dataset["endName"] == entry["name"] and dataset["startName"] != dataset["endName"]:
                count += dataset["count"]
        entry["count"] = count
    return district_id_name


#
# get the total traffic for the given dataset_type, start_date, end_date
#
def get_total_traffic(dataset_type, start_date, end_date):
    datasets = get_datasets_from_db(dataset_type, start_date, end_date)
    with open("webapp/static/util/district_id_name.json", 'r', encoding="utf-8") as j:
        district_id_name = json.loads(j.read())
    for entry in district_id_name:
        count = 0
        for dataset in datasets:
            # check if start is selected district and start is not same as end
            if dataset["endName"] == entry["name"] or dataset["startName"] == dataset["endName"]:
                count += dataset["count"]
        entry["count"] = count
    return district_id_name


#
# get the traffic depending on the traffic_type
#
def traffic_controller(traffic_type, dataset_type, start_date, end_date):
    if traffic_type == "Binnen-Verkehr":
        return get_domestic_traffic(dataset_type, start_date, end_date)
    elif traffic_type == "Outgoing-Verkehr":
        return get_outgoing_traffic(dataset_type, start_date, end_date)
    elif traffic_type == "Incoming-Verkehr":
        return get_incoming_traffic(dataset_type, start_date, end_date)
    elif traffic_type == "Gesamtverkehr":
        return get_total_traffic(dataset_type, start_date, end_date)


#
# sums the counts in an entry for a given list if entry is already in this list
#
def sum_all_modes_of_transport(entry, domestic_traffic):
    if is_json_with_attr_in_list(domestic_traffic, "id", entry["startId"]):
        # throw all modes of transport together
        for domestic_traffic_entry in domestic_traffic:
            # if entry is already contained: only add the count
            if domestic_traffic_entry["name"] == entry["startName"]:
                domestic_traffic_entry["count"] += entry["count"]
    else:
        domestic_traffic.append(dict({'id': entry["startId"], 'count': entry["count"],
                                      'name': entry["startName"]}))
    return domestic_traffic


#
# checks if list check_list contains attribute attr
#
def is_json_with_attr_in_list(check_list, keyword, attr):
    for entry in check_list:
        if entry[keyword] == attr:
            return True
    return False


#
# get the suitable datasets from the db for the dataset_type, start_date, end_date
#
def get_datasets_from_db(dataset_type, start_date, end_date):
    datasets = []
    if dataset_type == "Täglicher Datensatz":
        if start_date is None or end_date is None:
            datasets = DailyData.objects().all().as_pymongo()
        else:
            datasets = DailyData.objects(bucket__gte=start_date,
                                         bucket__lte=end_date).all().as_pymongo()
    elif dataset_type == "Monatlicher Datensatz":
        if start_date is None or end_date is None:
            datasets = MonthlyData.objects().all().as_pymongo()
        else:
            datasets = MonthlyData.objects(bucket__gte=start_date,
                                           bucket__lte=end_date).all().as_pymongo()
    return datasets


#
# sets the form fields with the given parameters
#
def set_filter_fields(filter_form, graph_id):
    import json
    from datetime import datetime
    inputs = json.loads(SavedMaps.objects(_id=graph_id).values_list("input").as_pymongo()[0])
    filter_form.start_date.data = datetime.strptime(inputs["start_date"], "%Y-%m-%d")
    filter_form.end_date.data = datetime.strptime(inputs["end_date"], "%Y-%m-%d")
    filter_form.traffic_type.data = inputs["traffic_type"]
    filter_form.dataset_type.data = inputs["dataset_type"]
    filter_form.color_scale.data = inputs["color_scale"]
    filter_form.upper_range_color.data = inputs["upper_range_color"]
    filter_form.lower_range_color.data = inputs["lower_range_color"]
    if inputs["start_date_compare"] and inputs["end_date_compare"]:
        filter_form.start_date_compare.data = datetime.strptime(inputs["start_date_compare"], "%Y-%m-%d")
        filter_form.end_date_compare.data = datetime.strptime(inputs["end_date_compare"], "%Y-%m-%d")
    filter_form.proportion_unit.data = inputs["proportion_unit"]
    filter_form.reverse_colorscale.data = inputs["reverse_colorscale"]


#
# calculate the count for a compare graph
# returns the traffic list
#
def calc_compare_graph(inputs, traffic):
    traffic_compare = traffic_controller(inputs.traffic_type, inputs.dataset_type, inputs.start_date_compare,
                                         inputs.end_date_compare)
    traffic_compare = crop_districts(traffic_compare)
    traffic = crop_districts(traffic)

    # sort the both lists to match the ids at the same index
    traffic.sort(key=lambda x: x["id"], reverse=True)
    traffic_compare.sort(key=lambda x: x["id"], reverse=True)
    if inputs.proportion_unit == "Absolute Zahlen":
        for i in range(len(traffic)):
            traffic[i]["count"] = traffic_compare[i]["count"] - traffic[i]["count"]
    else:
        for i in range(len(traffic)):
            # prevent divison by zero
            if traffic[i]["count"] == 0:
                traffic[i]["count"] = 100
            else:
                traffic[i]["count"] = round((traffic_compare[i]["count"] / traffic[i]["count"] - 1) * 100, 2)

    return traffic


#
# gets a list and crops out the non-bavarian districts
#
def crop_districts(traffic):
    bavarian_ids = get_bavarian_ids()

    bavarian_traffic = []
    for entry in traffic:
        if entry["id"] in bavarian_ids:
            bavarian_traffic.append(entry)
    return bavarian_traffic


#
# returns a list of bavarian ids
#
def get_bavarian_ids():
    with open("webapp/static/util/bavarian_ids.txt") as f:
        bavarian_ids = f.read().splitlines()
    f.close()
    return bavarian_ids

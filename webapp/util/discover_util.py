#
# get data entries depending on the traffic_type
#
from webapp.db_models import DailyData, MonthlyData

pipeline = [
    {
        "$group":
            {
                "_id": {
                    "$dateToString": {
                        "date": "$bucket",
                        "format": "%Y-%m-%d"
                    }
                },
                "count": {"$sum": 1}
            }
    }
]
TIME_SPANS = {
    0: '0-3',
    3: '3-6',
    6: '6-9',
    9: '9-12',
    12: '12-15',
    15: '15-18',
    18: '18-21',
    21: '21-24'
}


def get_time_list(time_begin, time_end):
    time_span = []
    time_begin = int(time_begin)
    time_end = int(time_end)
    for key in TIME_SPANS.keys():
        if time_begin <= key < time_end:
            time_span.append(TIME_SPANS.get(key))
    return time_span


def discovery_controller(inputs, index_start, index_end):
    query_operators = {}
    if inputs.start_name or inputs.end_name:
        if inputs.traffic_type == "Gesamtverkehr":
            query_operators = {"startName__contains": inputs.start_name,
                               "endName__contains": inputs.end_name}
        elif inputs.traffic_type == "Binnen-Verkehr":
            query_operators = {"startName__contains": inputs.start_name,
                               "endName__contains": inputs.start_name}
        elif inputs.traffic_type == "Outgoing-Verkehr":
            query_operators = {"startName__contains": inputs.start_name,
                               "endName__ne": inputs.start_name
                               }
        elif inputs.traffic_type == "Incoming-Verkehr":
            query_operators = {"endName__contains": inputs.end_name,
                               "startName__ne": inputs.end_name
                               }
    if inputs.start_date and inputs.end_date:
        query_operators["bucket__gte"] = inputs.start_date
        query_operators["bucket__lte"] = inputs.end_date

    if inputs.start_time and inputs.end_time:
        time_line = get_time_list(inputs.start_time, inputs.end_time)
        query_operators["daytime__in"] = time_line
    return run_query(inputs.dataset_type, query_operators, index_start, index_end)


def run_query(dataset_type, query_operators, index_start, index_end):
    global pipeline
    stripped_json = []
    keywords = []
    count = ''
    total = 0
    datasets = []
    if index_start > 0:
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators)[index_start:index_end].as_pymongo()
            total = DailyData.objects(**query_operators).count()
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators)[index_start:index_end].as_pymongo()
            total = MonthlyData.objects(**query_operators).count()
        count = {'from': index_start, 'to': index_end - 1, 'of': total}
        if datasets:
            for dataset in datasets:
                dataset.pop("_id")
                dataset['bucket'] = dataset['bucket'].strftime('%d.%m.%Y')
                stripped_json.append(dataset)
            if stripped_json:
                keywords = list(stripped_json[0])
    else:
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).only('bucket').as_pymongo().aggregate(pipeline)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).only('bucket').as_pymongo().aggregate(pipeline)
        stripped_json = list(datasets)
    return {'data': stripped_json, 'keys': keywords, 'index': count}

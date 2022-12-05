#
# get data entries depending on the traffic_type
#
from webapp.db_models import DailyData, MonthlyData, SavedCharts
from webapp.util.discover_util import get_time_list

#pipelines gruppieren bzw. aggregieren die Daten je nach Bedarf
# original
# pipeline_dat = [
#     {
#         "$group":
#             {
#                 "_id": {
#                     "$dateToString": {
#                         "date": "$bucket",
#                         "format": "%Y-%m-%d"
#                     }
#                 },
#                 "count": {"$sum": "$count"}
#             }
#     }
# ]
pipeline_dat = [
    {
        '$group': {
            '_id': {
                '$dateToString': {
                    'date': '$bucket',
                    'format': '%Y-%m-%d'
                }
            },
            'count': {
                '$sum': '$count'
            },
            'tripDistance': {
                '$sum': '$tripDistance'
            },
            # 'modeOfTransport': {
            #     '$sum': '$modeOfTransport'
            # }
        }
    }, {
        "$sort": {
            "_id": -1
        }
    }
]

pipeline_dat_trp = [
    {
        '$group': {
            '_id': {
                '$dateToString': {
                    'date': '$bucket',
                    'format': '%Y-%m-%d'
                }
            },
            'count': {
                '$sum': '$count'
            },
            'tripDistance': {
                '$sum': '$tripDistance'
            }
        },
        'modeOfTransport': {
            '$sum': '$modeOfTransport'
        }
    }, {
        "$sort": {
            "_id": -1
        }
    }
]

pipeline_trp = [
    {
        '$group': {
            '_id': '$modeOfTransport',
            'count': {'$sum': '$count'},
            'tripDistance': {'$sum': '$tripDistance'}
        }
    }, {
        "$sort": {
            "count": -1
        }
    }

]
pipeline_slk = [
    {
        '$group': {
            '_id': '$startName',
            'count': {'$sum': '$count'},
            'tripDistance': {'$sum': '$tripDistance'}
        }
    }, {
        "$sort": {
            "count": -1
        }
    }
]

pipeline_elk = [
    {
        '$group': {
            '_id': '$endName',
            'count': {'$sum': '$count'},
            'tripDistance': {'$sum': '$tripDistance'}
        }
    }, {
        "$sort": {
            "count": -1
        }
    }
]

pipeline_wtg = [
    {
        '$group': {
            '_id': '$weekday',
            'count': {'$sum': '$count'},
            'tripDistance': {'$sum': '$tripDistance'}
        }
    }, {
        "$sort": {
            "count": -1
        }
    }
]

pipeline_tgz = [
    {
        '$group': {
            '_id': '$daytime',
            'count': {'$sum': '$count'},
            'tripDistance': {'$sum': '$tripDistance'}
        }
    }, {
        "$sort": {
            "count": -1
        }
    }
]

pipeline_tds = [
    {
        '$group': {
            '_id': '$tripDistance',
            'count': {'$sum': '$count'},
            'tripDistance': {'$sum': '$tripDistance'}
        }
    }, {
        "$sort": {
            "_id": 1
        }
    }
]

#Abfrage der Auswahl und dementsprchende automatische Gruppierung der Daten (mittels Pipelines)

def chart_controller(inputs):
    query_operators = {}
    if inputs.lk_start or inputs.lk_end:
        if inputs.traffic == "Gesamtverkehr":
            query_operators = {"startName__contains": inputs.lk_start,
                               "endName__contains": inputs.lk_end}
        elif inputs.traffic == "Binnen-Verkehr":
            query_operators = {"startName__contains": inputs.lk_start,
                               "endName__contains": inputs.lk_start}
        elif inputs.traffic == "Outgoing-Verkehr":
            query_operators = {"startName__contains": inputs.lk_start,
                               "endName__ne": inputs.lk_start
                               }
        elif inputs.traffic == "Incoming-Verkehr":
            query_operators = {"endName__contains": inputs.lk_end,
                               "startName__ne": inputs.lk_end
                               }
    if inputs.start_date and inputs.end_date:
        query_operators["bucket__gte"] = inputs.start_date
        query_operators["bucket__lte"] = inputs.end_date

    if inputs.start_time and inputs.end_time:
        time_line = get_time_list(inputs.start_time, inputs.end_time)
        query_operators["daytime__in"] = time_line
    return run_query(inputs.dataset_type, inputs.type_of_chart, query_operators)


def run_query(dataset_type, type_of_chart, query_operators):
    global pipeline
    datasets = []

    group_by = ""
    # type_of_chart = type_of_chart.strip()
    # Abfangen von Auswahl des Charts und Zuordnung der entsprechenden Gruppierung
    print(type_of_chart)

    if type_of_chart == "Histogramm mit Datum und Anzahl":
        group_by = "Datum"
    elif type_of_chart == "Histogramm mit Datum und Anzahl_vertauscht":
        group_by = "Datum"
    elif type_of_chart == "Histogramm mit Datum und Anzahl_Slider":
        group_by = "Datum"
    elif type_of_chart == "Linien Diagramm mit Datum und Anzahl_Slider":
        group_by = "Datum"
    elif type_of_chart == "Linien Diagramm mit Datum und Distanz":
        group_by = "Datum"
    elif type_of_chart == "Tortendiagramm mit Datum und Anzahl":
        group_by = "Datum"
    elif type_of_chart == "Histogramm mit Start-Landkreis und Anzahl":
        group_by = "Landkreis Start"
    elif type_of_chart == "Histogramm mit Start-Landkreis und Anzahl_Top10":
        group_by = "Landkreis Start"
    elif type_of_chart == "Histogramm mit Start-Landkreis und Distanz":
        group_by = "Landkreis Start"
    elif type_of_chart == "Histogramm mit End-Landkreis und Anzahl":
        group_by = "Landkreis Ende"
    elif type_of_chart == "Histogramm mit End-Landkreis und Anzahl_Top10":
        group_by = "Landkreis Ende"
    elif type_of_chart == "Histogramm mit Transportmittel und Anzahl":
        group_by = "Transportmittel"
    elif type_of_chart == "Histogramm mit Transportmittel und Distanz":
        group_by = "Transportmittel"
    elif type_of_chart == "Tortendiagramm mit Transportmittel und Anzahl (anteilig)":
        group_by = "Transportmittel"
    elif type_of_chart == "Histogramm mit Wochentag und Anzahl":
        group_by = "Wochentag"
    elif type_of_chart == "Tortendiagramm mit Wochentagen und Anzahl (anteilig)":
        group_by = "Wochentag"
    elif type_of_chart == "Histogramm mit Tageszeit und Anzahl":
        group_by = "Tageszeit"
    elif type_of_chart == "Liniendiagramm mit Tageszeit und Anzahl":
        group_by = "Tageszeit"
    elif type_of_chart == "Liniendiagramm mit Distanz und Anzahl_ungruppiert":
        group_by = "Distanz"
    elif type_of_chart == "Histogramm mit Distanz und Anzahl_ungruppiert":
        group_by = "Distanz"
    elif type_of_chart == "Histogramm mit Distanz und Anzahl_gruppiert":
        group_by = "Distanz"
    elif type_of_chart == "Liniendiagramm mit Distanz und Anzahl_gruppiert":
        group_by = "Distanz"

    else:
        print("Chart nicht erkannt")

    # modifiziert für Vorhersage
    if group_by == "Datum":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_dat)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_dat)
    # passe diese Abfragen an, damit andere Daten verwendet werden --> ergänze analog dazu andere Abfragen
        elif dataset_type == "Vorhersage: Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_dat)
        elif dataset_type == "Vorhersage: Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_dat)
        datasets = list(datasets)
    elif group_by == "Transportmittel":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_trp)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_trp)
        datasets = list(datasets)
    elif group_by == "Landkreis Start":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_slk)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_slk)
        datasets = list(datasets)
    elif group_by == "Landkreis Ende":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_elk)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_elk)
        datasets = list(datasets)
    elif group_by == "Wochentag":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_wtg)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_wtg)
        datasets = list(datasets)
    elif group_by == "Tageszeit":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_tgz)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_tgz)
        datasets = list(datasets)
    elif group_by == "Distanz":
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo().aggregate(pipeline_tds)
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo().aggregate(pipeline_tds)
        datasets = list(datasets)

    else:
        if dataset_type == "Täglicher Datensatz":
            datasets = DailyData.objects(**query_operators).as_pymongo()
        elif dataset_type == "Monatlicher Datensatz":
            datasets = MonthlyData.objects(**query_operators).as_pymongo()
    return datasets


#
# sets the form fields with the given parameters
#
def set_chart_filter_fields(filter_form, graph_id):
    import json
    from datetime import datetime
    inputs = json.loads(SavedCharts.objects(_id=graph_id).values_list("input").as_pymongo()[0])

    filter_form.traffic_type.data = inputs["traffic"]
    filter_form.dataset_type.data = inputs["dataset_type"]
    filter_form.group_by.data = inputs["grp_by"]
    filter_form.x_axis.data = inputs["x"]
    filter_form.y_axis.data = inputs["y"]
    filter_form.district_start.data = inputs["lk_start"]
    filter_form.district_end.data = inputs["lk_end"]
    if inputs["start_date"] and inputs["end_date"]:
        filter_form.start_date.data = datetime.strptime(inputs["start_date"], "%Y-%m-%d")
        filter_form.end_date.data = datetime.strptime(inputs["end_date"], "%Y-%m-%d")
    filter_form.start_time.data = inputs["start_time"]
    filter_form.end_time.data = inputs["end_time"]
    filter_form.start_date_compare.data = inputs["start_date_compare"]
    filter_form.end_date_compare.data = inputs["end_date_compare"]
    filter_form.district_compare.data = inputs["district_compare"]
    filter_form.type_of_chart.data = inputs["type_of_chart"]

import json
import os

from flask import Blueprint, render_template, request
from flask_login import login_required

from webapp.db_models import SavedMaps, SavedCharts, Dashboards
from webapp.forms.charts_form import FilterFormCharts
from webapp.forms.maps_form import FilterFormMaps

graph_to_db = Blueprint("graph_to_db", __name__, template_folder="templates")


@login_required
@graph_to_db.route('/graph_to_db', methods=["GET", "POST"])
def save_graph_to_db():
    graph_json = json.loads(str(request.get_data(), "utf-8"))
    if "graph_id" not in graph_json:
        _id = SavedMaps.objects.count() + 1
        # ensure unique id
        while SavedMaps.objects(_id=_id).all().as_pymongo():
            _id += 1
    else:
        _id = graph_json["graph_id"]

    # set an autogenerated title depending on the input fields
    if not graph_json["title"]:
        inputs = json.loads(graph_json["input"])
        # no compare graph
        if not inputs["start_date_compare"] and not inputs["end_date_compare"]:
            graph_json["title"] = inputs["traffic_type"] + " " + inputs["start_date"] + ", " + inputs["end_date"]
        # compare graph
        else:
            graph_json["title"] = "Vergleich des " + inputs["traffic_type"] + "s " + "zwischen \n" + \
                                  inputs["start_date"] + ", " + inputs["end_date"] + " und " \
                                  + inputs["start_date_compare"] + ", " + inputs["end_date_compare"]

    save_graph = SavedMaps(
        _id=_id,
        data=graph_json["graph"],
        title=graph_json["title"],
        input=graph_json["input"],
        visible=True,
        favorite=json.dumps({
            "text": "",
            "is_favorite": False
        })
    )
    save_graph.save()

    return render_template("maps.html", graph={}, form=FilterFormMaps(), is_new_graph=False)


@login_required
@graph_to_db.route('/chart_to_db', methods=["GET", "POST"])
def save_chart_to_db():
    graph_json = json.loads(str(request.get_data(), "utf-8"))
    if "graph_id" not in graph_json:
        _id = SavedCharts.objects.count() + 1
        # ensure unique id
        while SavedCharts.objects(_id=_id).all().as_pymongo():
            _id += 1
    else:
        _id = graph_json["graph_id"]

    # set an autogenerated title depending on the input fields
    if not graph_json["title"]:
        inputs = json.loads(graph_json["input"])
        graph_json["title"] = inputs["traffic"] + " " + inputs["start_date"] + ", " + inputs["end_date"]


    save_chart = SavedCharts(
        _id=_id,
        data=graph_json["graph"],
        title=graph_json["title"],
        input=graph_json["input"],
        visible=True,
        favorite=json.dumps({
            "text": "",
            "is_favorite": False
        })
    )
    save_chart.save()
    return render_template("charts.html", graph={}, form=FilterFormCharts(), is_new_graph=False, is_image=False)


@login_required
@graph_to_db.route('/dashboard_to_db', methods=["GET", "POST"])
def save_dashboard_to_db():
    _id = Dashboards.objects.count() + 1
    # ensure unique id
    while Dashboards.objects(_id=_id).all().as_pymongo():
        _id += 1

    graph_json = json.loads(str(request.get_data(), "utf-8"))
    # check if any field is not set in dashboard
    if "1" not in graph_json:
        graph_json["1"]["id"] = None
        graph_json["1"]["type"] = None
    if "2" not in graph_json:
        graph_json["2"]["id"] = None
        graph_json["2"]["type"] = None
    if "3" not in graph_json:
        graph_json["3"]["id"] = None
        graph_json["3"]["type"] = None

    # create new dashboard
    new_dashboard = Dashboards(
        _id=_id,
        first_entry=graph_json["1"]["id"],
        first_entry_type=graph_json["1"]["type"],
        second_entry=graph_json["2"]["id"],
        second_entry_type=graph_json["2"]["type"],
        third_entry=graph_json["3"]["id"],
        third_entry_type=graph_json["3"]["type"],
        text=graph_json["text"]
    )
    new_dashboard.save()
    return render_template("create_dashboard.html", map_ids=[], chart_ids=[], charts=[], graphs=[])
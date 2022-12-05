import ast
import json

from flask import Blueprint, request
from flask.templating import render_template
from flask_login import login_required

from webapp.db_models import SavedMaps, GraphOrder, Dashboards, SavedCharts
from webapp.util.modify_data import convert_booleans_in_saved_graph

main = Blueprint("main", __name__, template_folder="templates")


@login_required
@main.route('/dashboard/create')
def create_dashboards():
    maps = []
    charts = []
    dashboards = []

    # set the order defined in GraphOrder
    map_order = ast.literal_eval(GraphOrder.objects().all().as_pymongo()[0]["map_order"])
    chart_order = ast.literal_eval(GraphOrder.objects().all().as_pymongo()[0]["chart_order"])
    for graph_id in map_order:
        if json.loads(SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["favorite"])["is_favorite"]:
            maps.append(SavedMaps.objects(_id=graph_id).all().as_pymongo()[0])
    for graph_id in chart_order:
        if json.loads(SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["favorite"])["is_favorite"]:
            charts.append(SavedCharts.objects(_id=graph_id).all().as_pymongo()[0])

    # convert python boolean to string to make it readable for js
    maps_modified = convert_booleans_in_saved_graph(maps)
    charts_modified = convert_booleans_in_saved_graph(charts)
    # get all ids and give it to html
    map_ids = []
    chart_ids = []
    for entry in maps:
        map_ids.append(entry["_id"])
    for entry in charts:
        chart_ids.append(entry["_id"])

    return render_template("create_dashboard.html", map_ids=map_ids, chart_ids=chart_ids, charts=charts_modified,
                           graphs=maps_modified, dashboards=dashboards)


@main.route('/')
def display_dashboards():
    dashboards = []
    dashboards_order = Dashboards.objects().all().as_pymongo()
    for dashboard in dashboards_order:
        if "first_entry" in dashboard:
            graph_id = dashboard["first_entry"]
            if dashboard["first_entry_type"] == "map":
                dashboard["first_entry"] = SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["data"]
                dashboard["first_entry_title"] = SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["title"]
            else:
                dashboard["first_entry"] = SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["data"]
                dashboard["first_entry_title"] = SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["title"]
        if "second_entry" in dashboard:
            graph_id = dashboard["second_entry"]
            if dashboard["second_entry_type"] == "map":
                dashboard["second_entry"] = SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["data"]
                dashboard["second_entry_title"] = SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["title"]
            else:
                dashboard["second_entry"] = SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["data"]
                dashboard["second_entry_title"] = SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["title"]
        if "third_entry" in dashboard:
            graph_id = dashboard["third_entry"]
            if dashboard["third_entry_type"] == "map":
                dashboard["third_entry"] = SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["data"]
                dashboard["third_entry_title"] = SavedMaps.objects(_id=graph_id).all().as_pymongo()[0]["title"]
            else:
                dashboard["third_entry"] = SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["data"]
                dashboard["third_entry_title"] = SavedCharts.objects(_id=graph_id).all().as_pymongo()[0]["title"]
        dashboards.append(dashboard)
    return render_template("display_dashboards.html", dashboards=dashboards)


@login_required
@main.route('/dashboard/create/reorder', methods=["GET", "POST"])
def reorder_graphs():
    graphs = []
    map_ids = []
    chart_ids = []
    charts = []
    reordered_list = json.loads(str(request.get_data(), "utf-8"))
    if reordered_list["type"] == "map":
        GraphOrder.objects().update(set__map_order=reordered_list["list"])
    elif reordered_list["type"] == "chart":
        GraphOrder.objects().update(set__chart_order=reordered_list["list"])

    return render_template("create_dashboard.html", map_ids=map_ids, chart_ids=chart_ids, charts=charts, graphs=graphs)

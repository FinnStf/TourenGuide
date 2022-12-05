import ast
import json

from flask import Blueprint, render_template, request
from flask_login import login_required
from mongoengine import Q

from webapp.db_models import SavedMaps, GraphOrder, Dashboards, SavedCharts

modify_graph = Blueprint("modify_graph", __name__, template_folder="templates")


@login_required
@modify_graph.route('/modify_map', methods=["GET", "POST"])
def modify_db_map():
    graph_id = json.loads(str(request.get_data(), "utf-8"))

    # if delete button was pressed: delete entry with that id
    if graph_id["method"] == "delete":
        # if graph to be deleted is part of a dashboard: question delete request
        for dashboard in Dashboards.objects().all().as_pymongo():
            if graph_id["id"] in dashboard.values():
                return "true"

        SavedMaps.objects(_id=graph_id["id"]).delete()
        # if deleted graph in order on homescreen: delete it there aswell
        if GraphOrder.objects(map_order__contains=str(graph_id["id"])):
            remove_graph_from_order("map", graph_id["id"])

    # if visible button was pressed: set the other boolean value as visible value
    elif graph_id["method"] == "visible":
        if SavedMaps.objects(_id=graph_id["id"]).values_list("visible")[0]:
            SavedMaps.objects(_id=graph_id["id"]).update(set__visible=False)
        else:
            SavedMaps.objects(_id=graph_id["id"]).update(set__visible=True)

    # if favorite button was pressed: set the other boolean value as favorite value
    elif graph_id["method"] == "favorite":
        favorite = json.loads(SavedMaps.objects(_id=graph_id["id"]).values_list("favorite")[0])
        if favorite["is_favorite"]:
            favorite["is_favorite"] = False
            if GraphOrder.objects(map_order__contains=str(graph_id["id"])):
                remove_graph_from_order("map", graph_id["id"])
        else:
            favorite["is_favorite"] = True
            add_graph_to_order("map", graph_id["id"])

        favorite = json.dumps(favorite)
        SavedMaps.objects(_id=graph_id["id"]).update(set__favorite=favorite)

    # if text was added to favorite: set the text into the favorite json
    elif graph_id["method"] == "add_text_favorite":
        if graph_id["text"]:
            favorite = json.loads(SavedMaps.objects(_id=graph_id["id"]).values_list("favorite")[0])
            favorite["text"] = graph_id["text"]
            favorite = json.dumps(favorite)
            SavedMaps.objects(_id=graph_id["id"]).update(set__favorite=favorite)

    return render_template("display_maps.html")


@login_required
@modify_graph.route('/modify_chart', methods=["GET", "POST"])
def modify_db_chart():
    graph_id = json.loads(str(request.get_data(), "utf-8"))

    # if delete button was pressed: delete entry with that id
    if graph_id["method"] == "delete":
        # if graph to be deleted is part of a dashboard: question delete request
        for dashboard in Dashboards.objects().all().as_pymongo():
            if graph_id["id"] in dashboard.values():
                return "true"

        SavedCharts.objects(_id=graph_id["id"]).delete()
        # if deleted graph in order on homescreen: delete it there aswell
        if GraphOrder.objects(chart_order__contains=str(graph_id["id"])):
            remove_graph_from_order("chart", graph_id["id"])

    # if visible button was pressed: set the other boolean value as visible value
    elif graph_id["method"] == "visible":
        if SavedCharts.objects(_id=graph_id["id"]).values_list("visible")[0]:
            SavedCharts.objects(_id=graph_id["id"]).update(set__visible=False)
        else:
            SavedCharts.objects(_id=graph_id["id"]).update(set__visible=True)

        # if favorite button was pressed: set the other boolean value as favorite value
    elif graph_id["method"] == "favorite":
        favorite = json.loads(SavedCharts.objects(_id=graph_id["id"]).values_list("favorite")[0])
        if favorite["is_favorite"]:
            favorite["is_favorite"] = False
            if GraphOrder.objects(chart_order__contains=str(graph_id["id"])):
                remove_graph_from_order("chart", graph_id["id"])
        else:
            favorite["is_favorite"] = True
            add_graph_to_order("chart", graph_id["id"])

        favorite = json.dumps(favorite)
        SavedCharts.objects(_id=graph_id["id"]).update(set__favorite=favorite)

    # if text was added to favorite: set the text into the favorite json
    elif graph_id["method"] == "add_text_favorite":
        if graph_id["text"]:
            favorite = json.loads(SavedCharts.objects(_id=graph_id["id"]).values_list("favorite")[0])
            favorite["text"] = graph_id["text"]
            favorite = json.dumps(favorite)
            SavedCharts.objects(_id=graph_id["id"]).update(set__favorite=favorite)

    return render_template("display_charts.html")


#
# adds the id of a favorized graph to the order list
#
def add_graph_to_order(type_of_graph, graph_id):
    insert = {}
    order = ast.literal_eval(GraphOrder.objects().all().as_pymongo()[0][type_of_graph+"_order"])
    order.append(graph_id)
    new_order = str(order)
    insert["set__"+type_of_graph+"_order"] = new_order
    for entry in GraphOrder.objects():
        entry.update(**insert)


#
# removes the id of a favorized graph from the order list
#
def remove_graph_from_order(type_of_graph, graph_id):
    remove = {}
    order = ast.literal_eval(GraphOrder.objects().all().as_pymongo()[0][type_of_graph+"_order"])
    order.remove(graph_id)
    new_order = str(order)
    remove["set__"+type_of_graph+"_order"] = new_order
    for entry in GraphOrder.objects():
        entry.update(**remove)


#
# delete graph although it is in a dashboard
#
@login_required
@modify_graph.route('/delete_graph', methods=["GET", "POST"])
def confirm_graph_delete():
    graph_id = str(request.get_data(), "utf-8")

    SavedMaps.objects(_id=graph_id).delete()
    # if deleted graph in order on homescreen: delete it there aswell
    if GraphOrder.objects(map_order__contains=graph_id):
        remove_graph_from_order(int(graph_id))
    # delete the dashboard that contains the graph aswell
    Dashboards.objects().filter(
        Q(first_entry__contains=graph_id) |
        Q(second_entry__contains=graph_id) |
        Q(third_entry__contains=graph_id)).delete()
    return render_template("display_maps.html")


#
# delete chart although it is in a dashboard
#
@login_required
@modify_graph.route('/delete_chart', methods=["GET", "POST"])
def confirm_chart_delete():
    graph_id = str(request.get_data(), "utf-8")

    SavedCharts.objects(_id=graph_id).delete()
    # if deleted graph in order on homescreen: delete it there aswell
    if GraphOrder.objects(chart_order__contains=graph_id):
        remove_graph_from_order(int(graph_id))
    # delete the dashboard that contains the graph aswell
    Dashboards.objects().filter(
        Q(first_entry__contains=graph_id) |
        Q(second_entry__contains=graph_id) |
        Q(third_entry__contains=graph_id)).delete()
    return render_template("display_charts.html")


@login_required
@modify_graph.route('/delete_dashboard', methods=["GET", "POST"])
def delete_dashboard():
    dashboard_id = str(request.get_data(), "utf-8")
    Dashboards.objects(_id=dashboard_id).delete()

    return render_template("display_dashboards.html")

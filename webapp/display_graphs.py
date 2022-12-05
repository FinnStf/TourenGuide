from flask import Blueprint, render_template

from webapp.db_models import SavedMaps, SavedCharts
from webapp.util.modify_data import convert_booleans_in_saved_graph

display_graphs = Blueprint("display_graphs", __name__, template_folder="templates")


#
# display all the maps from the database
#
@display_graphs.route('/display_maps', methods=["GET", "POST"])
def show_maps():

    graphs = SavedMaps.objects().all().as_pymongo()

    # convert python boolean to string to make it readable for js
    graphs_modified = convert_booleans_in_saved_graph(graphs)

    return render_template("display_maps.html", graphs=graphs_modified)


@display_graphs.route('/display_charts', methods=["GET", "POST"])
def show_charts():

    # Todo anpassen; sollte irgendwie so in etwa aussehen
    # graphs_stripped = []
    # graphs = SavedCharts.objects().all().as_pymongo()
    # for graph in graphs:
    #     if graph["visible"]:
    #         graph["visible"] = "true"
    #     else:
    #         graph["visible"] = "false"
    #     graphs_stripped.append(graph)

    charts = SavedCharts.objects().all().as_pymongo()

    # convert python boolean to string to make it readable for js
    charts_modified = convert_booleans_in_saved_graph(charts)

    return render_template("display_charts.html", graphs=charts_modified)

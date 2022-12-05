import json

import plotly
from flask import Blueprint, flash
from flask.templating import render_template
from flask_login import login_required

from webapp.db_models import SavedMaps
from webapp.forms.maps_form import FilterFormMaps
from webapp.util.maps_util import set_filter_fields, traffic_controller, calc_compare_graph

maps = Blueprint("maps", __name__, template_folder="templates")


class Filters:
    def __init__(self,
                 start_date,
                 end_date,
                 traffic_type,
                 dataset_type,
                 start_date_compare,
                 end_date_compare,
                 proportion_unit,
                 reverse_colorscale):
        self.start_date = start_date
        self.end_date = end_date
        self.traffic_type = traffic_type
        self.dataset_type = dataset_type
        self.start_date_compare = start_date_compare
        self.end_date_compare = end_date_compare
        self.proportion_unit = proportion_unit
        self.reverse_colorscale = reverse_colorscale


#
# return parameters: graph_json = newly created graph,
#                    form = the form of the filters,
#                    is_new_graph = boolean to decide whether graph was newly created or just edited
#
@maps.route('/maps', methods=["GET", "POST"])
@login_required
def create_maps():
    filter_form = FilterFormMaps()
    is_new_graph = False
    with open("webapp/static/util/map_without_data.json", encoding="utf-8") as f:
        graph_json = f.read()

    # if user has (probably) set some filters and clicked submit
    if filter_form.is_submitted():
        inputs = Filters(filter_form.start_date.data,
                         filter_form.end_date.data,
                         filter_form.traffic_type.data,
                         filter_form.dataset_type.data,
                         filter_form.start_date_compare.data,
                         filter_form.end_date_compare.data,
                         filter_form.proportion_unit.data,
                         filter_form.reverse_colorscale.data)

        # get the traffic depending on traffic type, dataset type and time range
        traffic = traffic_controller(inputs.traffic_type, inputs.dataset_type, inputs.start_date, inputs.end_date)
        # if user wants to create a compare map
        if inputs.start_date_compare and inputs.end_date_compare:
            traffic = calc_compare_graph(inputs, traffic)

        if not traffic:
            flash("Unzureichende Filter ausgewählt!", "danger")
        else:
            # reverse color scale by using _r-suffix if box was checked
            color_scale = filter_form.color_scale.data
            if inputs.reverse_colorscale:
                color_scale += "_r"
            # create the graph
            graph_json = create_choropleth(traffic,
                                           color_scale,
                                           filter_form.upper_range_color.data,
                                           filter_form.lower_range_color.data,
                                           inputs.proportion_unit)

            is_new_graph = True

    return render_template("maps.html", graph=graph_json, form=filter_form, is_new_graph=is_new_graph)


#
# fills the form fields with the saved values from the database to ensure that user can continue from when he saved
#
@maps.route('/maps/<graph_id>', methods=["GET", "POST"])
@login_required
def edit_map(graph_id):
    filter_form = FilterFormMaps()
    is_new_graph = False
    graph_json = {}

    if not filter_form.is_submitted():
        graph_json = SavedMaps.objects(_id=graph_id).values_list("data").as_pymongo()[0]
        set_filter_fields(filter_form, graph_id)

    if filter_form.is_submitted():
        inputs = Filters(filter_form.start_date.data,
                         filter_form.end_date.data,
                         filter_form.traffic_type.data,
                         filter_form.dataset_type.data,
                         filter_form.start_date_compare.data,
                         filter_form.end_date_compare.data,
                         filter_form.proportion_unit.data,
                         filter_form.reverse_colorscale.data)

        # get normal traffic data
        traffic = traffic_controller(inputs.traffic_type, inputs.dataset_type, inputs.start_date, inputs.end_date)
        # if fields for compare graph are set: get compare traffic data
        if inputs.start_date_compare and inputs.end_date_compare:
            traffic = calc_compare_graph(inputs, traffic)

        # if list is empty
        if not traffic:
            flash("Unzureichende Filter ausgewählt!", "danger")
        else:
            # reverse color scale by using _r-suffix if box was checked
            color_scale = filter_form.color_scale.data
            if inputs.reverse_colorscale:
                color_scale += "_r"
            # create the graph and the dataframe
            graph_json = create_choropleth(traffic,
                                           color_scale,
                                           filter_form.upper_range_color.data,
                                           filter_form.lower_range_color.data,
                                           inputs.proportion_unit)

            is_new_graph = True

    return render_template("maps.html", graph=graph_json, form=filter_form, is_new_graph=is_new_graph)


#
# create a choropleth map
# return value is the json of the created map
#
def create_choropleth(traffic, color_scale, upper_range_color, lower_range_color, proportion_unit):
    if proportion_unit == "Prozentuale Zahlen":
        labels = {'count': 'Veränderung in Prozent', 'startName': 'Landkreis'}
        hovertemplate = "<br>".join([
            "Name: %{customdata[0]}",
            "Veränderung: %{customdata[1]}%"
        ])
    else:
        labels = {'count': 'Anzahl', 'startName': 'Landkreis'}
        hovertemplate = "<br>".join([
            "Name: %{customdata[0]}",
            "Anzahl: %{customdata[1]}"
        ])

    with open('webapp/static/util/geodata_bavaria.json') as response:
        districts = json.load(response)

    import pandas as pd
    df = pd.DataFrame.from_dict(traffic)

    df.to_csv('webapp/outputs/saved_csv.csv', sep=",", index=False, encoding='utf-8')

    import plotly.express as px
    fig = px.choropleth(df,
                        geojson=districts,
                        locations='id',
                        color='count',
                        hover_name='name',
                        color_continuous_scale=color_scale,
                        range_color=(lower_range_color, upper_range_color),
                        scope="europe",
                        labels=labels,
                        custom_data=['name', 'count']
                        )

    # do not show the borders of the rest of germany/the world
    # zoom in to bavaria/germany/our defined important spots
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@maps.route('/csv_download')
def plot_csv():
    from flask import send_file

    return send_file('outputs/saved_csv.csv',
                     mimetype='text/csv',
                     attachment_filename='CSV-Download.csv',
                     as_attachment=True)

from flask import Blueprint, render_template, flash, jsonify
from flask_login import login_required
from webapp.forms.discover_form import FilterForm
from webapp.util.discover_util import discovery_controller
import json
import plotly

discover = Blueprint("discover", __name__,
                     template_folder="templates")


class DiscoverFilter:
    def __init__(self,
                 dataset_type,
                 start_date,
                 end_date,
                 start_time,
                 end_time,
                 start_name,
                 end_name,
                 traffic_type):
        self.dataset_type = dataset_type
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.start_name = start_name
        self.end_name = end_name
        self.traffic_type = traffic_type

# fill table & graph relevant fields for first load of page
inputs = DiscoverFilter("Monatlicher Datensatz",
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        "Gesamtverkehr"
                        )
page = 1
dataset_title = "Monatlicher Datensatz"


#
#   route responsible for collection user input and generating corresponding data queries
#   return parameters: datasets==Table Data, keywords==Column Names of Table,
#                            form==data_filter_form, pagination==Index of which part of table data is shown,
#                            graph= Plotly graph in json format
#
@discover.route("/discover", methods=["GET", "POST"])
@login_required
def discover_data():
    global dataset_title
    global inputs
    global page
    data_filter_form = FilterForm()
    keywords = []
    datasets = []
    index = ''
    graph_json = []
    if data_filter_form.is_submitted():
        dataset_title = data_filter_form.dataset_type.data
        page = 1
        if data_filter_form.dataset_type.data == 'Monatlicher Datensatz':
            inputs = DiscoverFilter(data_filter_form.dataset_type.data,
                                    data_filter_form.startDate.data,
                                    data_filter_form.endDate.data,
                                    data_filter_form.startTime.data,
                                    data_filter_form.endTime.data,
                                    data_filter_form.startName.data,
                                    data_filter_form.endName.data,
                                    data_filter_form.traffic_type.data
                                    )
        else:
            inputs = DiscoverFilter(data_filter_form.dataset_type.data,
                                    data_filter_form.startDate.data,
                                    data_filter_form.endDate.data,
                                    None, None,
                                    data_filter_form.startName.data,
                                    data_filter_form.endName.data,
                                    data_filter_form.traffic_type.data
                                    )
    else:
        graph_json = create_timeseries_chart(discovery_controller(inputs, -1, -1)["data"])
    if inputs is not None:
        data_response = discovery_controller(inputs, page * 20 - 19, page * 20 + 1)
        graph_json = create_timeseries_chart(discovery_controller(inputs, -1, -1)["data"])
        if data_response and graph_json:
            datasets = data_response['data']
            index = data_response['index']
            keywords = data_response['keys']
        else:
            flash("Keine passenden Einträge gefunden! Bitte andere Suchparameter eingeben", "danger")
    return render_template("discover.html", datasets=datasets, keywords=keywords,
                           form=data_filter_form, pagination=index, graph=graph_json)


#
# reloads Data for corresponding page
#
@discover.route("/_get_next_data_page/<int:change>", methods=["GET", "POST"])
@login_required
def _get_next_data_page(change):
    global page
    if change == 0:
        if page > 1:
            page -= 1
        else:
            return jsonify('')
    else:
        page += 1
    if inputs is not None:
        data_response = discovery_controller(inputs, page * 20 - 19, page * 20 + 1)
        return jsonify(data_response)


#
# create a timeseries chart
# return value is the json of the created map
#
def create_timeseries_chart(data):
    global dataset_title
    if data:
        labels = {'count': 'Anzahl Einträge', '_id': 'Datum'}
        import pandas as pd
        df = pd.DataFrame.from_dict(data)

        import plotly.express as px
        fig = px.bar(df, x=df['_id'], y=df['count'],
                     labels=labels
                     )
        fig.update_layout(title_text=dataset_title,
                          title_font_size=30,
                          yaxis_title="",
                          xaxis_title="")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        return []

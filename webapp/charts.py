import json
import os

import plotly
from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required

from webapp.db_models import SavedCharts
from webapp.forms.charts_form import FilterFormCharts
from webapp.util.chart_util import chart_controller, set_chart_filter_fields

charts = Blueprint("charts", __name__, template_folder="templates")


# Übernahme Eingaben Website
class ChartFilter:
    def __init__(self,
                 traffic,
                 dataset_type,
                 grp_by,
                 x1,
                 y1,
                 lk_start,
                 lk_end,
                 start_date,
                 end_date,
                 start_time,
                 end_time,
                 start_date_compare,
                 end_date_compare,
                 district_compare,
                 type_of_chart
                 ):
        self.traffic = traffic
        self.dataset_type = dataset_type
        self.grp_by = grp_by
        self.x1 = x1
        self.y1 = y1
        self.lk_start = lk_start
        self.lk_end = lk_end
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.start_date_compare = start_date_compare
        self.end_date_compare = end_date_compare
        self.district_compare = district_compare
        self.type_of_chart = type_of_chart


@charts.route('/charts', methods=["GET", "POST"])
@login_required
def create_charts():
    filter_form = FilterFormCharts()
    graph_json = os.path.join('static', 'image', 'empty_graph.png')
    is_new_graph = False
    is_image = True
    if filter_form.is_submitted():
        inputs = ChartFilter(filter_form.traffic_type.data,
                             filter_form.dataset_type.data,
                             filter_form.group_by.data,
                             filter_form.x_axis.data,
                             filter_form.y_axis.data,
                             filter_form.district_start.data,
                             filter_form.district_end.data,
                             filter_form.start_date.data,
                             filter_form.end_date.data,
                             filter_form.start_time.data,
                             filter_form.end_time.data,
                             filter_form.start_date_compare.data,
                             filter_form.end_date_compare.data,
                             filter_form.district_compare.data,
                             filter_form.type_of_chart.data)

        graph_json = create_chart(chart_controller(inputs), inputs)
        is_new_graph = True
        is_image = False
    return render_template("charts.html", form=filter_form, graph=graph_json, is_new_graph=is_new_graph,
                           is_image=is_image)


#
# fills the form fields with the saved values from the database to ensure that user can continue from when he saved
#
@charts.route('/charts/<chart_id>', methods=["GET", "POST"])
@login_required
def edit_chart(chart_id):
    filter_form = FilterFormCharts()
    is_new_graph = False
    graph_json = {}

    if not filter_form.is_submitted():
        graph_json = SavedCharts.objects(_id=chart_id).values_list("data").as_pymongo()[0]
        set_chart_filter_fields(filter_form, chart_id)

    if filter_form.is_submitted():
        inputs = ChartFilter(filter_form.traffic_type.data,
                             filter_form.dataset_type.data,
                             filter_form.group_by.data,
                             filter_form.x_axis.data,
                             filter_form.y_axis.data,
                             filter_form.district_start.data,
                             filter_form.district_end.data,
                             filter_form.start_date.data,
                             filter_form.end_date.data,
                             filter_form.start_time.data,
                             filter_form.end_time.data,
                             filter_form.start_date_compare.data,
                             filter_form.end_date_compare.data,
                             filter_form.district_compare.data,
                             filter_form.type_of_chart.data)

        graph_json = create_chart(chart_controller(inputs), inputs)
        is_new_graph = True

    return render_template("charts.html", form=filter_form, graph=graph_json, is_new_graph=is_new_graph,
                           is_image=False)


#
# create a chart
# return value is the json of the created chart
#
def create_chart(data, inputs):
    import pandas as pd
    df = pd.DataFrame.from_dict(data)
    import plotly.express as px
    df = df.dropna()
    print(df.head())

    # Abfangen möglicher Chart-Typen und daraus resultierend Erstellung von plotly Graph

    # if inputs.dataset_type == Vorhersage... für den Fall, dass Vorhersagedaten genutzt werden
    # Generierung und Implementierung dieser Daten noch offen (Kai)

    if inputs.type_of_chart == "Histogramm mit Transportmittel und Anzahl":
        df = df[df._id != "Not Classified"]
        df = df[df._id != "Unbekannt"]
        df = df[df._id != "None"]
        # df = df.reindex([1, 3, 0])
        print(df.head())
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Transportmittel")
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Transportmittel und Distanz":
        df = df[df._id != "Not Classified"]
        df = df[df._id != "Unbekannt"]
        # df = df.reindex([0, 3, 1])
        # print(df.head())
        fig = px.bar(df, x=df['_id'], y=df['tripDistance'])
        fig.update_layout(yaxis_title="Distanz (km)",
                          xaxis_title="Transportmittel")
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Linien Diagramm mit Datum und Distanz":
        fig = px.line(df, x=df['_id'], y=df['tripDistance'])
        fig.update_layout(yaxis_title="Distanz (km)",
                          xaxis_title="Datum")
        fig.update_traces(mode='lines+markers')
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(line_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(line_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Start-Landkreis und Anzahl":
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Start Landkreis")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Start-Landkreis und Anzahl_Top10":
        fig = px.bar(df, x=df[:10]['_id'], y=df[:10]['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Start Landkreis")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    # Falls genutzt: Neue Pipeline, Sortieren nach Distanz, statt Count
    elif inputs.type_of_chart == "Histogramm mit Start-Landkreis und Distanz":
        fig = px.bar(df, x=df['_id'], y=df['tripDistance'])
        fig.update_layout(yaxis_title="Distanz (km)",
                          xaxis_title="Start Landkreis")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit End-Landkreis und Anzahl":
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="End Landkreis")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit End-Landkreis und Anzahl_Top10":
        fig = px.bar(df, x=df[:10]['_id'], y=df[:10]['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="End Landkreis")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Datum und Anzahl_Slider":
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Datum")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Datum und Anzahl":
        print(inputs.dataset_type)
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Datum")
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Datum und Anzahl_vertauscht":
        fig = px.bar(df, x=df['count'], y=df['_id'])
        fig.update_layout(yaxis_title="Datum",
                          xaxis_title="Anzahl")
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    if inputs.type_of_chart == "Linien Diagramm mit Datum und Anzahl_Slider":
        fig = px.line(df, x=df['_id'], y=df['count'],
                      # hover_data = {"_id": "|%B %d, %Y"}
                      )
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Datum")
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_traces(mode='lines+markers')
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(line_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(line_color='#DAA520')


    # ToDo Ergänzen von alternativen Farben für Vorhersage (Kai)
    elif inputs.type_of_chart == "Tortendiagramm mit Datum und Anzahl":
        df = df.sort_values(by=['_id'], ascending=False)
        print(df.head())
        fig = px.pie(df, values='count', names='_id', color_discrete_sequence=px.colors.sequential.Blues)
        #                  #categoryorder='category ascending')
        #
        # Alternative, mit Werten innen
        # fig.update_traces(textposition='inside', textinfo='percent+label')

    # ToDo Ergänzen analog
    elif inputs.type_of_chart == "Tortendiagramm mit Transportmittel und Anzahl (anteilig)":
        df = df[df._id != "Not Classified"]
        df = df[df._id != "Unbekannt"]
        # df = df.dropna()
        print(df.head())
        fig = px.pie(df, values='count', names='_id',
                     color_discrete_sequence=["DodgerBlue", "RoyalBlue", "DeepSkyBlue"])
        # Alternative, mit Werten innen
        fig.update_traces(textposition='inside', textinfo='percent+label')


    # ToDo Vorhersage Farben für Wochentage/Wochenende festlegen analog Rest
    elif inputs.type_of_chart == "Histogramm mit Wochentag und Anzahl":
        print(df.head(10))
        # custom_dict = {'Mo': 0, 'Di': 1, 'Mi': 3}
        # df = df.reindex([4, 3, 2, 1, 0, 5, 6])
        custom_dict = {'Mo': 0, 'Di': 1, 'Mi': 2, 'Do': 3, 'Fri': 4, 'Sa': 5, 'So': 6}
        df = df.sort_values(by=['_id'], key=lambda x: x.map(custom_dict))
        print(df.head(10))
        my_sequence_weekend = ['#636EFA', '#636EFA', '#636EFA', '#636EFA', '#636EFA', 'RoyalBlue', 'RoyalBlue']
        # print(px.colors.qualitative.Plotly)
        fig = px.bar(df, x=df['_id'], y=df['count'],
                     color_discrete_sequence=[my_sequence_weekend]
                     )
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Wochentag")


    # ToDo Farben für Tortendiagramm festlegen + Abfrage auf Vorhersage analog Rest
    elif inputs.type_of_chart == "Tortendiagramm mit Wochentagen und Anzahl (anteilig)":
        custom_dict = {'Mo': 0, 'Di': 1, 'Mi': 2, 'Do': 3, 'Fri': 4, 'Sa': 5, 'So': 6}
        df = df.sort_values(by=['_id'], key=lambda x: x.map(custom_dict))
        print(df.head())
        my_sequence_pie_days = ['PowderBlue', 'DeepSkyBlue', 'RoyalBlue', 'SkyBlue', 'SlateBlue', 'SteelBlue',
                                'AliceBlue']

        fig = px.pie(df, values='count', names='_id',
                     color_discrete_sequence=my_sequence_pie_days,
                     )
        # Alternative, mit Werten innen

        fig.update_traces(textposition='inside', textinfo='percent+label')

    elif inputs.type_of_chart == "Histogramm mit Tageszeit und Anzahl":
        print(df.head(10))
        # df = df.reindex([7, 6, 3, 2, 1, 0, 4, 5])
        custom_dict = {'0-3': 0, '3-6': 1, '6-9': 2, '9-12': 3, '12-15': 4, '15-18': 5, '18-21': 6, '21-24': 7}
        df = df.sort_values(by=['_id'], key=lambda x: x.map(custom_dict))
        print(df.head(10))
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Tageszeit")
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Liniendiagramm mit Tageszeit und Anzahl":
        print(df.head(10))
        # df = df.reindex([7, 6, 3, 2, 1, 0, 4, 5])
        custom_dict = {'0-3': 0, '3-6': 1, '6-9': 2, '9-12': 3, '12-15': 4, '15-18': 5, '18-21': 6, '21-24': 7}
        df = df.sort_values(by=['_id'], key=lambda x: x.map(custom_dict))
        print(df.head(10))
        fig = px.line(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Tageszeit")
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_traces(mode='lines+markers')
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(line_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(line_color='#DAA520')


    elif inputs.type_of_chart == "Liniendiagramm mit Distanz und Anzahl_ungruppiert":
        print(df.head(10))
        fig = px.line(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Distanz")
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_traces(mode='lines+markers')
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(line_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(line_color='#DAA520')


    elif inputs.type_of_chart == "Histogramm mit Distanz und Anzahl_ungruppiert":
        print(df.head(10))
        fig = px.bar(df, x=df['_id'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Distanz")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Histogramm mit Distanz und Anzahl_gruppiert":
        # Gruppierungsfunktionen:
        cut_labels = ['0', '1-10', '11-20', '21-50', '51-75', '76-100', '101-200', '201-300', '>300']
        cut_bins = [-1, 1, 10, 20, 50, 75, 100, 200, 300, 10000]
        df['Gruppierte_Distanz'] = pd.cut(df['_id'], bins=cut_bins, labels=cut_labels)
        print(df.head(20))
        fig = px.bar(df, x=df['Gruppierte_Distanz'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Distanz")
        fig.update_xaxes(rangeslider_visible=True)
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(marker_color='#DAA520')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(marker_color='#DAA520')

    elif inputs.type_of_chart == "Liniendiagramm mit Distanz und Anzahl_gruppiert":
        # Gruppierungsfunktionen:
        cut_labels = ['0', '1-10', '11-20', '21-50', '51-75', '76-100', '101-200', '201-300', '>300']
        cut_bins = [-1, 1, 10, 20, 50, 75, 100, 200, 300, 10000]
        df['Gruppierte_Distanz'] = pd.cut(df['_id'], bins=cut_bins, labels=cut_labels)  # , labels=cut_labels
        print(df.head(20))
        fig = px.line(df, x=df['Gruppierte_Distanz'], y=df['count'])
        fig.update_layout(yaxis_title="Anzahl",
                          xaxis_title="Distanz")
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_traces(mode='lines+markers')
        # Mode optional für Punkte
        if inputs.dataset_type == "Vorhersage: Monatlicher Datensatz":
            fig.update_traces(line_color='#DAA520', mode='lines+markers')
        elif inputs.dataset_type == "Vorhersage: Täglicher Datensatz":
            fig.update_traces(line_color='#DAA520', mode='lines+markers')

    df.to_csv('webapp/outputs/saved_csv.csv', sep=",", index=False, encoding='utf-8')

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


# Download Button: Speichern des dataframes
@charts.route('/csv_download')
def plot_csv():
    from flask import send_file

    return send_file('outputs/saved_csv.csv',
                     mimetype='text/csv',
                     attachment_filename='CSV-Download.csv',
                     as_attachment=True)

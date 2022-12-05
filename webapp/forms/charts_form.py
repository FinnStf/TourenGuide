from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


#Mögliche Auswahlfelder
TYPE_CHOICES = ["Monatlicher Datensatz", "Täglicher Datensatz"] #wieder entfernt: "Vorhersage: Monatlicher Datensatz", "Vorhersage: Täglicher Datensatz"
TRAFFIC_CHOICES = ["Gesamtverkehr", "Binnen-Verkehr", "Outgoing-Verkehr", "Incoming-Verkehr"]
CHART_TYPE_CHOICES = [
                      "Histogramm mit Datum und Anzahl",
                      "Histogramm mit Datum und Anzahl_vertauscht",
                      "Histogramm mit Datum und Anzahl_Slider",
                      "Linien Diagramm mit Datum und Anzahl_Slider",
                      "Linien Diagramm mit Datum und Distanz",
                      "Tortendiagramm mit Datum und Anzahl",
                      "Histogramm mit Start-Landkreis und Anzahl",
                      "Histogramm mit Start-Landkreis und Anzahl_Top10",
                      "Histogramm mit Start-Landkreis und Distanz",
                      "Histogramm mit End-Landkreis und Anzahl",
                      "Histogramm mit End-Landkreis und Anzahl_Top10",
                      "Histogramm mit Transportmittel und Anzahl",
                      "Histogramm mit Transportmittel und Distanz",
                      "Tortendiagramm mit Transportmittel und Anzahl (anteilig)",
                      "Histogramm mit Wochentag und Anzahl",
                      "Tortendiagramm mit Wochentagen und Anzahl (anteilig)",
                      "Histogramm mit Tageszeit und Anzahl",
                      "Liniendiagramm mit Tageszeit und Anzahl",
                      "Liniendiagramm mit Distanz und Anzahl_ungruppiert",
                      "Histogramm mit Distanz und Anzahl_ungruppiert",
                      "Histogramm mit Distanz und Anzahl_gruppiert",
                      "Liniendiagramm mit Distanz und Anzahl_gruppiert"
]
X_AXIS_CHOICE = ["", "Landkreis-Start", "Landkreis-Ende", "Wochentag"]
Y_AXIS_CHOICE = ["", "Distanz", "Anzahl", "Wochentag"]
GROUP_BY_CHOICES = ["Datum", "Transportmittel", "Landkreis Start", "Landkreis Ende", "Wochentag", "Tageszeit", "Distanz", ""]
TIME_CHOICES = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18",
                "19", "20", "21", "22", "23", "0"]

#Zuordnung Auswahlmöglichkeiten mit Website-Feldern
class FilterFormCharts(FlaskForm):
    dataset_type = SelectField(label='state_dataset', choices=TYPE_CHOICES)
    type_of_chart = SelectField(label='type_of_chart', choices=CHART_TYPE_CHOICES)
    traffic_type = SelectField(label='state_traffic', choices=TRAFFIC_CHOICES)

    district_start = StringField(label='startName')
    district_end = StringField(label='endName')

    start_date = DateField('start_date')                #, validators=[DataRequired()]
    end_date = DateField('end_date')
    start_time = SelectField(label='startTime', choices=TIME_CHOICES)
    end_time = SelectField(label='endTime', choices=TIME_CHOICES)

    district_compare = StringField(label='district_compare')
    start_date_compare = DateField(label='start_date_compare')
    end_date_compare = DateField(label='end_date_compare')

    x_axis = SelectField(label='x_axis', choices=X_AXIS_CHOICE)
    y_axis = SelectField(label='y_axis', choices=Y_AXIS_CHOICE)

    group_by = SelectField(label='group_by', choices=GROUP_BY_CHOICES)

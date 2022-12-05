from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.html5 import DateField

TYPE_CHOICES = ["Monatlicher Datensatz", "Täglicher Datensatz"]
TIME_CHOICES = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18",
                "19", "20", "21", "22", "23", "0"]
TRAFFIC_CHOICES = ["Gesamtverkehr", "Outgoing-Verkehr", "Incoming-Verkehr", "Binnen-Verkehr"]


class FilterForm(FlaskForm):
    dataset_type = SelectField(label='State', choices=TYPE_CHOICES)
    startDate = DateField('startDate')
    endDate = DateField('endDate')
    startTime = SelectField(label='startTime', choices=TIME_CHOICES)
    endTime = SelectField(label='endTime', choices=TIME_CHOICES)
    startName = StringField(label='startName')
    endName = StringField(label='endName')
    traffic_type = SelectField(label='state_traffic', choices=TRAFFIC_CHOICES)
    submit = SubmitField('submit')

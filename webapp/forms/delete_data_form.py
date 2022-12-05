from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput


class DeleteDataForm(FlaskForm):
    datasetID = IntegerField(widget=HiddenInput())
    startDate = DateField('startDate', validators=[DataRequired()])
    endDate = DateField('endDate', validators=[DataRequired()])
    deleteAll = BooleanField('deleteAll')
    deleteSubmit = SubmitField('Delete')

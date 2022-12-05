from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired

TYPE_CHOICES = ["Täglicher Datensatz", "Monatlicher Datensatz"]
TRAFFIC_CHOICES = ["Binnen-Verkehr", "Outgoing-Verkehr", "Incoming-Verkehr", "Gesamtverkehr"]
COLOR_SCALE_CHOICES = ["aggrnyl", "agsunset", "blackbody", "bluered", "blues", "blugrn", "bluyl", "brwnyl",
                       "bugn", "bupu", "burg", "burgyl", "cividis", "darkmint", "electric", "emrld",
                       "gnbu", "greens", "greys", "hot", "inferno", "jet", "magenta", "magma",
                       "mint", "orrd", "oranges", "oryel", "peach", "pinkyl", "plasma", "plotly3",
                       "pubu", "pubugn", "purd", "purp", "purples", "purpor", "rainbow", "rdbu",
                       "rdpu", "redor", "reds", "sunset", "sunsetdark", "teal", "tealgrn", "turbo",
                       "viridis", "ylgn", "ylgnbu", "ylorbr", "ylorrd", "algae", "amp", "deep",
                       "dense", "gray", "haline", "ice", "matter", "solar", "speed", "tempo",
                       "thermal", "turbid", "armyrose", "brbg", "earth", "fall", "geyser", "prgn",
                       "piyg", "picnic", "portland", "puor", "rdgy", "rdylbu", "rdylgn", "spectral",
                       "tealrose", "temps", "tropic", "balance", "curl", "delta", "oxy", "edge",
                       "hsv", "icefire", "phase", "twilight", "mrybm", "mygbm"]
PROPORTION_CHOICES = ["Absolute Zahlen", "Prozentuale Zahlen"]


class FilterFormMaps(FlaskForm):
    dataset_type = SelectField(label='state_dataset', choices=TYPE_CHOICES)
    start_date = DateField('start_date', validators=[DataRequired()])
    end_date = DateField('end_date', validators=[DataRequired()])
    traffic_type = SelectField(label='state_traffic', choices=TRAFFIC_CHOICES)
    color_scale = SelectField(label='state_color', choices=COLOR_SCALE_CHOICES, default="blues")
    upper_range_color = IntegerField(label='upper_range_color')
    lower_range_color = IntegerField(label='lower_range_color')
    start_date_compare = DateField(label='start_date_compare')
    end_date_compare = DateField(label='end_date_compare')
    proportion_unit = SelectField(label='proportion_unit', choices=PROPORTION_CHOICES)
    reverse_colorscale = BooleanField(label='reverse_colorscale')
    submit = SubmitField('submit')

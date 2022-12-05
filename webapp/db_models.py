from datetime import datetime
from flask_login import UserMixin
from webapp import db, login_manager


#
# simply loads the user when logged in
#
@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=int(user_id)).first()


#
# User object and structure that will be saved in the mongo database
#
class User(db.Document, UserMixin):
    id = db.IntField(primary_key=True)
    first_name = db.StringField(max_length=50, null=False, required=True)
    last_name = db.StringField(max_length=50, null=False, required=True)
    email = db.EmailField(max_length=100, unique=True,
                          null=False, required=True)
    password = db.StringField(max_length=60, null=False, required=True)


#
# daily dataset
#
class DailyData(db.Document):
    bucket = db.DateField(null=False, required=True)
    startId = db.StringField(null=False, required=True)
    startName = db.StringField(max_length=100, null=False, required=True)
    endId = db.StringField(null=False, required=True)
    endName = db.StringField(max_length=100, null=False, required=True)
    modeOfTransport = db.StringField(max_length=100, null=False, required=True)
    tripDistance = db.IntField(null=False, required=True)
    count = db.IntField(null=False, required=True)
    meta = {
        'indexes': [
            'bucket'
        ]
    }


#
# monthly dataset
#
class MonthlyData(db.Document):
    bucket = db.DateField(null=False, required=True)
    startId = db.StringField(null=False, required=True)
    startName = db.StringField(max_length=100, null=False, required=True)
    endId = db.StringField(null=False, required=True)
    endName = db.StringField(max_length=100, null=False, required=True)
    weekday = db.StringField(max_length=100, null=False, required=True)
    daytime = db.StringField(max_length=100, null=False, required=True)
    tripDistance = db.IntField(null=False, required=True)
    modeOfTransport = db.StringField(max_length=100, null=False, required=True)
    count = db.IntField(null=False, required=True)
    meta = {
        'indexes': [
            'bucket'
        ]
    }


#
# geodata
#
class GeoData(db.Document):
    _id = db.StringField(primary_key=True)
    name = db.StringField(null=False, required=True)
    lon = db.FloatField(null=False, required=True)
    lat = db.FloatField(null=False, required=True)


#
# contains saved charts
#
class SavedMaps(db.Document):
    _id = db.IntField(primary_key=True)
    data = db.StringField(null=False, required=True)
    title = db.StringField()
    visible = db.BooleanField(null=False, required=True)
    favorite = db.StringField(null=False, required=True)
    input = db.StringField(null=False, required=True)


#
# contains saved charts
#
class SavedCharts(db.Document):
    _id = db.IntField(primary_key=True)
    data = db.StringField(null=False, required=True)
    title = db.StringField()
    visible = db.BooleanField(null=False, required=True)
    favorite = db.StringField(null=False, required=True)
    input = db.StringField(null=False, required=True)


#
# dataset for monitoring/managing db
#
class CollectionRecord(db.Document):
    _id = db.IntField(primary_key=True)
    name = db.StringField(null=False, required=True)
    timespan_start = db.DateField()
    timespan_end = db.DateField()
    row_count = db.IntField()
    modified_date = db.DateTimeField()


#
# contains the list that defines which graph to be displayed where at homescreen
#
class GraphOrder(db.Document):
    map_order = db.StringField(null=False, required=True)
    chart_order = db.StringField(null=False, required=True)


#
# contains the contents of a dashboard
#
class Dashboards(db.Document):
    _id = db.IntField(primary_key=True)
    first_entry = db.IntField()
    first_entry_type = db.StringField()
    second_entry = db.IntField()
    second_entry_type = db.StringField()
    third_entry = db.IntField()
    third_entry_type = db.StringField()
    text = db.StringField()

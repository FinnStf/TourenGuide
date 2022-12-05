import json
import os
import re
import threading
from datetime import datetime, timezone, timedelta, date

from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, url_for, request, jsonify, abort, flash
from flask_login import login_required
from mongoengine import OperationError
from pandas.errors import ParserError
from werkzeug.utils import redirect, secure_filename

from webapp.db_models import DailyData, MonthlyData, CollectionRecord
from webapp.forms.delete_data_form import DeleteDataForm

data_view = Blueprint("data_view", __name__, template_folder="templates")
progress = 0.0
upload = False
upload_Dataset_name = ''
upload_abort = False


#
# show the route that displays all datasets
#
@data_view.route('/data', methods=["GET", "POST"])
@login_required
def data_shown():
    collections = CollectionRecord.objects().all().as_pymongo()
    delete_data_form = DeleteDataForm()
    if delete_data_form.is_submitted():
        dataset_id = delete_data_form.datasetID.data
        start = delete_data_form.startDate.data
        end = delete_data_form.endDate.data
        delete_all = delete_data_form.deleteAll.data
        success_msg = delete_dataset(dataset_id, start, end, delete_all)
        flash(f'Aus dem Datensatz "{success_msg[0]}" wurden {success_msg[1]} Einträge erfolgreich gelöscht.', 'success')
        return redirect(url_for('data_view.data_shown'))
    return render_template("data_view.html", collections=collections, form=delete_data_form)


#
# route for updating dataset
#
@data_view.route("/data/<int:dataset_id>/update", methods=["GET", "POST"])
@login_required
def update_data(dataset_id):
    global upload_abort
    global upload
    global upload_Dataset_name
    global progress
    choices = []
    if request.method == "GET":
        upload_abort = False

        collections = CollectionRecord.objects.all()
        collection = CollectionRecord.objects.get(_id=dataset_id)
        # # Fill Selection Values with selected dataset on first position
        choices = [(col._id, col.name) for col in collections]
        choices.pop(choices.index((collection.id, collection.name)))
        choices.insert(0, (collection.id, collection.name))

    if request.method == "POST":
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        from run import app
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            file_path = os.path.join(app.root_path, 'uploads', filename)
            uploaded_file.save(file_path)
            # return selection: request.form["Dataset"] == "1,Täglicher Datensatz" ||  "2,Monatlicher Datensatz"
            dataset_key_value = request.form["Dataset"].split(',')
            dataset_key = int(dataset_key_value[0])
            upload_Dataset_name = dataset_key_value[1]
            # setz Upload Flag für die Progress Bar im data_view.html
            progress = 0.0
            upload = True
            insert_mongo_thread = threading.Thread(target=insert_mongo,
                                                   args=(file_path, filename, dataset_key))
            insert_mongo_thread.start()

            return redirect(url_for('data_view.data_shown'))
    return render_template('update_data.html', title='Update Dataset', options=choices)


#
# collect data from db for collection-register
#
def gather_collection_data(dataset_id, total_entries, oldest_date, latest_date):
    collection = CollectionRecord.objects.get(_id=dataset_id)
    if collection.timespan_start and collection.timespan_end:
        if collection.timespan_start > oldest_date:
            collection.timespan_start = oldest_date
        if collection.timespan_end < latest_date:
            collection.timespan_end = latest_date
    else:
        collection.timespan_start = oldest_date
        collection.timespan_end = latest_date
    collection.row_count += total_entries
    collection.modified_date = datetime.now(timezone.utc)
    collection.save()


#
# obsolete Method, due to teralitics data having data quality deficits --> insert_mongo used instead
# import a csv file and upload it to a given database
# might use too much memory for servers
#
def mongoimport(csv_path, dataset_type, db_name, db_url='localhost', db_port=27017):
    import pandas as pd
    from pymongo import MongoClient
    import json
    if dataset_type == "Täglicher Datensatz":
        coll_name = "daily_data"
        header_list = ["bucket", "startId", "startName", "endId", "endName", "modeOfTransport", "tripDistance", "count"]
    elif dataset_type == "Monatlicher Datensatz":
        coll_name = "monthly_data"
        header_list = ["bucket", "startId", "startName", "endId", "endName", "weekday", "daytime", "modeOfTransport",
                       "tripDistance", "count"]

    client = MongoClient(db_url, db_port)
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(csv_path, sep=",", header=0, index_col=False, names=header_list)
    payload = json.loads(data.to_json(orient='records'))
    coll.insert(payload)


#
# insert the uploaded datasets into the mongo database
# better for servers, since it doesnt consume too much memory
# collect data for collectionrecord ( oldest_date, latest_date, row_count)
#
def insert_mongo(csv_file_path, filename, dataset_key):
    global progress
    global upload
    global upload_abort
    # open up the file that was uploaded before
    file = convert_csv_to_json(csv_file_path, filename, dataset_key)
    with open(file, encoding="utf-8") as f:
        latest_date = None
        oldest_date = None
        # convert string to JsonObject
        entries = json.loads(f.read())
        daily_data = []
        monthly_data = []
        total_entries = len(entries)
        if total_entries > 1000:
            relative_progress = relative_progress_begin = int(total_entries / 100)
        else:
            relative_progress = 0
            relative_progress_begin = 1
        # iterate through all entries and save them in the database
        for idx, entry in enumerate(entries):
            if idx == relative_progress and progress < 100.0:
                relative_progress += relative_progress_begin
                progress = (100 * (idx + 1)) / total_entries
            elif idx == (total_entries - 1):
                progress = 100.0
            # check if this entry already exists
            # check only for the first entry due to performance reasons
            # if the first one is duplicate, then most likely the others are aswell (and the other way round)
            if idx == 0:
                if (DailyData.objects(bucket=entry["bucket"]).first() and
                    DailyData.objects(startId=entry["startId"]).first() and
                    DailyData.objects(startName=entry["startName"]).first() and
                    DailyData.objects(endId=entry["endId"]).first() and
                    DailyData.objects(endName=entry["endName"]).first() and
                    DailyData.objects(modeOfTransport=entry["modeOfTransport"]).first() and
                    DailyData.objects(tripDistance=entry["tripDistance"]).first() and
                    DailyData.objects(count=entry["count"]).first()) is None and \
                        (MonthlyData.objects(bucket=entry["bucket"]).first() and
                         MonthlyData.objects(startId=entry["startId"]).first() and
                         MonthlyData.objects(startName=entry["startName"]).first() and
                         MonthlyData.objects(endId=entry["endId"]).first() and
                         MonthlyData.objects(endName=entry["endName"]).first() and
                         MonthlyData.objects(weekday=entry["weekday"]).first() and
                         MonthlyData.objects(daytime=entry["daytime"]).first() and
                         MonthlyData.objects(modeOfTransport=entry["modeOfTransport"]).first() and
                         MonthlyData.objects(tripDistance=entry["tripDistance"]).first() and
                         MonthlyData.objects(count=entry["count"]).first()) is None:

                    if dataset_key == 1:
                        if re.search("\d\d\d\d-\d\d-\d\d", entry["bucket"]) is None:
                            entry["bucket"] = parse_bucket_str(entry["bucket"])
                        daily_data.append(DailyData(**entry))
                    elif dataset_key == 2:
                        entry["bucket"] = entry["bucket"] + "-01"
                        monthly_data.append(MonthlyData(**entry))
                    latest_date = oldest_date = parse_bucket_to_date(entry['bucket'])
                else:
                    abort_upload()
                    break
            else:
                if dataset_key == 1:
                    if re.search("\d\d\d\d-\d\d-\d\d", entry["bucket"]) is None:
                        entry["bucket"] = parse_bucket_str(entry["bucket"])
                    daily_data.append(DailyData(**entry))
                elif dataset_key == 2:
                    entry["bucket"] = entry["bucket"] + "-01"
                    monthly_data.append(MonthlyData(**entry))

                entry_date = parse_bucket_to_date(entry['bucket'])

                if latest_date < entry_date:
                    latest_date = entry_date
                elif oldest_date > entry_date:
                    oldest_date = entry_date
            # mongo can only store files with size 16MB (~50.000 entries)
            # if border is reached: upload and clear array
            if idx % 50000 == 0:
                if daily_data:
                    DailyData.objects.insert(daily_data)
                    daily_data = []
                if monthly_data:
                    MonthlyData.objects.insert(monthly_data)
                    monthly_data = []

    # upload the array
    if daily_data:
        DailyData.objects.insert(daily_data)
    if monthly_data:
        MonthlyData.objects.insert(monthly_data)

    f.close()
    os.remove(file)
    if not upload_abort:
        gather_collection_data(dataset_key, total_entries, oldest_date, latest_date)
    # progress == 101 => reload table
    progress += 1.0
    # set Upload to false
    upload = False


#
# convert the given dataset from a csv format to a json format
#
def convert_csv_to_json(csv_file_path, filename, dataset_type):
    json_filename = filename.replace("csv", "json")
    from run import app
    json_file_path = os.path.join(app.root_path, 'uploads', json_filename)

    import pandas as pd
    if dataset_type == 1:
        header_list = ["bucket", "startId", "startName", "endId", "endName", "modeOfTransport", "tripDistance", "count"]
    elif dataset_type == 2:
        header_list = ["bucket", "startId", "startName", "endId", "endName", "weekday", "daytime", "tripDistance",
                       "modeOfTransport", "count"]
    # to ensure that leading zero are kept: change dtype from int to string
    dtype_dic = {'startId': str, 'endId': str}
    # read in csv, convert to pandas dataframe and convert that to a json format
    try:
        csv_file = pd.DataFrame(
            pd.read_csv(csv_file_path, quotechar='"', doublequote=False, sep=',',
                        names=header_list, header=0, dtype=dtype_dic, encoding='utf-8'))
    except ParserError:
        print("Wrong File Format")
        csv_file = pd.DataFrame(
            pd.read_csv(csv_file_path, sep=',', names=header_list, header=0, dtype=dtype_dic, encoding='utf-8'))

    csv_file.to_json(json_file_path, orient="records", date_format="epoch", double_precision=10, force_ascii=False,
                     date_unit="ms", default_handler=None)
    os.remove(csv_file_path)

    return json_file_path


def parse_bucket_str(str):
    g = re.findall("[0-9]+", str)
    return g[0] + '-' + g[1] + '-' + g[2]


def parse_bucket_to_date(str):
    g = re.findall("[0-9]+", str)
    return date(int(g[0]), int(g[1]), int(g[2]))


#
# function for deleting dataset
#
def delete_dataset(dataset_id, start, end, all):
    # select specified dataset and Collection Record
    dataset = DailyData()
    selected_dataset = CollectionRecord.objects.get(_id=dataset_id)
    if dataset_id == 2:
        dataset = MonthlyData()
    # save old row count
    deleted_line_count = selected_dataset.row_count
    if all:
        try:
            dataset.drop_collection()
        except OperationError:
            raise OperationError("Delete failed. No collection for key: " + dataset_id)
        # delete connected CollectionRecord
        del selected_dataset.timespan_start
        del selected_dataset.timespan_end
    else:
        if dataset_id == 1:
            DailyData.objects(bucket__gte=start, bucket__lte=end).delete()
        elif dataset_id == 2:
            MonthlyData.objects(bucket__gte=start, bucket__lte=end).delete()
        if selected_dataset.timespan_start and selected_dataset.timespan_end:
            if start <= selected_dataset.timespan_start <= end and not selected_dataset.timespan_end <= end:
                dif = end - selected_dataset.timespan_start
                if dataset_id == 1:
                    selected_dataset.timespan_start += timedelta(days=dif.days + 1)
                elif dataset_id == 2:
                    selected_dataset.timespan_start += timedelta(days=dif.days)
                    selected_dataset.timespan_start += relativedelta(months=+1)
            elif start <= selected_dataset.timespan_end <= end and not selected_dataset.timespan_start >= start:
                dif = selected_dataset.timespan_end - start
                if dataset_id == 1:
                    selected_dataset.timespan_end -= timedelta(days=dif.days + 1)
                elif dataset_id == 2:
                    selected_dataset.timespan_end -= timedelta(days=dif.days)
                    selected_dataset.timespan_end -= relativedelta(months=+1)
            elif selected_dataset.timespan_end <= end and selected_dataset.timespan_start >= start:
                del selected_dataset.timespan_start
                del selected_dataset.timespan_end
    if dataset_id == 1:
        selected_dataset.row_count = DailyData.objects().count()
    elif dataset_id == 2:
        selected_dataset.row_count = MonthlyData.objects().count()
    deleted_line_count -= selected_dataset.row_count
    selected_dataset.modified_date = datetime.now(timezone.utc)
    selected_dataset.save()
    return [selected_dataset.name, deleted_line_count];


#
# reload table content
#
@data_view.route('/load_table', methods=["GET"])
@login_required
def load_table():
    collections = CollectionRecord.objects()
    json_table = []
    for collection in collections:
        json_table.append({"_id": collection._id,
                           "name": collection.name,
                           "time_begin": collection.timespan_start,
                           "time_end": collection.timespan_end,
                           "row_count": collection.row_count,
                           "modified": collection.modified_date,
                           })
    return jsonify(json_table)


#
# check for upload
#
@data_view.route('/_check_for_upload', methods=["GET"])
@login_required
def check_for_upload():
    global upload
    return jsonify({'response': upload})


#
# check for progress
#
@data_view.route('/_upload_progress', methods=["GET"])
@login_required
def upload_progress():
    global progress
    global upload_abort
    global upload_Dataset_name
    return jsonify({'progress': progress, 'datasetName': upload_Dataset_name, 'abort': upload_abort})


#
# inform progressBar of aborted upload
#
def abort_upload():
    global upload
    global upload_abort
    upload_abort = True
    upload = False


#
# reload table content
#
@data_view.route('/_get_datasetTime/<int:data_Id>', methods=["GET"])
@login_required
def retrieve_dataset_time(data_Id):
    collection = CollectionRecord.objects.get(_id=data_Id)
    return jsonify({"begin": collection.timespan_start, "end": collection.timespan_end})

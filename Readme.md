##Installation Instructions (Mac/Linux)
**Prerequisite: installed Python3**
**Prerequisite: running mongodb service**

###Step 1: Install Virtual Environment
python3 -m venv <name of environment>

###Step 2: Activate Venv
. <name of environment>/bin/activate

###Step 3: Install Requirements
pip install -r requirements.txt

###Step 4: Run App
python3 run.py


##MongoDB required collections
**The app requires some initial data in our database. Otherwise it wouldn’t work.
These collections have to be inserted:**
###CollectionRecord collection: 

db.collection_record.insertMany([{
  "_id": 1,
  "name": "Täglicher Datensatz",
  "row_count": 0,
  "modified_date": {
    "$date": "2021-06-14T12:35:03.429Z"
  }
},{
  "_id": 2,
  "name": "Monatlicher Datensatz",
  "row_count": 0,
  "modified_date": {
    "$date": "2021-06-14T12:35:07.326Z"
  }
}])
###User collection
***(needs at least one User – fill out <> with specific values):***
***Password Value needs to be hashed pwrd via bcrypt 12 rounds:***


db.user.insertOne({
"_id":1,"first_name":"<Vorname>","last_name":"<Nachname>","email":"<email_des_Users>","password":"<hashes_password>"})

###Graph_order collection:

db.graph_order.insertOne({
  "order": "[]"
})

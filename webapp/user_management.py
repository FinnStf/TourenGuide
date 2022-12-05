from flask import Blueprint, render_template, url_for, request
from flask.helpers import flash
from flask_login import login_required
from werkzeug.utils import redirect

from webapp import bcrypt
from webapp.db_models import User
from webapp.forms.user_form import UserUpdateForm, UserInsertForm

user_management = Blueprint("user_management", __name__,
                            template_folder="templates")


@user_management.route("/user_management", methods=["GET", "POST"])
@login_required
def user_table():
    users = User.objects().all().as_pymongo()
    admin_form = UserInsertForm()
    if admin_form.validate_on_submit():
        # if there is already an entry with that email address then throw an error
        if User.objects(email=admin_form.email.data).first() is None:
            create_user_object(admin_form)
            admin_form = clear_user_form(admin_form)
    return render_template("users.html", users=users, title="Neuen Benutzer anlegen", form=admin_form)


@user_management.route("/user_management/create_user", methods=["GET", "POST"])
@login_required
def create():
    # fields firstname, lastname, emailaddress, password
    admin_form = UserInsertForm()
    if admin_form.validate_on_submit():
        # if there is already an entry with that email address then throw an error
        if User.objects(email=admin_form.email.data).first() is None:
            create_user_object(admin_form)
            return redirect(url_for('user_management.user_table'))
        else:
            flash("E-Mail Adresse wird bereits verwendet!", "danger")
    return render_template("users.html", title="Neuen Benutzer anlegen", form=admin_form)


#
# create an entry in the mongo database
#
def create_user_object(admin_form):
    # hash the passwort so that it isnt saved as clear text in the db
    hashed_password = bcrypt.generate_password_hash(
        admin_form.password.data).decode("utf-8")
    # find unique ID
    unique_id = User.objects.count()
    # checks if object with same if already exists
    while User.objects(id__exact=unique_id):
        unique_id += 1

    new_user = User(
        id=unique_id,
        first_name=admin_form.first_name.data,
        last_name=admin_form.last_name.data,
        email=admin_form.email.data,
        password=hashed_password
    )
    new_user.save()
    flash(f"Benutzer {new_user.first_name} {new_user.last_name} erfolgreich hinzugefügt", "success")


def clear_user_form(form):
    form.first_name.data = ""
    form.last_name.data = ""
    form.email.data = ""
    form.password.data = ""
    form.password_repeat.data = ""
    return form


#
# route for updating user
#
@user_management.route("/user_management/<user_id>/update", methods=["GET", "POST"])
@login_required
def update_user(user_id):
    user = User.objects.get(id=user_id)
    if user:
        userForm = UserUpdateForm()
    if userForm.validate_on_submit():
        user.first_name = userForm.first_name.data
        user.last_name = userForm.last_name.data
        user.email = userForm.email.data
        user.password = bcrypt.generate_password_hash(
            userForm.password.data).decode("utf-8")
        user.save();
        flash(f'Der Benutzer {user.first_name} wurde geändert!', 'success')
        return redirect(url_for('user_management.user_table'))
    elif request.method == 'GET':
        userForm.first_name.data = user.first_name
        userForm.last_name.data = user.last_name
        userForm.email.data = user.email
        userForm.password.data = user.password
        userForm.password_repeat.data = user.password
    return render_template('update_user.html', title='Update Benutzer', form=userForm)


#
# route for deleting user
#
@user_management.route("/user_management/<user_id>/delete", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    flash(f'Der Benutzer {user.first_name} wurde gelöscht!', 'success')
    return redirect(url_for('user_management.user_table'))

from flask import (Blueprint, render_template, url_for, flash)
from flask_login import login_user, logout_user
from werkzeug.utils import redirect

from webapp import bcrypt
from webapp.db_models import User
from webapp.forms.login_form import LoginForm

authentication = Blueprint("authentication", __name__,
                           template_folder="templates")


#
# log in if email address and password are fine
#
@authentication.route("/login", methods=["GET", "POST"])
def login():
    """
        This route logs the current user IN
    """
    # consists of emailaddress, password and submit button
    login_form = LoginForm()
    # true if error while logging in, false if everything is fine
    error = False
    # if user hits submit button
    if login_form.validate_on_submit():
        # check if there is a user with the entered email address
        user = User.objects(email=login_form.email.data).first()
        # check if user exists and if the password hashes match
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash('Logged in successfully.', "success")
            return redirect(url_for("main.display_dashboards"))
        else:
            error = True
    return render_template("login.html", form=login_form, error=error)


#
# simple logout
#
@authentication.route("/logout")
def logout():
    """
    This route logs the current user OUT
    """
    logout_user()
    flash("Erfolgreich abgemeldet", "success")
    return redirect(url_for("authentication.login"))

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from webapp.config import Config

db = MongoEngine()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # db stuff
    db.init_app(app)
    # login stuff
    bcrypt.init_app(app)
    login_manager.init_app(app)

    #
    # structure to register a blueprint
    #
    # from <filepath> import <variable that saves blueprint information>
    # app.register_blueprint(<blueprint_name>)

    from webapp.main import main
    app.register_blueprint(main)

    from webapp.charts import charts
    app.register_blueprint(charts)

    from webapp.maps import maps
    app.register_blueprint(maps)

    from webapp.authentication import authentication
    app.register_blueprint(authentication)

    from webapp.data_view import data_view
    app.register_blueprint(data_view)

    from webapp.discover import discover
    app.register_blueprint(discover)

    from webapp.user_management import user_management
    app.register_blueprint(user_management)

    from webapp.graph_to_db import graph_to_db
    app.register_blueprint(graph_to_db)

    from webapp.display_graphs import display_graphs
    app.register_blueprint(display_graphs)

    from webapp.util.modify_graph import modify_graph
    app.register_blueprint(modify_graph)

    return app

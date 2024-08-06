from flask import Flask
from website.views import views
from website.auth import auth
from . import models
import os


def create_app(mydb):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'theva&raksh'

    uploads_folder = 'website\\uploads'
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)

    app.config['UPLOAD_FOLDER'] = uploads_folder
    app.config['UPLOADED_TEXT_URL'] = '/uploads/text/'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    models.set_app(app, mydb)

    return app


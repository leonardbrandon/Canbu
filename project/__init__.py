import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)


# Configuration - once happy with this, separate into separate config.py file
app.config['SECRET_KEY'] = 'BCRcooperative21'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'canbu.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

#global startDate, endDate
#global master_df_flag
master_df_flag = False

# NOTE! These imports need to come after you've defined db, otherwise you will
# get errors in your models.py files.
## Grab the blueprints from the other views.py files for each "app"
from project.canbu.blueprint import canbu_bp

app.register_blueprint(canbu_bp)


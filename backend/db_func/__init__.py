from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

""" This 4 Lines of Code is needed, if not templates would need to be in the same folder flask was initialized"""
current_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current file (__init__.py)
project_root = os.path.dirname(current_dir) # Go up one level to the project root
template_dir = os.path.join(project_root, 'templates')# Path to the templates folder

app = Flask(__name__, template_folder=template_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app) 

# Reason for using packages - for example, you don't need to run this app.push() func in every function called. 
app.app_context().push()

# Also, without packages, you will have to import app and db to every function called. 
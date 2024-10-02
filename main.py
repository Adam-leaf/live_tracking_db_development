from db_func import app
from routes import *

if __name__ == '__main__' : 

    app.run(host="0.0.0.0", port=5001, debug=True)

# TODO:
# Calculate PNL and display in web
# Improve file structure and use blueprints if needed
# Migrate Bybit
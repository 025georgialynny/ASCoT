from app import app
from config_default import *
from app.build_data import make_data

if __name__ == "__main__":
    make_data()
    app.run(host="0.0.0.0", debug=True)

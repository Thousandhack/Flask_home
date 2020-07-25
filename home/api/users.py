from . import api
from home import db

@api.route("/index")
def index():
    """
    http://127.0.0.1:5000/api/v1.0/index
    :return:
    """
    return "index page"

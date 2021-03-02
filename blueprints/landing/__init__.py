from quart import Blueprint
landing = Blueprint('landing', __name__, template_folder='templates')
from . import landing_page
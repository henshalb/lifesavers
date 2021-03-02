from . import landing
from quart import render_template

@landing.route('/',methods=['GET'])
async def landing_function():
    return await render_template('landing.html')
import json

from flask import current_app, g

import plotly
import plotly.express as px


def make_chart(df, sensor, var, units):

    # TODO determine appropriate plot from sensor type

    # Create pond sensor plot
    fig = px.line(df, x=df.index, y=var,
                  labels={ df.index.name: 'Date', var: f'{var} ({units})' },
                  title=f'{sensor["display_name"]}: {var}')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

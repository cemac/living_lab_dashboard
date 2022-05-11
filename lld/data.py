from flask import current_app, g

import pandas as pd
import numpy as np

def get_data_path(site_name, sensor_name):
    '''
    Use site and sensor name to construct path to data
    '''
    data_path = "/".join([
        current_app.config['DATA_PATH'],
        site_name,
        sensor_name,
        sensor_name
    ])
    data_path = data_path.replace(' ', '_')

    return data_path


def get_data(sensor):

    # TODO replace below with call to data handling methods as appropriate

    # TODO find index of line starting with !Names
    index = 7
    fp = get_data_path(sensor['site_name'], sensor['sensor_name']) + ".csv"
    columns = pd.read_csv(current_app.open_resource(fp), header=index, nrows=index).columns[1:]

    # TODO read metadata section and extract info e.g. units
    df = pd.read_csv(
        current_app.open_resource(fp),
        comment="!",  # skip metadata section
        names=columns,
        header=None,
        index_col=0,
        parse_dates=True
    )

    df.index.set_names(["Timestamp"], inplace=True)

    # Remove rows that contain system messages
    msg = df[df.columns[0]].str.contains('\*')
    df = df.drop(index=msg.index[np.where(msg==True)])

    # Set data types to np.float64
    # TODO specify correct data types for this dataset
    types = dict(map(lambda t: (t, np.float64), df.columns))
    df = df.astype(types)

    # TODO enable correction of variables in admin UI?
    df = df.rename(columns={'Velcoity':'Velocity'})

    return df

from flask import current_app, g

import pandas as pd
import numpy as np

def get_data_path(site_name, sensor_name, suffix = ".csv"):
    '''
    Use site and sensor name to construct path to data
    '''
    data_path = "/".join([
        current_app.config['DATA_PATH'],
        site_name,
        sensor_name,
        sensor_name
    ])
    data_path = data_path.replace(' ', '_') + suffix

    return data_path


def get_data(sensor):

    # TODO replace below with call to data handling methods as appropriate

    # TODO find index of line starting with !Names
    index = 7
    fp = get_data_path(sensor['site_name'], sensor['sensor_name'])
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

    # Get metadata about columns for fixing variable names etc
    # TODO enable specification of variables in admin UI?
    columns = {}
    try:
        # Read variable names and units from metadata file
        md_path = get_data_path(sensor['site_name'], sensor['sensor_name'],
                                suffix="-metadata.csv")
        metadata = pd.read_csv(current_app.open_resource(md_path)).set_index('column_name').to_dict()

        # Create lookup from initial column name to display name
        columns = metadata['name']

        # Create lookup from display name to units
        units = { value: metadata['units'][key]
                  for key, value in metadata['name'].items() }

        # Drop unspecified columns
        df = df.drop(df.columns.difference(columns.keys()), axis=1)
    except FileNotFoundError:
        columns = {'Velcoity':'Velocity'}

    # Clean up column names
    df = df.rename(columns=columns)

    return df, units

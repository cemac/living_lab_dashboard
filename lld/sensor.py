from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lld.auth import login_required
from lld.db import get_db
from lld.data import get_data
from lld.chart import make_chart

bp = Blueprint('sensor', __name__, url_prefix='/sensor')

@bp.route('/<int:sensor_id>', defaults={ 'var': None })
@bp.route('/<int:sensor_id>/<string:var>')
def index(sensor_id, var):
    db = get_db()

    sensor = db.execute(
        'SELECT s.id, s.sensor_name, s.sensor_type, s.display_name,'
        ' s.site_id, s.description, i.site_name'
        ' FROM sensor s'
        ' JOIN site i ON s.site_id = i.id'
        ' WHERE s.id = ?'
        ' ORDER BY sensor_name DESC', (sensor_id,)
    ).fetchone()

    try:
        data, metadata = get_data(sensor)
        if var is None:
            # Default to variable in first column
            var = data.columns[0]
        # Get units from metadata for display in chart
        units = metadata[var]
        chart = make_chart(data, sensor, var, units)
        return render_template('sensor/index.html', sensor=sensor, data=data, chart=chart, var=var)
    except FileNotFoundError:
        error = f"Couldn't find data file for sensor {sensor['sensor_name']}"
        flash(error)
        return render_template('sensor/index.html', sensor=sensor)


@bp.route('/<int:site_id>/create', methods=('GET', 'POST'))
@login_required
def create(site_id):
    if request.method == 'POST':
        sensor_name = request.form['sensor_name']
        sensor_type = request.form['sensor_type']
        description = request.form['description']
        display_name = request.form['display_name']
        error = None

        if not sensor_name:
            error = 'Sensor name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO sensor (sensor_name, sensor_type, description, display_name, site_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (sensor_name, sensor_type, description, display_name, site_id)
            )
            db.commit()
            return redirect(url_for('site.index'))

    return render_template('sensor/create.html', site_id=site_id)


def get_sensor(id):
    sensor = get_db().execute(
        'SELECT s.id, sensor_name, sensor_type, description, display_name'
        ' FROM sensor s'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if sensor is None:
        abort(404, f"Sensor id {id} doesn't exist.")

    return sensor


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    sensor = get_sensor(id)

    if request.method == 'POST':
        sensor_name = request.form['sensor_name']
        sensor_type = request.form['sensor_type']
        description = request.form['description']
        display_name = request.form['display_name']
        error = None

        if not sensor_name:
            error = 'Sensor name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE sensor SET sensor_name = ?, sensor_type = ?,'
                ' description = ?, display_name = ?'
                ' WHERE id = ?',
                (sensor_name, sensor_type,
                 description, display_name, id)
            )
            db.commit()
            return redirect(url_for('sensor.index', sensor_id=id))

    return render_template('sensor/update.html', sensor=sensor)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_sensor(id)
    db = get_db()
    db.execute('DELETE FROM sensor WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('site.index'))

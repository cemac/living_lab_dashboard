from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lld.auth import login_required
from lld.db import get_db

from itertools import groupby

#bp = Blueprint('site', __name__)
bp = Blueprint('site', __name__, url_prefix='/site')


@bp.route('/<int:id>')
def index(id = None):
    db = get_db()
    if id is not None:
        site = get_site(id)
        sensors = db.execute(
            'SELECT s.id, s.sensor_name, s.display_name, s.site_id'
            ' FROM sensor s JOIN site i ON s.site_id = i.id'
            ' WHERE s.id = ?'
            ' ORDER BY sensor_name DESC',
            (id,)
        ).fetchall()

        return render_template('site/index.html', site=site, sensors=sensors)
    else:
        sites = db.execute(
            'SELECT s.id, site_name, description, lat, lon'
            ' FROM site s'
            ' ORDER BY site_name DESC'
            
            # 'SELECT s.id, s.site_name, s.description, s.lat, s.lon'
            # ' FROM site s JOIN sensor s2 ON s.id = s2.site_id'
            # ' ORDER BY site_name DESC'

        ).fetchall()

        sensors = db.execute(
            'SELECT s.id, s.sensor_name, s.display_name, s.site_id'
            ' FROM sensor s JOIN site i ON s.site_id = i.id'
            ' ORDER BY site_id, sensor_name DESC'
        ).fetchall()

        sensors_grouped = {}

        for k, g in groupby(sensors, key=lambda t: t['site_id']):
            sensors_grouped[k] = list(g)
        # object with key site_id, value list of sqlite3.Row objects
        # flash(sensors_grouped[1])
        return render_template('index.html', sites=sites, sensors=sensors, sensors_grouped=sensors_grouped)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        site_name = request.form['site_name']
        description = request.form['description']
        lat = request.form['lat']
        lon = request.form['lon']
        error = None

        if not site_name:
            error = 'Site name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO site (site_name, description, lat, lon)'
                ' VALUES (?, ?, ?, ?)',
                (site_name, description, lat, lon)
            )
            db.commit()
            return redirect(url_for('site.index'))

    return render_template('site/create.html')


def get_site(id, check_author=False):
    site = get_db().execute(
        'SELECT s.id, site_name, description, lat, lon'
        ' FROM site s' #JOIN user u ON p.author_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if site is None:
        abort(404, f"Site id {id} doesn't exist.")

    #if check_author and post['author_id'] != g.user['id']:
    #    abort(403)

    return site


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    site = get_site(id)

    if request.method == 'POST':
        site_name = request.form['site_name']
        description = request.form['description']
        lat = request.form['lat']
        lon = request.form['lon']
        error = None

        if not site_name:
            error = 'Site name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE site SET site_name = ?, description = ?,'
                'lat = ?, lon = ?'
                ' WHERE id = ?',
                (site_name, description, lat, lon, id)
            )
            db.commit()
            return redirect(url_for('site.index'))

    return render_template('site/update.html', site=site)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_site(id)
    db = get_db()
    db.execute('DELETE FROM site WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('site.index'))

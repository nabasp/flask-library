from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('home', __name__)
@bp.route('/')
@login_required
def index():
    db = get_db()
    members = db.execute(
        'SELECT *'
        ' FROM members'
        ' ORDER BY created_at DESC'
    ).fetchall()
    return render_template('index.html',members=members)

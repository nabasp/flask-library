from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('member', __name__,url_prefix='/member')

@bp.route('/')
def index():
    db = get_db()
    members = get_members()
    return render_template('member/index.html', members_list=members)
    
@bp.route('/manage')
def manage():
    db = get_db()
    members = get_members()
    return render_template('member/manage.html', members_list=members)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        member_name = request.form['name']
        member_email = request.form['email']
        member_phone = request.form['phone']
        member_dob = request.form['dob']
        member_gender = request.form['gender']
        member_status = request.form['status']
        member_address = request.form['address']
        
        error = None

        if not member_name:
            error = 'member name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO members (name,status,phone,email,dob,gender,address)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (member_name, member_status, member_phone,member_email,member_dob,member_gender,member_address)
            )
            db.commit()
            return redirect(url_for('member.index'))

    return render_template('member/create.html')

def get_member(id):
    member = get_db().execute(
        'SELECT *'
        ' FROM members'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if member is None:
        abort(404, f"Post id {id} doesn't exist.")

    return member
def get_members():
    db = get_db()
    members = db.execute(
        'SELECT id,name,status,phone,email,dob,gender,address,created_at'
        ' FROM members'
        ' ORDER BY created_at DESC'
    ).fetchall()
    return members
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_member(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('member.index'))

    return render_template('member/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

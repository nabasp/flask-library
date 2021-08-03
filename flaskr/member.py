from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db,get_db_dict

bp = Blueprint('member', __name__,url_prefix='/member')

@bp.route('/')
@login_required
def index():
    db = get_db()
    members = get_members()
    return render_template('member/index.html', members_list=members)
    
@bp.route('/manage')
@login_required
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
        member_status = request.form.get('status')
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
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (member_name, member_status, member_phone, member_email, member_dob, member_gender, member_address)
            )
            db.commit()
            return redirect(url_for('member.index'))

    return render_template('member/create.html')

def get_member(id):
    member = get_db_dict().execute(
        'SELECT id,name,status,phone,email,dob,gender,address,created_at'
        ' FROM members'
        ' WHERE id = ?',
        (id,)
    ).fetchall()
    if member is not None:
        member=member[0]
    return member
def get_members():
    db = get_db()
    members = db.execute(
        'SELECT id,name,status,phone,email,dob,gender,address,created_at'
        ' FROM members'
        ' ORDER BY created_at DESC'
    ).fetchall()
    return members
@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    
    if request.method == 'POST':
        member_id = request.form['memberId']
        member_name = request.form['name']
        member_email = request.form['email']
        member_phone = request.form['phone']
        member_dob = request.form['dob']
        member_gender = request.form['gender']
        member_status = request.form.get('status')
        member_address = request.form['address']
        error = None
        if not member_id:
            error = 'member id is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE members SET name = ?, email = ?, phone = ?, dob = ?,  gender = ?, status = ?, address = ?'
                ' WHERE id = ?',
                (member_name, member_email, member_phone, member_dob, member_gender, member_status, member_address,member_id)
            )
            db.commit()
            

    return redirect(url_for('member.manage'))

@bp.route('/delete', methods=('POST',))
@login_required
def delete():
    member_id = request.form['delMemberId']
    db = get_db()
    db.execute('DELETE FROM members WHERE id = ?', (member_id,))
    db.commit()
    return redirect(url_for('member.manage'))

@bp.route('/<int:id>/edit')
@login_required
def getMemberAjax(id):
    
    member = get_member(id)
       
    return jsonify(member)

from re import M
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify,json
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db,get_db_dict


bp = Blueprint('home', __name__)
@bp.route('/')
@login_required
def index():
    db = get_db_dict()
    members = db.execute(
        'SELECT count(*) as memberCount,created_at as date'
        ' FROM members'
        ' GROUP BY created_at'
    ).fetchall()
    memberCount= []
    joinDates=[]
    
    for info in members:
        memberCount.append(info['memberCount'])
        joinDates.append(str(info['date']))

    totalmemberCount = sum(memberCount)

    books = db.execute(
        'SELECT count(*) as bookCount,created_at as date'
        ' FROM books'
        ' GROUP BY created_at'
    ).fetchall()
    bookCount= []
    importedDates=[]
    
    for info in books:
        bookCount.append(info['bookCount'])
        importedDates.append(str(info['date']))

    totalbookCount = sum(bookCount)

    totalReturned = get_db_dict().execute(
        'SELECT sum(total_rent + extra_charge) as totalReturned,return_date'
        ' FROM book_issued WHERE is_returned=1'
        ' GROUP BY return_date'
    ).fetchall()
    returnAmounts= []
    returnDates=[]
    
    for info in totalReturned:
        returnAmounts.append(info['totalReturned'])
        returnDates.append(str(info['return_date']))

    totalReturnAmounts = sum(returnAmounts)


    bookIssueCount = get_db_dict().execute(
        'SELECT count(*)'
        ' FROM book_issued'
    ).fetchone()

    bookIssueCount = get_db_dict().execute(
        'SELECT count(*)'
        ' FROM book_issued WHERE is_returned=1'
    ).fetchone()

    
    return render_template('index.html',
    returnAmounts=json.dumps(returnAmounts),
    returnDates=json.dumps(returnDates),
    totalReturnAmounts=totalReturnAmounts,
    memberCount=json.dumps(memberCount),
    joinDates=json.dumps(joinDates),
    totalmemberCount=totalmemberCount,
    bookCount=json.dumps(bookCount),
    importedDates=json.dumps(importedDates),
    totalbookCount=totalbookCount,
    bookIssueCount=bookIssueCount)

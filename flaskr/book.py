from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
import requests
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db,get_db_dict

bp = Blueprint('book', __name__,url_prefix='/book')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        query = request.form
        response =requests.get("https://frappe.io/api/method/frappe-library", params=query)
    else:
        response =requests.get("https://frappe.io/api/method/frappe-library")
        
    books = response.json()
    
    return render_template('book/index.html', books=books['message'])
    
@bp.route('/manage')
@login_required
def manage():
    db = get_db()
    members = get_members()
    return render_template('book/manage.html', members_list=members)

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
            return redirect(url_for('book.index'))

    return render_template('book/create.html')

def get_book(key,value):
    book=None
    
    if(key):
        sql = 'SELECT * FROM books WHERE ' + key + ' = ?'
        book = get_db_dict().execute(sql,(value,)).fetchone()

    return book
def get_all_book():
    book=None
    sql = 'SELECT * FROM books'
    books = get_db_dict().execute(sql).fetchall()
    
    return books
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
            

    return redirect(url_for('book.manage'))

@bp.route('/delete', methods=('POST',))
@login_required
def delete():
    member_id = request.form['delMemberId']
    db = get_db()
    db.execute('DELETE FROM members WHERE id = ?', (member_id,))
    db.commit()
    return redirect(url_for('book.manage'))

@bp.route('/<string:isbn>/getBook')
@login_required
def getBookAjax(isbn):
    if(isbn=="all"):
        book = {"data":get_all_book()}
    else:
        filter = {'key':'isbn', 'value': isbn}
        book = get_book(**filter)
       
    return jsonify(book)


def updateBookData(id,keys,values):

    if id:
        sql = 'UPDATE books SET '+ keys + ' WHERE id = ?'
        db = get_db()
        db.execute(sql,(values,id))
        db.commit()
        return True

    return False

def insertBookData(keys,values):

    sql = 'INSERT INTO books ('+ keys + ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    db = get_db()
    db.execute(sql,(values))
    db.commit()

    return True     

@bp.route('/<string:isbn>/importBook',methods=('POST',))
@login_required
def importBookAjax(isbn):
    
    book = None
    apiResponseData = None
    result = {'code' : '400' , 'message': 'Error, Method Not Allowed'}
    if request.method == 'POST':
        filter = {'key':'isbn', 'value': isbn}
        book = get_book(**filter)
        numberOfBooks = int(request.form['numberOfBooks'])
        
        if book and numberOfBooks>=1 and numberOfBooks <= 30:
            params = {'id':book['id'],'keys':'book_count = ?', 'values': book['book_count'] + numberOfBooks}
            res = updateBookData(**params)
            
            if res:
                result['code'] = 200
                result['message'] = "Success Fully Imported" 
                


        else:
            try:
                query={'isbn':isbn}
                response =requests.get("https://frappe.io/api/method/frappe-library", params=query)
                apiResponseData = response.json()
                if apiResponseData['message']:
                    book = apiResponseData['message'][0]
                    if book is not None:
                        params = {
                            'keys':'bookID,title,authors,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,book_count', 
                            'values': [book['bookID'],book['title'],book['authors'],book['average_rating'],book['isbn'],book['isbn13'],book['language_code'],book['  num_pages'],book['ratings_count'],book['text_reviews_count'],book['publication_date'],book['publisher'],numberOfBooks]
                            }
                        res = insertBookData(**params)
                        if res:
                            result['code'] = 200
                            result['message'] = "New Book, Success Fully Imported"

            except requests.exceptions.HTTPError as error:
                return jsonify(error)

    return jsonify(result)
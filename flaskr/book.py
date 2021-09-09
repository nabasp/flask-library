from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
import requests
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db,get_db_dict

from datetime import datetime

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

@bp.route('/issuedBooks')
@login_required
def issuedBooks():
    return render_template('book/issuedBooks.html')

@bp.route('/<int:issueId>/invoice',methods=('GET', 'POST'))
@login_required
def showInvoice(issueId):
    booksIssued = getBookIssueData(0,0,0,{},issueId)
    if(booksIssued):
        issueDate = datetime.strptime(booksIssued['issued_date'], '%Y-%m-%d %H:%M:%S').date()
        returnDate = datetime.strptime(booksIssued['return_date'], '%Y-%m-%d').date()
        booksIssued['fromDate'] = issueDate
        booksIssued['toDate'] = returnDate
        deltaDays = returnDate - issueDate
        booksIssued['noOfDays']=deltaDays.days
        booksIssued['total']=booksIssued['total_rent']+booksIssued['extra_charge']


    return render_template('book/invoice.html',data = booksIssued)

@bp.route('/issue', methods=('POST',))
@login_required
def create():
    result = {'code' : '400' , 'message': 'Error, Method Not Allowed'}
    if request.method == 'POST':
        
        member_id = request.form['issueMember']
        book_id = request.form['bookID']
        book = get_book('bookID',book_id)

        

        if not book:
            result['code'] = 422
            result['message'] = "Invalid Book" 
            return jsonify(result)

        day_rent = float(book['rent_day'])

        total_rent = float(request.form['totalRent'])
        return_date = request.form['returnDate']
        note = request.form['note']

        bookCount = book['book_count']

        if bookCount <= 0:
            result['code'] = 422
            result['message'] = "out of stock" 
            return jsonify(result)
        
        
        if not member_id:
            result['code'] = 422
            result['message'] = "Member is require"
            return jsonify(result)

        member=get_member_by_id(member_id)
        

        if not member:
            result['code'] = 422
            result['message'] = "Invalid member id"
            return jsonify(result)

        totalDebit = getTotalDebit(member_id)
        
        
        totalAmount = totalDebit + total_rent

        
        
        if  totalAmount >= 500:
            result['code'] = 422
            result['message'] = "Debit is More than 500 $ , Member pending rent = " + str(totalDebit) +' $'
            return jsonify(result)

        issueDetails=getBookIssueData(book_id,member_id)
        
        if issueDetails:
            result['code'] = 422
            result['message'] = "Already issued to this member on "+issueDetails['issued_date']
            return jsonify(result)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO book_issued (bookID,memberID,rent_day,total_rent,return_date,note)'
                ' VALUES (?, ?, ?, ?, ?, ? )',
                (book_id, member_id, day_rent, total_rent, return_date, note)
            )
            newStock = bookCount-1 
            sql = 'UPDATE books SET book_count = ? WHERE id = ?'
            db.execute(sql,(newStock,book['id']))

            db.commit()

            result['code'] = 200
            result['member'] = member
            result['book'] = book
            result['message'] = "Success Fully Issued" 
            

    return jsonify(result)

def get_book(key,value):
    book=None
    
    if(key):
        sql = 'SELECT * FROM books WHERE ' + key + ' = ?'
        book = get_db_dict().execute(sql,(value,)).fetchone()

    return book

def getBookIssueData(bookId,memberId,fetchAll=0,isReturned={},issueId=0):
    
    issueDetails=None
    if issueId:
        if isReturned:
            returnedStatus = isReturned['status']
            sql = 'SELECT book_issued.id as issueId,* FROM book_issued LEFT JOIN members ON book_issued.memberID = members.id LEFT JOIN books ON book_issued.bookID = books.bookID WHERE issueId = ? AND is_returned = ?'
            issueDetails = get_db_dict().execute(sql,(issueId,returnedStatus)).fetchone()
        else:
            sql = 'SELECT book_issued.id as issueId,* FROM book_issued LEFT JOIN members ON book_issued.memberID = members.id LEFT JOIN books ON book_issued.bookID = books.bookID WHERE issueId = ?'
            issueDetails = get_db_dict().execute(sql,(issueId,)).fetchone()
        

    elif(bookId and memberId):
        sql = 'SELECT book_issued.id as issueId,* FROM book_issued WHERE memberID = ? AND bookID = ?'
        issueDetails = get_db_dict().execute(sql,(memberId,bookId)).fetchone()
    elif fetchAll and isReturned:
        returnedStatus = isReturned['status']
        sql = 'SELECT book_issued.id as issueId,* FROM  book_issued LEFT JOIN members ON book_issued.memberID = members.id LEFT JOIN books ON book_issued.bookID = books.bookID WHERE book_issued.is_returned = ?'
        issueDetails = get_db_dict().execute(sql,(returnedStatus,)).fetchall()
    elif fetchAll:
        sql = 'SELECT book_issued.id as issueId,* FROM book_issued LEFT JOIN members ON book_issued.memberID = members.id LEFT JOIN books ON book_issued.bookID = books.bookID'
        issueDetails = get_db_dict().execute(sql).fetchall()

    return issueDetails

def getTotalDebit(memberId):
    TotalDebit=0
    
    if(memberId):
        sql = 'SELECT SUM(total_rent) AS totalDebit FROM book_issued WHERE memberID = ? AND  is_returned = ?'
        TotalDebitResult = get_db_dict().execute(sql,(memberId,False)).fetchone()
        if TotalDebitResult:
            TotalDebit = TotalDebitResult['totalDebit'] if TotalDebitResult['totalDebit'] else 0

    return TotalDebit

def get_member_by_id(id):
    member=None
    
    if(id):
        sql = 'SELECT * FROM members WHERE id = ?'
        member = get_db_dict().execute(sql,(id)).fetchone()

    return member

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

    sql = 'INSERT INTO books ('+ keys + ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    db = get_db()
    db.execute(sql,(values))
    db.commit()

    return True     

@bp.route('/getIssueDatas',methods=('GET', 'POST'))
@login_required
def getIssueDatas():
    booksIssued = {"data":getBookIssueData(0,0,1)}
  
    return jsonify(booksIssued)

@bp.route('/<int:id>/getIssueDatasById',methods=('GET', 'POST'))
@login_required
def getIssueData(id):
    booksIssued = getBookIssueData(0,0,0,{'status':0},id)
  
    return jsonify(booksIssued)

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
        perDayRent = int(request.form['perDayRent'])

        if (numberOfBooks < 0 or numberOfBooks > 300):
            result = {'code' : '422' , 'message': 'number Of Books must b/w 1-300'}
            return jsonify(result)

        if perDayRent<=0 or perDayRent>=500:
            result = {'code' : '422' , 'message': 'per Day Rent must b/w 0-500'}
            return jsonify(result)

        if book:
            params = {'id':book['id'],'keys':'book_count = ?', 'values': book['book_count'] + numberOfBooks}
            res = updateBookData(**params)
            params = {'id':book['id'],'keys':'rent_day = ?', 'values': perDayRent}
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
                            'keys':'bookID,title,authors,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,book_count,rent_day', 
                            'values': [book['bookID'],book['title'],book['authors'],book['average_rating'],book['isbn'],book['isbn13'],book['language_code'],book['  num_pages'],book['ratings_count'],book['text_reviews_count'],book['publication_date'],book['publisher'],numberOfBooks,perDayRent]
                            }
                        res = insertBookData(**params)
                        if res:
                            result['code'] = 200
                            result['message'] = "New Book, Success Fully Imported"

            except requests.exceptions.HTTPError as error:
                return jsonify(error)

    return jsonify(result)
@bp.route('/return', methods=('POST',))
@login_required
def bookReturn():
    result = {'code' : '400' , 'message': 'Error, Method Not Allowed'}
    if request.method == 'POST':
        
        extraCharge = float(request.form['extraCharge'])
        issueID = request.form['issueID']
        issueDetails = getBookIssueData(0,0,0,{'status':0},issueID)

        

        if not issueDetails:
            result['code'] = 422
            result['message'] = "Invalid issue id" 
            return jsonify(result)

        bookID = issueDetails['bookID']
        member = issueDetails['name']
        book = issueDetails['title']


        total_rent = float(issueDetails['total_rent'])
        return_date = request.form['returnDate']
        note = request.form['note']

        
        
        
        totalAmount = float(extraCharge) + total_rent
        db = get_db()
        sql = 'UPDATE book_issued SET is_returned = 1 ,extra_charge = ?,return_date = ? ,note = ? WHERE id = ?'
        db.execute(sql,(extraCharge,return_date,note,issueID))
        sql = 'UPDATE books SET book_count = book_count + 1 WHERE bookID = ?'
        db.execute(sql,(bookID,))
        db.commit()

        result['code'] = 200
        result['member'] = member
        result['book'] = book
        result['message'] = "Success Fully Returned" 
            

    return jsonify(result)
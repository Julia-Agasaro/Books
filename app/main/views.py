
from flask import render_template,request,redirect,url_for,abort
from ..models import  User,Book,Comment,Upvote
from . import main
# from ..request import get_movies,get_movie
from flask_login import login_required, current_user
from .forms import UpdateProfile,BookForm,CommentForm,UpvoteForm,ContactForm
from .. import db,photos
import markdown2 
import os
from werkzeug.utils import secure_filename
# from app import app

# Views
@main.route('/', methods = ['GET','POST'])
def index():

    '''
    View root page function that returns the index page and its data
    '''
    books = Book.query.all()
    title = 'Welcome Home-250-Books'
    # Educational = Book.query.filter_by(category="Educational")
    # Musical = Book.query.filter_by(category = "Musical")
    # Religion = Book.query.filter_by(category = "Religion")
    # Comedy = Book.query.filter_by(category = "Comedy")

    return render_template('index.html', title = title, books = books)


@main.route('/books/new/', methods = ['GET','POST'])
@login_required
def new_book():
    form = BookForm()
   
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data
        user_id = current_user
        category = form.category.data
        location =form.location.data
        f = form.poster.data
        filename = secure_filename(f.filename)
        path = f'photos/{filename}'
        # path = photos.url(filename)
        new_book = Book(user_id =current_user._get_current_object().id, title = title,summary=summary,category=category,location=location,poster=path)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('books.html',form=form)

@main.route('/comment/new/<int:book_id>', methods = ['GET','POST'])
@login_required
def new_comment(book_id):
    form = CommentForm()
    book=Book.query.get(book_id)
    if form.validate_on_submit():
        summary = form.summary.data

        new_comment = Comment(summary = summary, user_id = current_user._get_current_object().id, book_id = book_id)
        db.session.add(new_comment)
        db.session.commit()


        return redirect(url_for('.new_comment', book_id= book_id))

    all_comments = Comment.query.filter_by(book_id = book_id).all()
    return render_template('comments.html', form = form, comment = all_comments, book = book )


@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()
    get_books = Book.query.filter_by(user_id = current_user.id).all()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user ,summary = get_books)

@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))

    return render_template('profile/update.html',form =form)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/book/upvote/<int:book_id>/upvote', methods = ['GET', 'POST'])
@login_required
def upvote(book_id):
    book = Book.query.get(book_id)
    user = current_user
    book_upvotes = Upvote.query.filter_by(book_id= book_id)
    
    if Upvote.query.filter(Upvote.user_id==user.id,Upvote.book_id==book_id).first():
        return  redirect(url_for('main.index'))


    new_upvote = Upvote(book_id=book_id, user = current_user)
    new_upvote.save_upvotes()
    return redirect(url_for('main.index'))

@main.route('/details/<id>')
def details(id):
	'''
	View Function that returns the book's page and details about the book.
	'''
	books = Book.query.filter_by(id = id).all()
	title = f'Book details'

	return render_template('details.html',title=title,books = books)        

@main.route('/book/contact', methods = ['GET','POST'])
def contactus():
    form = ContactForm()
    '''
    View root page function that returns the index page and its data
    '''

    return render_template('contact.html',form=form)

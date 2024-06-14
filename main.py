from flask import Flask, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
import os

app = Flask(__name__)

# Configure the SQLite database, relative to the app instance folder
db_path = os.path.join(os.getcwd(), 'new-books-collection.db')
print(f'Database will be created at: {db_path}')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications

db = SQLAlchemy(app)

# defines the Book model (modern approach, with Type Checking):
class Book(db.Model):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

# The traditional style of the Book model above:
# class Book(db.Model):
#     __tablename__ = 'books'
#     id = db.Column(Integer, primary_key=True)
#     title = db.Column(String(250), nullable=False, unique=True)
#     author = db.Column(String(250), nullable=False)
#     rating = db.Column(Float, nullable=False)

with app.app_context():
    db.create_all()

    # Adds a new book entry if it doesn't exist already
    if not Book.query.filter_by(id=9).first():
        new_book = Book(id=9, title="The 5 People You Meet in Heaven", author="Mitch Albom", rating=9.0)
        db.session.add(new_book)
        db.session.commit()
        print("New book entry added.")
    else:
        print("Book entry already exists.")

# Creates the database tables and adds a new book entry
# with app.app_context():
#     new_book = Book(id=9, title="The 5 People You Meet in Heaven", author="Mitch Albom", rating=9.0)
#     db.session.add(new_book)
#     db.session.commit()
    # db.create_all()

    book_to_update = db.session.execute(db.select(Book).where(Book.title == "Harry Potter")).scalar()
    if book_to_update:
        book_to_update.title = "Harry Potter and the Chamber of Secrets"
        db.session.commit()
        print("The book title has been updated.")
    else:
        print("Book 'Harry Potter' not found.")

@app.route('/delete', methods=['POST'])
def delete_book():
    title = request.form['title']
    book_to_delete = db.session.execute(db.select(Book).where(Book.title == title)).scalar()
    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect(url_for('list_books'))
    else:
        return "This book was not found", 404

# Define a route to check the database
@app.route('/check_db')
def check_db():
    books = Book.query.all()
    return '<br>'.join([f'{book.id}: {book.title} by {book.author} (Rating: {book.rating})' for book in books])


# Define a route to add a book
@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    rating = request.form['rating']
    new_book = Book(title=title, author=author, rating=rating)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('list_books'))


# Define a route to list books
# (previous code) for list_books route:
# @app.route('/')
# def list_books():
#     books = Book.query.all()
#     return '<br>'.join([f'{book.title} by {book.author} (Rating: {book.rating})' for book in
#                         books]) + '<br><a href="/add_form">Add a new book</a>'

@app.route('/')
def list_books():
    books = Book.query.all()
    return render_template_string('''
        <h1>Siris's Book Collection</h1>
        <ul>
            {% for book in books %}
                <li>{{ book.title }} by {{ book.author }} (Rating: {{ book.rating }})</li>
            {% endfor %}
        </ul>
        <br><a href="/add_form">Add a new book</a>
        <br><a href="/delete_form">Delete a book</a>
    ''', books=books)

@app.route('/add_form')
def add_form():
    return '''
        <form action="/add" method="post">
            <label for="title">Book Name</label>
            <input type="text" id="title" name="title"><br>
            <label for="author">Book Author</label>
            <input type="text" id="author" name="author"><br>
            <label for="rating">Book Rating</label>
            <input type="text" id="rating" name="rating"><br>
            <button type="submit">Add Book</button>
        </form>
    '''

@app.route('/delete_form')
def delete_form():
    return '''
        <form action="/delete" method="post">
            <label for="title">Title</label>
            <input type="text" id="title" name="title"><br>
            <button type="submit">Delete Book</button>
        </form>
    '''

@app.route('/edit_rating', methods=['POST'])
def edit_rating():
    return '''
        <form action="/edit" method="post">
    '''

if __name__ == '__main__':
    app.run(debug=True)

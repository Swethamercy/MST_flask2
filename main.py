from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask.helpers import stream_with_context
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='msttemplates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)


books = [{
    'id': 1,
    'title': 'Flask 101',
    'author': 'John Doe'
}, {
    'id': 2,
    'title': 'Python Web Development',
    'author': 'Jane Smith'
}]


# Default route
@app.route('/')
def hello():
    return 'Hello, Flask!'


# Read all books
@app.route('/books', methods=['GET'])
def get_books():
    books = db.session.query(Book).all()  # SELECT * FROM books
    return render_template('book_list.html', books=books)


# Read a specific book
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = db.session.query(Book).filter_by(id=book_id).first()
    if book:
        return render_template('book_detail.html', book=book)
    return jsonify({'message': 'Book not found'}), 404


# Delete a specific book
@app.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = db.session.query(Book).filter_by(id=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('get_books'))
    return jsonify({'message': 'Book not found'}), 404


# Display form to create a book
@app.route('/books/new', methods=['GET'])
def add_book_form():
    return render_template('add_book.html')


# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    try:
        title = request.form['title']
        author = request.form['author']
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('get_books'))
    except Exception as e:
        print(f"Error creating book: {e}")
        return jsonify({'message': 'Error creating book'}), 500


# Edit a specific book
@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = db.session.query(Book).filter_by(id=book_id).first()
    if request.method == 'GET':
        if book:
            return render_template('edit_book.html', book=book)
        return jsonify({'message': 'Book not found'}), 404

    try:
        book.title = request.form['title']
        book.author = request.form['author']
        db.session.commit()
        return redirect(url_for('get_books'))
    except Exception as e:
        print(f"Error editing book: {e}")
        return jsonify({'message': 'Error editing book'}), 500


# Confirmation before deleting a book
@app.route('/books/<int:book_id>/confirm-delete', methods=['GET'])
def confirm_delete(book_id):
    book = db.session.query(Book).filter_by(id=book_id).first()
    if book:
        return render_template('delete_book.html', book=book)
    return jsonify({'message': 'Book not found'}), 404


# Populate the database with data from the variable books
@app.route('/books/populate', methods=['GET'])
def populate_books():
    for book_data in books:
        book_id = book_data['id']
        existing_book = db.session.query(Book).filter_by(id=book_id).first()

        # Check if the book with the given id already exists in the database
        if not existing_book:
            title = book_data['title']
            author = book_data['author']
            new_book = Book(id=book_id, title=title, author=author)
            db.session.add(new_book)
            db.session.commit()
        else:
            # Handle the case where a book with the same id already exists
            print(
                f"Book with id {book_id} already exists. Skipping insertion ..."
            )

    return redirect(url_for('get_books'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000)

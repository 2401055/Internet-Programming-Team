from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
import os

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'
# Using SQLite for local development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rst_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    studentId = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    memberSince = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    coverImage = db.Column(db.String(255), default='https://via.placeholder.com/150x200?text=No+Cover')
    addedDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

# Association Tables for Favorites and Event Registration
user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True)
)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    issueType = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    createdAt = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(
        fullName=data['fullName'],
        email=data['email'],
        studentId=data.get('studentId', ''),
        password=data['password']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        token = jwt.encode({
            'email': user.email, 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/books', methods=['GET'])
def get_books():
    search = request.args.get('search', '').lower()
    category = request.args.get('category', 'All')
    
    query = Book.query
    if category != 'All':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Book.title.ilike(f'%{search}%') | Book.author.ilike(f'%{search}%'))
    
    books_list = query.all()
    return jsonify([{
        "id": b.id, "title": b.title, "author": b.author, 
        "category": b.category, "coverImage": b.coverImage
    } for b in books_list])

@app.route('/api/events', methods=['GET'])
def get_events():
    events_list = Event.query.all()
    return jsonify([{
        "id": e.id, "title": e.title, "description": e.description,
        "date": e.date.strftime('%Y-%m-%d'), "time": e.time, "location": e.location
    } for e in events_list])

@app.route('/api/user/favorites', methods=['GET', 'POST'])
def handle_favorites():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Missing token"}), 401
    
    token = auth_header.split()[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = User.query.filter_by(email=data['email']).first()
        
        if request.method == 'POST':
            book_id = request.json.get('bookId')
            book = Book.query.get(book_id)
            if book and book not in user_fav_books(user):
                # Add to favorites logic
                stmt = user_favorites.insert().values(user_id=user.id, book_id=book.id)
                db.session.execute(stmt)
                db.session.commit()
            return jsonify({"message": "Added to favorites"})
        else:
            fav_books = user_fav_books(user)
            return jsonify([{
                "id": b.id, "title": b.title, "author": b.author, "coverImage": b.coverImage
            } for b in fav_books])
    except Exception as e:
        return jsonify({"message": "Invalid token", "error": str(e)}), 401

def user_fav_books(user):
    # Helper to get favorite books for a user
    return db.session.query(Book).join(user_favorites).filter(user_favorites.c.user_id == user.id).all()

@app.route('/api/complaints', methods=['POST'])
def complaints():
    data = request.json
    new_complaint = Complaint(
        issueType=data.get('issueType'),
        message=data.get('message')
    )
    db.session.add(new_complaint)
    db.session.commit()
    return jsonify({"message": "Complaint received"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

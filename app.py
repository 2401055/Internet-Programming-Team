from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

# Mock data
users = []
books = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "coverImage": "https://via.placeholder.com/150x200?text=Gatsby"},
    {"id": 2, "title": "1984", "author": "George Orwell", "coverImage": "https://via.placeholder.com/150x200?text=1984"},
    {"id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee", "coverImage": "https://via.placeholder.com/150x200?text=Mockingbird"},
    {"id": 4, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "coverImage": "https://via.placeholder.com/150x200?text=Catcher"},
]
events = [
    {"id": 1, "title": "Book Club Meeting", "description": "Discussing The Great Gatsby", "date": "2026-06-01", "time": "18:00", "location": "Library Hall"},
    {"id": 2, "title": "Author Talk", "description": "A talk by a local author", "date": "2026-06-15", "time": "19:00", "location": "Online"},
]
favorites = {}

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    users.append(data)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = next((u for u in users if u['email'] == data['email'] and u['password'] == data['password']), None)
    if user:
        token = jwt.encode({'email': user['email'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/user/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization').split()[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = next((u for u in users if u['email'] == data['email']), None)
        return jsonify(user)
    except:
        return jsonify({"message": "Invalid token"}), 401

@app.route('/api/books', methods=['GET'])
def get_books():
    search = request.args.get('search', '').lower()
    category = request.args.get('category', 'All')
    filtered_books = [b for b in books if search in b['title'].lower() or search in b['author'].lower()]
    return jsonify(filtered_books)

@app.route('/api/events', methods=['GET'])
def get_events():
    return jsonify(events)

@app.route('/api/user/favorites', methods=['GET', 'POST'])
def handle_favorites():
    token = request.headers.get('Authorization').split()[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        email = data['email']
        if request.method == 'POST':
            book_id = request.json.get('bookId')
            if email not in favorites:
                favorites[email] = []
            if book_id not in favorites[email]:
                favorites[email].append(book_id)
            return jsonify({"message": "Added to favorites"})
        else:
            user_favs = favorites.get(email, [])
            fav_books = [b for b in books if b['id'] in user_favs]
            return jsonify(fav_books)
    except:
        return jsonify({"message": "Invalid token"}), 401

@app.route('/api/complaints', methods=['POST'])
def complaints():
    return jsonify({"message": "Complaint received"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

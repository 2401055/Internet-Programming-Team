"""
FashionHub Backend - Flask Application
A complete e-commerce platform API
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
# Use absolute path for SQLite database to avoid issues in different environments
db_path = os.environ.get('DATABASE_PATH', os.path.join(os.getcwd(), 'fashionhub.db'))
app.config['DATABASE'] = db_path
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app, resources={r'/api/*': {'origins': '*', 'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], 'allow_headers': ['Content-Type', 'Authorization']}}, supports_credentials=True)

# ==================== Database Functions ====================

def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database from schema"""
    db = get_db()
    with open('database.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    db.close()

def query_db(query, args=(), one=False):
    """Execute a query and return results"""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute a query and commit"""
    db = get_db()
    db.execute(query, args)
    db.commit()
    db.close()

# ==================== Authentication ====================

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# ==================== User Routes ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    
    # Check if user exists
    existing = query_db('SELECT * FROM users WHERE email = ? OR username = ?', 
                       (email, username), one=True)
    if existing:
        return jsonify({'message': 'User already exists'}), 409
    
    # Hash password and create user
    hashed_password = generate_password_hash(password)
    try:
        execute_db('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                  (username, email, hashed_password))
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data['email']
    password = data['password']
    
    user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['user_id'],
        'username': user['username'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email']
        }
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user_id):
    """Logout user (client-side token deletion)"""
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    """Get user profile"""
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    user = query_db('SELECT user_id, username, email, address FROM users WHERE user_id = ?',
                   (user_id,), one=True)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(dict(user)), 200

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user_id, user_id):
    """Update user profile"""
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'address' in data:
        execute_db('UPDATE users SET address = ? WHERE user_id = ?',
                  (data['address'], user_id))
    
    return jsonify({'message': 'User updated successfully'}), 200

# ==================== Product Routes ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional category filter"""
    category_id = request.args.get('category_id', type=int)
    
    if category_id:
        products = query_db('''
            SELECT p.product_id, p.name, p.price, p.stock_qty, p.category_id, 
                   p.image, p.description, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.category_id = ?
            ORDER BY p.product_id
        ''', (category_id,))
    else:
        products = query_db('''
            SELECT p.product_id, p.name, p.price, p.stock_qty, p.category_id, 
                   p.image, p.description, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_id
        ''')
    
    return jsonify([dict(p) for p in products]), 200

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product"""
    product = query_db('''
        SELECT p.product_id, p.name, p.price, p.stock_qty, p.category_id, 
               p.image, p.description, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = ?
    ''', (product_id,), one=True)
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    return jsonify(dict(product)), 200

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """Search products by name"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'message': 'Search query required'}), 400
    
    products = query_db('''
        SELECT p.product_id, p.name, p.price, p.stock_qty, p.category_id, 
               p.image, p.description, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.name LIKE ?
        ORDER BY p.product_id
    ''', (f'%{query}%',))
    
    return jsonify([dict(p) for p in products]), 200

# ==================== Category Routes ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = query_db('SELECT * FROM categories ORDER BY category_id')
    return jsonify([dict(c) for c in categories]), 200

# ==================== Cart Routes ====================

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get shopping cart from session"""
    cart = session.get('cart', {})
    
    # Enrich cart with product details
    cart_items = []
    for product_id, quantity in cart.items():
        product = query_db('SELECT * FROM products WHERE product_id = ?', 
                          (int(product_id),), one=True)
        if product:
            cart_items.append({
                'product_id': int(product_id),
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'subtotal': product['price'] * quantity
            })
    
    total = sum(item['subtotal'] for item in cart_items)
    
    return jsonify({
        'items': cart_items,
        'total': total,
        'item_count': len(cart_items)
    }), 200

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()
    
    if not data or 'product_id' not in data:
        return jsonify({'message': 'Product ID required'}), 400
    
    product_id = str(data['product_id'])
    quantity = data.get('quantity', 1)
    
    # Verify product exists
    product = query_db('SELECT * FROM products WHERE product_id = ?',
                      (int(product_id),), one=True)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    if product['stock_qty'] < quantity:
        return jsonify({'message': 'Insufficient stock'}), 400
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if product_id in session['cart']:
        session['cart'][product_id] += quantity
    else:
        session['cart'][product_id] = quantity
    
    session.modified = True
    
    return jsonify({'message': 'Item added to cart successfully'}), 200

@app.route('/api/cart/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    """Remove item from cart"""
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True
    
    return jsonify({'message': 'Item removed from cart'}), 200

@app.route('/api/cart', methods=['DELETE'])
def clear_cart():
    """Clear entire cart"""
    session['cart'] = {}
    session.modified = True
    return jsonify({'message': 'Cart cleared'}), 200

# ==================== Order Routes ====================

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user_id):
    """Create an order from cart"""
    data = request.get_json()
    
    if not data or 'shipping_address' not in data:
        return jsonify({'message': 'Shipping address required'}), 400
    
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'message': 'Cart is empty'}), 400
    
    # Calculate total
    total = 0
    order_items = []
    
    for product_id, quantity in cart.items():
        product = query_db('SELECT * FROM products WHERE product_id = ?',
                          (int(product_id),), one=True)
        if not product:
            return jsonify({'message': f'Product {product_id} not found'}), 404
        
        if product['stock_qty'] < quantity:
            return jsonify({'message': f'Insufficient stock for {product["name"]}'}), 400
        
        subtotal = product['price'] * quantity
        total += subtotal
        order_items.append({
            'product_id': int(product_id),
            'quantity': quantity,
            'price': product['price']
        })
    
    try:
        # Create order
        db = get_db()
        cursor = db.execute(
            'INSERT INTO orders (user_id, total_amount, shipping_address, status) VALUES (?, ?, ?, ?)',
            (current_user_id, total, data['shipping_address'], 'Pending')
        )
        order_id = cursor.lastrowid
        
        # Add order items
        for item in order_items:
            db.execute(
                'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                (order_id, item['product_id'], item['quantity'], item['price'])
            )
            # Update stock
            db.execute(
                'UPDATE products SET stock_qty = stock_qty - ? WHERE product_id = ?',
                (item['quantity'], item['product_id'])
            )
        
        db.commit()
        db.close()
        
        # Clear cart
        session['cart'] = {}
        session.modified = True
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order_id,
            'total': total
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Order creation failed: {str(e)}'}), 500

@app.route('/api/orders', methods=['GET'])
@token_required
def get_user_orders(current_user_id):
    """Get user's orders"""
    orders = query_db('''
        SELECT o.order_id, o.order_date, o.total_amount, o.status, o.shipping_address
        FROM orders o
        WHERE o.user_id = ?
        ORDER BY o.order_date DESC
    ''', (current_user_id,))
    
    return jsonify([dict(o) for o in orders]), 200

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user_id, order_id):
    """Get order details"""
    order = query_db('''
        SELECT o.order_id, o.order_date, o.total_amount, o.status, o.shipping_address
        FROM orders o
        WHERE o.order_id = ? AND o.user_id = ?
    ''', (order_id, current_user_id), one=True)
    
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    items = query_db('''
        SELECT oi.order_item_id, oi.product_id, oi.quantity, oi.price, p.name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    ''', (order_id,))
    
    order_dict = dict(order)
    order_dict['items'] = [dict(item) for item in items]
    
    return jsonify(order_dict), 200

# ==================== Health Check ====================

@app.route('/')
def index():
    """Serve the frontend"""
    return app.send_static_file('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'FashionHub API is running'}), 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

# ==================== Initialization ====================

# Initialize database if it doesn't exist (runs on import for Gunicorn)
if not os.path.exists(app.config['DATABASE']):
    with app.app_context():
        try:
            init_db()
            print(f"Database initialized at {app.config['DATABASE']}")
        except Exception as e:
            print(f"Error initializing database: {e}")

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Starting FashionHub API on http://0.0.0.0:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)

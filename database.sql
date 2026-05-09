-- FashionHub Database Schema
-- SQLite format

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_qty INTEGER DEFAULT 0,
    category_id INTEGER NOT NULL,
    image TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    status TEXT DEFAULT 'Pending',
    shipping_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert sample categories
INSERT OR IGNORE INTO categories (category_id, name, description) VALUES
(1, 'Men', 'Men Clothing'),
(2, 'Women', 'Women Clothing');

-- Insert real products
DELETE FROM products;
INSERT INTO products (product_id, name, price, stock_qty, category_id, image, description) VALUES
(1, 'Oversized-Fit Scuba T-Shirt-Cream', 29.99, 50, 1, 'https://image.hm.com/assets/hm/de/c3/dec3757daa998b0b948717553d72977b2b2c3242.jpg', 'Premium Oversized-Fit Scuba T-Shirt-Cream from H&M'),
(2, 'Baggy Denim Shorts-Denim gray', 29.99, 50, 1, 'https://image.hm.com/assets/hm/57/2b/572bdcb8b7c7f6956028101d85647a7c6edeb07f.jpg', 'Premium Baggy Denim Shorts-Denim gray from H&M'),
(3, 'Loose-Fit Printed Sleeveless T-Shirt-Black/Los Angeles', 29.99, 50, 1, 'https://image.hm.com/assets/hm/c3/80/c38093969f10db67af96f172b6e944c3e671bb7c.jpg', 'Premium Loose-Fit Printed Sleeveless T-Shirt-Black/Los Angeles from H&M'),
(4, 'Slim-Fit Linen Jacket-Light beige', 29.99, 50, 1, 'https://image.hm.com/assets/hm/3f/62/3f62e6d763adc4e1d1c101a987e7d063afa50c74.jpg', 'Premium Slim-Fit Linen Jacket-Light beige from H&M'),
(5, 'Regular-Fit Linen-Blend Polo Shirt-Beige/striped', 29.99, 50, 1, 'https://image.hm.com/assets/hm/e8/20/e820e710d521ca5f4bebd6d747dc07205d668114.jpg', 'Premium Regular-Fit Linen-Blend Polo Shirt-Beige/striped from H&M'),
(6, '3-Pack Relaxed Fit T-Shirts-White/dark gray/black', 29.99, 50, 1, 'https://image.hm.com/assets/hm/e5/fe/e5fe0241b1083c5ca4fa9dba05e9a5077176d53a.jpg', 'Premium 3-Pack Relaxed Fit T-Shirts-White/dark gray/black from H&M'),
(7, 'Regular-Fit Shorts-Dark teal', 29.99, 50, 1, 'https://image.hm.com/assets/hm/f3/ca/f3caf91416066c9ddee0c1e3c9622d19a118b850.jpg', 'Premium Regular-Fit Shorts-Dark teal from H&M'),
(8, 'Relaxed-Fit Printed Resort Shirt-Dark brown/leopard', 29.99, 50, 1, 'https://image.hm.com/assets/hm/c4/96/c4960580ff2bfc1f1eca62920ddd0588671d8977.jpg', 'Premium Relaxed-Fit Printed Resort Shirt-Dark brown/leopard from H&M'),
(9, 'Asymmetric Lace-Trimmed T-Shirt-White', 29.99, 50, 2, 'https://image.hm.com/assets/hm/ac/32/ac32ae3fd11b17eb3ed50787f490382e9927f17a.jpg', 'Premium Asymmetric Lace-Trimmed T-Shirt-White from H&M'),
(10, 'Tie-Detail A-Line Dress-Navy blue/striped', 29.99, 50, 2, 'https://image.hm.com/assets/hm/bd/2f/bd2f0e3c778181c7fc1f28520a5db7893c0da107.jpg', 'Premium Tie-Detail A-Line Dress-Navy blue/striped from H&M'),
(11, 'Linen-Blend Pants-Light beige', 29.99, 50, 2, 'https://image.hm.com/assets/hm/f2/25/f225f733bedee939e5d8b350ca582161ab9f81b3.jpg', 'Premium Linen-Blend Pants-Light beige from H&M'),
(12, 'Wide-cut Pull-on Pants-Cream/striped', 29.99, 50, 2, 'https://image.hm.com/assets/hm/c0/d5/c0d579324539f40b9c77b28051b8ca3f96f49336.jpg', 'Premium Wide-cut Pull-on Pants-Cream/striped from H&M'),
(13, 'Linen-Blend Bandeau Top-Light pink/floral', 29.99, 50, 2, 'https://image.hm.com/assets/hm/8a/3b/8a3b28da03eedaa5210c997712831d6ebefba239.jpg', 'Premium Linen-Blend Bandeau Top-Light pink/floral from H&M'),
(14, 'Asymmetric Lace-Trimmed T-Shirt-Dark brown', 29.99, 50, 2, 'https://image.hm.com/assets/hm/25/fd/25fd4bdfc118bef8780cfe4f82a75671b2d0e469.jpg', 'Premium Asymmetric Lace-Trimmed T-Shirt-Dark brown from H&M'),
(15, 'Printed T-Shirt-Light yellow/Gelato', 29.99, 50, 2, 'https://image.hm.com/assets/hm/85/25/8525c0ab008f2515cf9a2b58275f7b78abf72184.jpg', 'Premium Printed T-Shirt-Light yellow/Gelato from H&M'),
(16, 'Draped Wrap Skirt-Light pink', 29.99, 50, 2, 'https://image.hm.com/assets/hm/30/c2/30c24484290309955f9750897e74862b0566102c.jpg', 'Premium Draped Wrap Skirt-Light pink from H&M');

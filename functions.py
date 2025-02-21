import sqlite3
from datetime import datetime
import random
import json
import ast
from argon2 import PasswordHasher

ph = PasswordHasher()

# Check order status
def getStatus(code):
    code = int(code)
    status = ""
    if code == 0:
        status = "Ongoing"
    elif code == 1:
        status = "Ready"
    elif code == 2:
        status = "Received"
    else:
        status = "NA"
    return status

# Initialize database
def init_db():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_number INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            items TEXT NOT NULL,
            total_cost REAL NOT NULL,
            gst_amount REAL NOT NULL,
            total_cost_with_gst REAL NOT NULL,
            timestamp TEXT NOT NULL,
            status INTEGER NOT NULL DEFAULT 0,
            sap_id TEXT NOT NULL,
            razorpay_order_id TEXT,
            payment_status TEXT DEFAULT 'Pending'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_name TEXT PRIMARY KEY,
            item_price REAL NOT NULL
        )
    ''')
    add_default_admin_user(cursor)
    conn.commit()
    conn.close()
    add_default_items()

def add_default_admin_user(cursor):
    try:
        username = 'canteen.admin'
        password_hash = ph.hash('pass')
        cursor.execute('''
            INSERT OR IGNORE INTO users (id, username, password_hash)
            VALUES (1, ?, ?)
        ''', (username, password_hash))
    except sqlite3.IntegrityError:
        pass

def add_default_items():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    items = [
        ('Pizza', 90.00),
        ('Burger', 55.00),
        ('Pasta', 90.00),
        ('Salad', 45.00),
        ('Soda', 25.00),
        ('Coffee', 20.00),
        ('Idli', 30.00),
        ('Medu Vada', 35.00),
        ('Dosa', 35.00)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO items (item_name, item_price)
        VALUES (?, ?)
    ''', items)
    conn.commit()
    conn.close()

def get_items_from_db():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, item_price FROM items')
    rows = cursor.fetchall()
    conn.close()
    return [{'name': row[0], 'price': row[1]} for row in rows]

def place_order_in_db(name, sap_id, items, quantities):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, item_price FROM items')
    menu = {row[0]: row[1] for row in cursor.fetchall()}
    
    total_cost = sum(menu[item] * int(quantity) for item, quantity in zip(items, quantities))
    gst_amount = total_cost * 0.05
    total_cost_with_gst = total_cost + gst_amount
    
    order_number = random.randint(10000000, 99999999)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    items_list = list(zip(items, quantities))
    items_json = json.dumps(items_list)

    # Initialize razorpay_order_id and payment_status
    razorpay_order_id = None
    payment_status = 'Pending'

    cursor.execute('''
        INSERT INTO orders (order_number, name, items, total_cost, gst_amount, total_cost_with_gst, timestamp, status, sap_id, razorpay_order_id, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_number, name, items_json, total_cost, gst_amount, total_cost_with_gst, timestamp, 0, sap_id, razorpay_order_id, payment_status))
    conn.commit()
    conn.close()

    return order_number

def update_order_with_payment_details(order_number, razorpay_order_id):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders
        SET razorpay_order_id = ?
        WHERE order_number = ?
    ''', (razorpay_order_id, order_number))
    conn.commit()
    conn.close()

def get_order_details(order_number):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
    order = cursor.fetchone()
    conn.close()
    
    if order:
        (order_number, name, items_json, total_cost, gst_amount, total_cost_with_gst, timestamp, status, sap_id,
         razorpay_order_id, payment_status) = order
        items = json.loads(items_json)

        conn = sqlite3.connect('canteen.db')
        cursor = conn.cursor()
        cursor.execute('SELECT item_name, item_price FROM items')
        menu = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()

        return {
            'order_number': order_number,
            'name': name,
            'sap_id': sap_id,
            'items': items,
            'total_cost': total_cost,
            'gst_amount': gst_amount,
            'total_cost_with_gst': total_cost_with_gst,
            'timestamp': timestamp,
            'status': status,
            'menu': menu,
            'int': int,
            'orderStatus': getStatus(status),
            'razorpay_order_id': razorpay_order_id,
            'payment_status': payment_status
        }
    else:
        return None

def update_order_payment_status(razorpay_order_id, status):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders
        SET payment_status = ?
        WHERE razorpay_order_id = ?
    ''', (status, razorpay_order_id))
    conn.commit()
    conn.close()

def get_order_number_by_razorpay_id(razorpay_order_id):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT order_number FROM orders WHERE razorpay_order_id = ?', (razorpay_order_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None  # Handle cases where the order is not found

def update_order_status(order_number, new_status=2):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE order_number = ?', (new_status, order_number))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and ph.verify(user[0], password):
        return True
    return False

def validate_barcode(barcode_number):
    return barcode_number and len(barcode_number) == 8 and barcode_number.isdigit()

def get_all_orders():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE payment_status="Paid" ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    orders = []
    for row in rows:
        (order_number, name, items_json, total_cost, gst_amount, total_cost_with_gst, timestamp, status, sap_id,
         razorpay_order_id, payment_status) = row
        items = json.loads(items_json)
        orders.append({
            'order_number': order_number,
            'name': name,
            'items': items,
            'total_cost': total_cost,
            'gst_amount': gst_amount,
            'total_cost_with_gst': total_cost_with_gst,
            'timestamp': timestamp,
            'sap_id': sap_id,
            'status': status,
            'razorpay_order_id': razorpay_order_id,
            'payment_status': payment_status
        })
    return orders

# functions.py

def get_order_item_counts():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT items FROM orders')
    rows = cursor.fetchall()
    conn.close()
    
    item_counts = {}
    
    for row in rows:
        items_json = row[0]
        items = json.loads(items_json)  # items is a list of tuples: [(item_name, quantity), ...]
        
        for item_name, quantity in items:
            quantity = int(quantity)
            if item_name in item_counts:
                item_counts[item_name] += quantity
            else:
                item_counts[item_name] = quantity
    
    return item_counts

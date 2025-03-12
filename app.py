from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from functions import *
import random
from datetime import datetime
import os
import razorpay

app = Flask(__name__, static_url_path='')
razorpay_client = razorpay.Client(auth=("rzp_test_eSD2WPZpkAJ6V4", "isI5FAcqurKYMVMcpFNHAvG0"))

app.secret_key = 'your_secret_key'  # Secret key for session management

# Initialize database
init_db()

# Initialize server status variable
server_status = 'live'

@app.route('/')
def home():
    global server_status
    if server_status == 'off':
        return "Not accepting orders right now" #render_template('not_accepting_orders.html')
    else:
        return render_template('order.html')


@app.route('/api/items')
def get_items():
    items = get_items_from_db()
    return jsonify(items)

@app.route('/api/order', methods=['POST'])
def place_order():
    name = request.form['name']
    sap_id = request.form['sap_id']
    delivery_floor = request.form['delivery_floor']
    items = request.form.getlist('items')
    quantities = request.form.getlist('quantities')

    # Server-side validation for SAP ID
    if not sap_id.isdigit() or len(sap_id) != 11:
        error_message = "SAP ID must be exactly 11 digits."
        return render_template('order.html', error=error_message)

    # Place order and retrieve order details
    order_number = place_order_in_db(name, sap_id, items, quantities, delivery_floor)
    order = get_order_details(order_number)

    # Calculate amount in paise (Razorpay expects amount in smallest currency unit)
    amount_in_paise = int(order['total_cost_with_gst'] * 100)

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount_in_paise,
        currency='INR',
        payment_capture='1'
    ))
    razorpay_order_id = razorpay_order['id']

    # Update order with Razorpay order ID
    update_order_with_payment_details(order_number, razorpay_order_id)

    # Render payment page with necessary details
    return render_template('payment.html', 
                           order=order, 
                           razorpay_order_id=razorpay_order_id, 
                           razorpay_key= 'rzp_test_eSD2WPZpkAJ6V4')

@app.route('/payment/success', methods=['POST'])
def payment_success():
    # Retrieve payment details from Razorpay
    payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    signature = request.form.get('razorpay_signature')

    # Dictionary of parameters for signature verification
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        # Verify the payment signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Update order payment status to 'Paid' in the database
        update_order_payment_status(razorpay_order_id, 'Paid')

        # Retrieve the order number using the Razorpay order ID
        order_number = get_order_number_by_razorpay_id(razorpay_order_id)

        # Redirect to the bill page
        return redirect(url_for('show_bill', order_number=order_number))
    except razorpay.errors.SignatureVerificationError:
        # If verification fails, update payment status to 'Failed'
        update_order_payment_status(razorpay_order_id, 'Failed')
        return redirect(url_for('payment_failed'))


@app.route('/bill/<int:order_number>')
def show_bill(order_number):
    order = get_order_details(order_number)
    if order:
        return render_template('bill.html', **order, getStatus=getStatus)
    else:
        return "Order not found", 404

@app.route('/canteen/orders/')
def view_orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    global server_status
    return render_template('view_orders.html', server_status=server_status)


@app.route('/canteen/break_orders')
def break_orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Get the aggregated data from the database
    item_counts = get_order_item_counts()
    floor_items = get_order_item_counts_by_floor()
    
    return render_template('break_orders.html', item_counts=item_counts, floor_items=floor_items)

@app.route('/canteen/orders/details/<int:order_id>')
def order_details(order_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    order = get_order_details(order_id)
    if order:
        return render_template('order-details.html', **order)
    else:
        return "Order not found", 404

@app.route('/api/update_ready/<int:order_id>', methods=['POST'])
def update_ready(order_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    update_order_status(order_id, 1)
    return redirect(url_for('view_orders', order_id=order_id))

@app.route('/canteen/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            session['logged_in'] = True
            return redirect(url_for('view_orders'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/canteen/barcodescan/')
def barcodescan():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('barcodescan.html')

@app.route('/api/order_update_barcode/', methods=['POST'])
def scan_barcode():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    data = request.get_json()
    barcode_number = data.get('barcode_number')
    
    if barcode_number and len(barcode_number) == 8 and barcode_number.isdigit():
        order_id = int(barcode_number)
        update_order_status(order_id, new_status=2)  # Update the order status to 2
        return jsonify({"message": "Order status updated to 2"})
    else:
        return jsonify({'error': 'Invalid barcode number'}), 400

@app.route('/api/orders_view')
def orders_view():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    orders = get_all_orders()
    return jsonify(orders)

@app.route('/api/update_server_status', methods=['POST'])
def update_server_status():
    if 'logged_in' not in session:
        return jsonify({'success': False}), 401  # Unauthorized if not logged in

    status = request.form.get('status')
    global server_status
    if status in ['live', 'off']:
        server_status = status
        return jsonify({'success': True, 'status': server_status})
    else:
        return jsonify({'success': False}), 400  # Bad Request for invalid status


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port=80)
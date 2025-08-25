import os
import io
import base64
import cv2
import numpy as np
import pytesseract
import qrcode
import easyocr
import cv2
import easyocr
import pyqrcode
import os
import mysql.connector
from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

reader = easyocr.Reader(['en'])  

# Ensure necessary folders exist
os.makedirs("static/qrcodes", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
app.secret_key = 'your_secret_key'  # Used for session management

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost/parking_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded images

db = SQLAlchemy(app)

# Load EasyOCR Reader
reader = easyocr.Reader(['en'])

# Define Admin Model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# Define Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    slot = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Occupied')  # 'Occupied' or 'Available'

# Create tables if they don’t exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/parking')
def parking():
    location = request.args.get('location', 'Unknown Location')

    # Fetch booked slots from MySQL
    booked_cars = {b.slot for b in Booking.query.filter(Booking.slot.like('C%')).all()}  # Cars
    booked_bikes = {b.slot for b in Booking.query.filter(Booking.slot.like('B%')).all()}  # Bikes

    return render_template('parking_layout.html', location=location, booked_cars=booked_cars, booked_bikes=booked_bikes)

@app.route('/booking_form', methods=['GET'])
def booking_form():
    location = request.args.get('location')
    slot = request.args.get('slot')

    existing_booking = Booking.query.filter_by(slot=slot).first()
    if existing_booking:
        return f"<h3>Slot {slot} is already booked! Please choose another.</h3> <a href='/parking?location={location}'>Go Back</a>"

    return render_template('booking_form.html', location=location, slot=slot)

@app.route('/book', methods=['POST'])
def book_slot():
    location = request.form.get('location')
    slot = request.form.get('slot')
    name = request.form.get('name')
    vehicle_number = request.form.get('vehicle_number')
    contact = request.form.get('contact')

    existing_booking = Booking.query.filter_by(slot=slot).first()
    if existing_booking:
        return f"<h3>Slot {slot} is already booked! Please choose another.</h3> <a href='/parking?location={location}'>Go Back</a>"

    # Store booking details in MySQL
    new_booking = Booking(location=location, slot=slot, name=name, vehicle_number=vehicle_number, contact=contact)
    db.session.add(new_booking)
    db.session.commit()

    return redirect(url_for('ticket', booking_id=new_booking.id))

@app.route('/ticket')
def ticket():
    booking_id = request.args.get('booking_id')

    if not booking_id:
        return "<h3>Booking ID is missing!</h3> <a href='/'>Go Back</a>"

    booking = Booking.query.get(booking_id)

    if not booking:
        return "<h3>Booking not found!</h3> <a href='/'>Go Back</a>"

    return render_template('ticket.html', details=booking)

# Admin Authentication Routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid username or password. <a href='/admin'>Try Again</a>"

    return render_template('admin_login.html')

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            return "Username already taken. <a href='/admin/signup'>Try Again</a>"

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new admin
        new_admin = Admin(username=username, password_hash=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        return redirect(url_for('admin_login'))

    return render_template('admin_signup.html')





@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    total_bookings = Booking.query.count()
    booked_cars = Booking.query.filter(Booking.slot.like('C%')).all()
    booked_bikes = Booking.query.filter(Booking.slot.like('B%')).all()

    available_car_slots = 50 - len(booked_cars)
    available_bike_slots = 500 - len(booked_bikes)

    return render_template('admin_dashboard.html', 
                           username=session['admin'],
                           total_bookings=total_bookings, 
                           booked_cars=booked_cars, 
                           booked_bikes=booked_bikes, 
                           available_car_slots=available_car_slots, 
                           available_bike_slots=available_bike_slots)


@app.route('/admin/car-booking-history')
def car_booking_history():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    booked_cars = Booking.query.filter(Booking.slot.like('C%')).all()
    
    return render_template('car_booking_history.html', booked_cars=booked_cars)

@app.route('/admin/bike-booking-history')
def bike_booking_history():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    booked_bikes = Booking.query.filter(Booking.slot.like('B%')).all()
    
    return render_template('bike_booking_history.html', booked_bikes=booked_bikes)

@app.route('/admin/reports')
def reports():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    total_bookings = Booking.query.count()
    
    return render_template('reports.html', total_bookings=total_bookings)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# Number Plate Recognition & QR Code Generation

@app.route('/detect_plate', methods=['POST'])
def detect_plate():
    # example placeholder logic
    return "Detect plate endpoint working"


# Database Connection Function
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="parking"
        )
        return conn
    except mysql.connector.Error as err:
        print(f" Database Connection Error: {err}")
        return None

# Check if Plate Exists in Database
def check_plate_in_db(plate_number):
    conn = connect_db()
    if not conn:
        return None

    cursor = conn.cursor()
    print(f" Checking DB for plate: {plate_number}")

    # Ensure case insensitivity
    cursor.execute("SELECT * FROM vehicles WHERE UPPER(plate_number) = UPPER(%s)", (plate_number,))
    data = cursor.fetchone()
    conn.close()

    print(f" DB Query Result: {data}")
    return data


# Save Entry Data in Database
def save_entry(plate_number, qr_code):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    cursor.execute("INSERT INTO entries (plate_number, qr_code, status) VALUES (%s, %s, %s)",
                   (plate_number, qr_code, "occupied"))
    conn.commit()
    conn.close()

# Detect Number Plate from Image
def detect_number_plate(image_path):
    print(f" Processing Image: {image_path}")
    
    # Read Image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    # Apply preprocessing for better OCR
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Reduce noise
    edged = cv2.Canny(gray, 30, 200)  # Edge detection

    # OCR Read
    result = reader.readtext(gray, detail=True)  # Get text details

    best_plate = None
    best_confidence = 0

    # Select the best text with highest confidence
    for (bbox, text, confidence) in result:
        text = text.upper().replace(" ", "").replace("-", "").strip()  # Normalize format
        print(f" Detected: {text} (Confidence: {confidence:.2f})")  # Debugging

        if confidence > best_confidence:
            best_plate = text
            best_confidence = confidence

    if best_plate:
        print(f" Best Plate Detected: {best_plate}")
        return best_plate

    print(" No Plate Detected")
    return None



# Generate QR Code
def generate_qr_code(plate_number):
    qr = pyqrcode.create(plate_number)
    qr_path = f"static/qrcodes/{plate_number}.png"
    qr.png(qr_path, scale=6)
    return qr_path

# Home Page
@app.route('/')
def index():
    return render_template('index.html')
# Vehicle Entry Route (OCR + QR Code)


#compare noplate to database
@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if request.method == 'POST':
        file = request.files['image']
        file_path = os.path.join("static/uploads", file.filename)
        file.save(file_path)

        # Detect number plate
        plate_number = detect_number_plate(file_path)

        if plate_number:
            if check_plate_in_db(plate_number):
                qr_code_path = generate_qr_code(plate_number)  # Generate QR Code
                save_entry(plate_number, qr_code_path)  # Save in DB
                
                return jsonify({
                    "status": "success",
                    "plate_number": plate_number,
                    "message": " Number plate found in database",
                    "qr_code": qr_code_path
                })
            else:
                return jsonify({"status": "failed", "message": " Number plate not found in database"})
        else:
            return jsonify({"status": "failed", "message": " Number plate detection failed"})

    return render_template('entry.html')




#show no plate in screen
# @app.route('/entry', methods=['GET', 'POST'])
# def entry():
#     if request.method == 'POST':
#         file = request.files['image']
#         file_path = os.path.join("static/uploads", file.filename)
#         file.save(file_path)

#         # Detect number plate
#         plate_number = detect_number_plate(file_path)

#         if plate_number:
#             return jsonify({
#                 "status": "success",
#                 "detected_plate": plate_number,
#                 "message": " Number plate detected successfully"
#             })
#         else:
#             return jsonify({"status": "failed", "message": " Number plate detection failed"})

#     return render_template('entry.html')


# Admin Dashboard - Shows Parking Entries
@app.route('/dashboard')
def dashboard():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT plate_number, status FROM entries")
    entries = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', entries=entries)

# Vehicle Exit Route - Updates Parking Status
@app.route('/exit', methods=['GET', 'POST'])
def exit_vehicle():
    if request.method == 'POST':
        plate_number = request.form['plate_number']

        conn = connect_db()
        cursor = conn.cursor()

        # Check if the vehicle exists in the system
        cursor.execute("SELECT * FROM entries WHERE plate_number = %s", (plate_number,))
        result = cursor.fetchone()

        if result:
            cursor.fetchall()  # Ensure previous queries are read
            cursor.execute("UPDATE entries SET status = 'available' WHERE plate_number = %s", (plate_number,))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": f" Exit recorded for {plate_number}"})
        else:
            conn.close()
            return jsonify({"status": "failed", "message": " Vehicle not found in the parking system"})

    return render_template('exit.html')


if __name__ == '__main__':
    app.run(debug=True)

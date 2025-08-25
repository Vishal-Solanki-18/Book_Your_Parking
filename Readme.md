# 🚗 Parking Management System with Number Plate Recognition & QR Codes

An **intelligent parking management system** built with **Flask**, **MySQL**, **OpenCV**, and **EasyOCR**.
This project allows users to **book slots, generate tickets with QR codes, detect number plates via OCR, and manage parking status**.
It also includes an **Admin Panel** to manage bookings, view reports, and monitor parking availability.

---

## ✨ Features

### 🔑 User Features

* 📍 Select parking location and view available slots
* 📝 Fill booking form with **Name, Vehicle Number, Contact**
* 🎫 Auto-generate **Ticket** after booking
* 📷 Upload vehicle image → **Automatic Number Plate Detection (OCR)**
* 🔍 System verifies if the plate exists in the database
* 📡 QR Code generation for vehicle entry/exit
* 🚪 Vehicle exit updates parking slot availability

### 🛠️ Admin Features

* 🔐 Secure **Admin Authentication (Login & Signup)** with hashed passwords
* 📊 **Dashboard**: View total bookings, available slots (Cars/Bikes)
* 🚗 **Car Booking History** and 🏍️ **Bike Booking History**
* 📑 **Reports Page**: Summarize total bookings
* 📤 Admin logout

---

## 🛠️ Tech Stack

* **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
* **Database**: [MySQL](https://www.mysql.com/) (via SQLAlchemy & mysql-connector)
* **OCR**: [EasyOCR](https://github.com/JaidedAI/EasyOCR) + [OpenCV](https://opencv.org/)
* **QR Codes**: [pyqrcode](https://pypi.org/project/PyQRCode/)
* **Security**: Werkzeug (password hashing)
* **Frontend**: HTML, CSS, Bootstrap

---

## 📂 Project Structure

```
Parking_System/
│
├── app.py                        # Main Flask app
├── static/
│   ├── uploads/                   # Stores uploaded vehicle images
│   └── qrcodes/                   # Stores generated QR codes
├── templates/                     # HTML Templates
│   ├── home.html
│   ├── user.html
│   ├── parking_layout.html
│   ├── booking_form.html
│   ├── ticket.html
│   ├── admin_login.html
│   ├── admin_signup.html
│   ├── admin_dashboard.html
│   ├── car_booking_history.html
│   ├── bike_booking_history.html
│   ├── reports.html
│   ├── entry.html
│   ├── exit.html
│   └── dashboard.html
└── requirements.txt               # Dependencies
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Parking_System.git
cd Parking_System
```

### 2. Create & Activate Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install flask flask_sqlalchemy mysql-connector-python easyocr opencv-python pyqrcode pypng
```

### 4. Setup MySQL Database

* Create a database `parking_db` for bookings and admins.
* Create another database `parking` for OCR entries.

#### `parking_db` tables:

* **admins** → Stores admin credentials
* **bookings** → Stores user bookings (location, slot, vehicle\_number, contact, status)

#### `parking` tables:

* **vehicles** → Registered vehicles with valid plate numbers
* **entries** → Tracks vehicle entry/exit logs with QR codes

---

## ▶️ Running the Application

```bash
python app.py
```

Application will be available at:
👉 `http://127.0.0.1:5000/`

---

## 🖼️ Workflow

1. User selects **Parking Location**
2. Chooses an available slot → Fills booking form
3. System stores booking → Generates **Ticket**
4. On **entry**, user uploads vehicle image → OCR detects plate
5. If plate exists in DB → Generate **QR Code** & mark slot as **Occupied**
6. On **exit**, system scans QR/plate and marks slot as **Available**

---

## 🔐 Security Notes

* Admin passwords are **hashed** before storing.
* QR codes are generated per entry → prevents duplication.
* Session-based authentication for admins.

---

## 🛣️ Roadmap

* ✅ Booking & Ticket Generation
* ✅ Admin Dashboard with Reports
* ✅ Number Plate Recognition (OCR)
* ✅ QR Code Generation for Entry/Exit
* ⏳ Payment Gateway Integration
* ⏳ SMS/Email Notifications
* ⏳ Camera Integration for Live Feed OCR

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch (`feature-new-thing`)
3. Commit changes
4. Push & open a Pull Request


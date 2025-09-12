from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import sqlite3
import os
from uuid import uuid4
from utils.registration import *
from utils.functions import *
from flask_socketio import SocketIO

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'Freebies#12345'
socketio = SocketIO(app)

@app.route("/")
def landing_page():
    return render_template('landingpagehtml.html')

@app.route("/home")
def home_page():
    return render_template('landingpagehtml.html')

@app.route("/survey")
def survey_page():
    return render_template('surveypagehtml.html')

@app.route("/about")
def about_page():
    return render_template('aboutpagehtml.html')

@app.route("/destination")
def destination_page():
    return render_template('destinationpagehtml.html')

@app.route("/feedback")
def feedback_page():
    return render_template('feedbackpagehtml.html')

@app.route("/final")
def final_page():
    return render_template('fakefinalpagehtml.html')

@app.route("/menu")
def menu():
    # Optional cleanup for QR code in menu
    image_filename = session.pop('last_image', None)
    if image_filename:
        try:
            os.remove(os.path.join('static', image_filename))
        except OSError:
            pass  # File not found or already deleted

    return render_template('menupagehtml.html')


@app.route("/signin_page", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            res = initialize_database()
            c = res.cursor()
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            account = c.fetchone()
            res.close()

            print("Account:", account)  # Add this line for debugging

            if account is None or not bcrypt.checkpw(password.encode('utf-8'), account[3].encode('utf-8')):
                message = 'Incorrect email or password.'

                socketio.emit('Incorrect_email')
                return render_template('signinpagehtml.html', msg=message)

            session['email'] = email
            username = account[1]
            # Redirect to the 'buttonpage' route
            return redirect(url_for('menu'))
        except sqlite3.Error as e:
            return jsonify({'message': f'Database error: {str(e)}'}), 500

    return render_template('signinpagehtml.html')


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data_dict = {
        'from_field': request.form['from'],
        'to_field': request.form['to'],
        'guider_number': request.form['guider_number'],
        'destination_address': request.form['destination_address'],
        'destination_contact': request.form['destination_contact']
    }
    random_file_name = f"{uuid4()}.png"
    file_path = os.path.join('static', random_file_name)
    generate_qr_code(data_dict, file_path)
    session['last_image'] = random_file_name
    return render_template('qrcode.html', image_url=url_for('static', filename=random_file_name)) 
        
@app.route('/registration', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username, email, password = request.form.get('name'), request.form.get('email'), request.form.get('password')
        if not (username and email and password):
            return render_template('signuppagehtml.html', message='Please provide all required fields.')

        db = initialize_database()
        message, success = registration(username, email, password, db)
        if success:
            # Return JSON response for successful registration
            return jsonify({'success': True, 'username': username})
        else:
            return jsonify({'success': False, 'message': message}), 500 
    return render_template('signuppagehtml.html')
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

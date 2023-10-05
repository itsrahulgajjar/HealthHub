from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')

model = pickle.load(open('model.pkl', 'rb'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

###
# Define a new SQLAlchemy model for the health data
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    systolic_bp = db.Column(db.Integer, nullable=False)
    diastolic_bp = db.Column(db.Integer, nullable=False)
    blood_sugar = db.Column(db.Float, nullable=False)
    body_temp = db.Column(db.Integer, nullable=False)
    heart_rate = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)
###

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Define a function to generate the Matplotlib visualization
import matplotlib.pyplot as plt
from io import BytesIO
import base64
##
import time
##

def generate_visualization(Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate):
##
     # Generate a unique filename with a timestamp
    timestamp = int(time.time())  # Get the current timestamp
    filename = f'static/visualization_{timestamp}.png'
##
    plt.figure()
    x_labels = ['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate']
    values = [Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate]
    plt.bar(x_labels, values)
    plt.xlabel('Input Parameters')
    plt.ylabel('Values')
    plt.title('Live Visualization')
##
    ##buffer = BytesIO()
    ##plt.savefig(buffer, format='png')
    ##buffer.seek(0)

        # Save the Matplotlib figure with the unique filename
    plt.savefig(filename, format='png')
    plt.close()
##

     # Encode the BytesIO object as base64
    ##image_data = base64.b64encode(buffer.read()).decode('utf-8')

    ##plt.close()

    ##return image_data
##
    return filename
##

@app.route('/predict', methods=['POST'])
def predict_health():
    Age = int(request.form.get('Age'))
    SystolicBP = int(request.form.get('SystolicBP'))
    DiastolicBP = int(request.form.get('DiastolicBP'))
    BS = float(request.form.get('BS'))
    BodyTemp = int(request.form.get('BodyTemp'))
    HeartRate = int(request.form.get('HeartRate'))

    result = model.predict(np.array([Age,SystolicBP,DiastolicBP,BS,BodyTemp,HeartRate]).reshape(1,6))
    if result[0] == 1:
        result_str = 'Your Health is on Low Risk'
    elif result[0] == 2:
        result_str = 'Your Health is on Mid Risk'
    else:
        result_str = 'Your Health is on High Risk'

###
     # Create a new HealthData object and save it to the database
    health_data = HealthData(
        age=Age,
        systolic_bp=SystolicBP,
        diastolic_bp=DiastolicBP,
        blood_sugar=BS,
        body_temp=BodyTemp,
        heart_rate=HeartRate,
        result=result_str
    )

    db.session.add(health_data)
    db.session.commit()
###

     # Generate the Matplotlib visualization and get the image data
    image_data = generate_visualization(Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate)

    # Save the visualization image to the static folder
    ##with open('static/visualization.png', 'wb') as f:
    ##    f.write(base64.b64decode(image_data))

    #return str(result)
    return render_template('prediction.html', result=result_str, image_data=image_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

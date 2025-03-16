from django.shortcuts import render, HttpResponse, redirect
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
import pandas as pd
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# Home Page

def home(request):
    return render(request, 'home.html', {'user': request.user})

# File Upload

def upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()
        file_path = fs.save(file.name, file)

        request.session['recent_file'] = file.name
        return render(request, "upload.html", {"file_path": file_path})
    
    return render(request, 'upload.html')

# View Uploaded Data

import os
import pandas as pd
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

def view_data(request):
    file_name = request.session.get('recent_file')
    
    if not file_name:  # Check if the session key exists
        return HttpResponse("No recent file found in session")

    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    if not os.path.exists(file_path):  # Check if the file exists
        return HttpResponse("File not found")
    
    try:
        df = pd.read_csv(file_path)
        data = df.to_dict(orient='records')
        return render(request, 'view_data.html', {"data": data})
    except Exception as e:
        return HttpResponse(f"Error reading file: {str(e)}")

# User Authentication

def login_view(request):
    response = render(request, "login.html")  # Initial response rendering
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"  # Older browsers
    response["Expires"] = "0"  # Expire immediately

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "✅ Login successful!")
            return redirect("main")
        else:
            messages.error(request, "❌ Invalid username or password")

    return response



from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import Register  # Ensure correct import
from django.contrib.auth.hashers import make_password  # Secure passwords

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if username or email already exists
        if Register.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already taken. Please choose another.")
            return render(request, 'register.html')  # Stay on the page

        if Register.objects.filter(email=email).exists():
            messages.error(request, "❌ Email already registered. Try logging in.")
            return render(request, 'register.html')  # Stay on the page

        # Save new user with hashed password
        new_register = Register(
            name=name,
            username=username,
            phone=phone,
            email=email,
            password=make_password(password)  # Secure password storage
        )
        new_register.save()
        messages.success(request, "✅ Registration successful! You can now log in.")
        return redirect("login")

    return render(request, 'register.html')

# Main Page

def main(request):
    return render(request, "main.html")


# Data Cleaning Function

def data_cleaning(df):
    df.dropna(inplace=True)
    fuel_dict = {"Diesel": 0, "Petrol": 1, "LPG": 2, "CNG": 3}
    df.fuel = df.fuel.map(fuel_dict)

    seller_dict = {"Individual": 0, "Dealer": 1, "Trustmark Dealer": 2}
    df.seller_type = df.seller_type.map(seller_dict)

    t_dict = {"Manual": 0, "Automatic": 1}
    df.transmission = df.transmission.map(t_dict)

    owner_dict = {'First Owner': 0, 'Second Owner': 1, 'Third Owner': 2,
                  'Fourth & Above Owner': 3, 'Test Drive Car': 4}
    df.owner = df.owner.map(owner_dict)

    df['mileage'] = df.mileage.str.replace(" kmpl", "").str.replace(" km/kg", "").astype(float)
    df['engine'] = df.engine.str.replace(" CC", "").astype(int)
    df['max_power'] = df.max_power.str.replace(" bhp", "").astype(float)

    df.drop(['torque', 'name'], axis=1, inplace=True)
    return df

# Train ML Model

def train(request):
    file_name = request.session.get('recent_file')
    if not file_name:
        return render(request, 'train.html', {'message': 'No file uploaded for training.'})

    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    if not os.path.exists(file_path):
        return render(request, 'train.html', {'message': 'File not found!'})

    df = pd.read_csv(file_path)  # Load DataFrame

    if df.empty:
        return render(request, 'train.html', {'message': 'Uploaded file is empty!'})

    df = data_cleaning(df)  # Clean Data

    x = df.drop(columns=['selling_price'], axis=1)
    y = df['selling_price']

    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor()
    model.fit(xtrain, ytrain)  # Train model

    model_path = os.path.join(settings.MEDIA_ROOT, 'ml_model.pkl')  # Save model
    joblib.dump(model, model_path)

    return render(request, 'train.html', {'message': f'Model Trained Successfully! Saved at: {model_path}'})


# Predict Using ML Model

def predict(request):
    global df
    if request.method == "POST":
        year = int(request.POST["year"])
        km = float(request.POST["km"])
        fuel = int(request.POST["fuel"])
        seller_type = int(request.POST["seller_type"])
        transmission = int(request.POST["transmission"])
        owner = int(request.POST["owner"])
        mileage = float(request.POST["mileage"])
        engine = int(request.POST["engine"])
        max_power = float(request.POST["max_power"])
        seats = int(request.POST["seats"])

        model_path = os.path.join(settings.MEDIA_ROOT, 'ml_model.pkl')
        model = joblib.load(model_path)

        col = ['year', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner', 'mileage', 'engine', 'max_power', 'seats']
        input_data = pd.DataFrame([[year, km, fuel, seller_type, transmission, owner, mileage, engine, max_power, seats]], columns=col)
        prediction = model.predict(input_data)[0]

        return render(request, "predict.html", {"prediction": round(prediction, 2)})

    return render(request, "predict.html")


from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out!")
    return redirect('home')  # Replace 'home' with your desired redirect page

from django.contrib.auth.decorators import user_passes_test

# Function to check if the user is an admin
def is_admin(user):
    return user.is_superuser  # Only allow superusers (admin)

# View to redirect to /admin
@user_passes_test(is_admin)  # Only admins can access this view
def admin_dashboard(request):
    return redirect('/admin/')  # Redirect to Django Admin

def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")

def services(request):
    return render(request, "services.html")




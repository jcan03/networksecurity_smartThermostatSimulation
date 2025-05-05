# T00686800 Joel Canonico COMP 3260 Project 
from flask import Flask, render_template, request, jsonify, session
# using haslib, time, random, uuid, Fernet libraries for encryption, hashing, unique thermostat names, and dos attack simulations
import hashlib 
import time
import random
import uuid  
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # used for session encryption 

# generate an encryption key for simulating encrypted communications
key = Fernet.generate_key()
cipher = Fernet(key)

# security settings for the simulation; all are enabled by default.
security_enabled = {
    "acl": True,             # access control for resource permissions
    "login_validation": True,  # validate user login credentials
    "dos_protection": True     # block simulated DoS attacks if true
}

# users with hashed passwords, one admin and one attacker
users = {
    "user1": {"password": hashlib.sha256("password123".encode()).hexdigest(), "role": "admin"},
    "attacker": {"password": hashlib.sha256("hackerpass".encode()).hexdigest(), "role": "unauthorized"}
}

# in-memory storage for all thermostats (each with a unique id and temperature)
thermostats = {}

# create a default thermostat with a unique id and default temperature 21 degrees celcius
default_id = str(uuid.uuid4())
thermostats[default_id] = {"id": default_id, "temperature": 21}

# function to authenticate a user by comparing hashed passwords
def authenticate(username, password):
    user = users.get(username)
    if user and user["password"] == hashlib.sha256(password.encode()).hexdigest():
        return user["role"]
    return None

# render the homepage, passing current security settings (they can be changed on the different accounts and remain)
@app.route("/")
def index():
    return render_template("index.html", security=security_enabled)

# process login requests and store user info in session if user/pass are valid
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # if the security is enabled, then validation is needed
    if security_enabled["login_validation"]:
        role = authenticate(username, password)

        if role is None: # makes sure there is some role on the account
            return jsonify({"success": False, "message": "Invalid credentials."})
    else:
        role = "admin"

    session["username"] = username
    session["role"] = role
    return jsonify({"success": True, "role": role}) 

# clear session data when the user logs out
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

# update security settings based on what's been saved
@app.route("/update_security", methods=["POST"])
def update_security():
    data = request.json

    # for all 3 security measures, check if security is enabled or not and store the value
    for key_name in ["acl", "login_validation", "dos_protection"]:
        if key_name in data:
            security_enabled[key_name] = bool(data[key_name])
    return jsonify({"success": True, "security_enabled": security_enabled})

# list all thermostats in the system
@app.route("/list_thermostats", methods=["GET"])
def list_thermostats():
    return jsonify({"success": True, "thermostats": list(thermostats.values())})

# add a new thermostat, but only admin accounts can add
@app.route("/add_thermostat", methods=["POST"])
def add_thermostat():
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized: Only admin can add thermostats."}), 403
    
    # creates a new thermostat id with default temperature
    new_id = str(uuid.uuid4())
    thermostats[new_id] = {"id": new_id, "temperature": 21}
    return jsonify({"success": True, "thermostat": thermostats[new_id]})

# remove a specific thermostat from id, only admin users can do this
@app.route("/remove_thermostat", methods=["POST"])
def remove_thermostat():
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized: Only admin can remove thermostats."}), 403
    data = request.json

    # get the thermostat id based on which remove button was clicked, and remove it using pop
    thermostat_id = data.get("thermostat_id")
    if thermostat_id in thermostats:
        removed = thermostats.pop(thermostat_id)
        return jsonify({"success": True, "removed": removed})
    else:
        return jsonify({"success": False, "message": "Thermostat ID not found."}), 404 # in case there's some error

# set the temperature for a specified thermostat, only admin users can update
@app.route("/set_temperature", methods=["POST"])
def set_temperature():
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized: Only admin can set temperature."}), 403
    data = request.json

    # get the id
    thermostat_id = data.get("thermostat_id")
    if thermostat_id not in thermostats:
        return jsonify({"success": False, "message": "Thermostat ID not found."}), 404
    try:
        temp = int(data.get("temperature"))
    except (TypeError, ValueError): # in case there's some non numerical value inputted
        return jsonify({"success": False, "message": "Invalid temperature value."})
    
    MIN_TEMP, MAX_TEMP = 10, 25  # acceptable temperature range in celcius
    if temp < MIN_TEMP or temp > MAX_TEMP:
        return jsonify({
            "success": False, 
            "message": f"Temperature must be between {MIN_TEMP}°C and {MAX_TEMP}°C." # send message if number is not in range
        }), 400

    # if no errors or rules violated, update the temperature
    thermostats[thermostat_id]["temperature"] = temp
    message = f"Thermostat {thermostat_id} set to {temp}°C."
    return jsonify({"success": True, "message": message, "thermostat": thermostats[thermostat_id]})

# simulate a Denial-of-Service (DoS) attack with varying intensity
@app.route("/simulate_dos", methods=["GET"])
def simulate_dos():
    # create variables, intensity low by default
    intensity = request.args.get("intensity", "low")
    delay = 0
    packet_loss = 0

    # if protection is ON, simply say it's blocked
    if security_enabled["dos_protection"]:
        message = "DoS Attack Blocked: Protection is enabled."
        success = False

    # otherwise, do different delays and packet loss percentages based on some randomness
    else:
        if intensity == "low":
            delay = random.uniform(0.1, 0.3)
            packet_loss = random.uniform(0, 0.1)
        elif intensity == "medium":
            delay = random.uniform(0.3, 0.7)
            packet_loss = random.uniform(0.1, 0.3)
        elif intensity == "high":
            delay = random.uniform(0.7, 1.5)
            packet_loss = random.uniform(0.3, 0.7)
        else:
            message = "Invalid intensity choice"
            return jsonify({"success": False, "message": message})
        
        time.sleep(delay)  # simulate some random network delay
        if random.random() < packet_loss:  # simulate packet loss leading to attack drop (can randomly happen)
            message = "DoS Attack Dropped: Packet lost during attack."
            success = False
        else:
            message = f"DoS Attack Success: {int((1 - packet_loss) * 100)}% of packets got through!" # convert percent of packets getting through into whole number
            success = True

    return jsonify({"success": success, "message": message, "response_time": delay})

# simulate an unauthorized access attempt based on current security settings (default on)
@app.route("/simulate_unauthorized", methods=["GET"])
def simulate_unauthorized():
    if security_enabled["login_validation"] and security_enabled["acl"]: # if on, simply say blocked
        message = "Unauthorized Access Failed: Security measures are active."
        success = False
    else:
        message = "Unauthorized Access Success: Security measures are disabled." # if one or both off, say success
        success = True
    return jsonify({"success": success, "message": message})

if __name__ == "__main__":
    app.run(debug=True) 
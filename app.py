from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import ast, os, csv
from datetime import datetime
import json


app = Flask(__name__)
app.secret_key = "secret123"

DATA_FILE = "data/pets.csv"
REQUESTS_FILE = "data/requests.csv"

def save_pets(pets):
    """Save pets data back to JSON file."""
    os.makedirs("data", exist_ok=True)
    with open("data/pets.json", "w") as f:
        json.dump(pets, f, indent=4)
# ------------------ Ensure folders ------------------
os.makedirs("data", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

# ------------------ Ensure requests.csv exists ------------------
if not os.path.exists(REQUESTS_FILE):
    with open(REQUESTS_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pet_index", "user", "name", "email", "phone", "state", "place", "tal", "district", "datetime"])

# ------------------ Load pets dynamically ------------------
# def load_pets():
#     pets = []
#     if os.path.exists(DATA_FILE):
#         with open(DATA_FILE, newline="", encoding="utf-8") as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 try:
#                     if pd.notna(row.get("primary_photo_cropped", "")):
#                         photo_dict = ast.literal_eval(str(row["primary_photo_cropped"]))
#                         if isinstance(photo_dict, dict):
#                             row["PhotoURL"] = photo_dict.get("small", "/static/images/default.jpg")
#                         else:
#                             row["PhotoURL"] = "/static/images/default.jpg"
#                     else:
#                         row["PhotoURL"] = "/static/images/default.jpg"
#                 except:
#                     row["PhotoURL"] = "/static/images/default.jpg"
#                 pets.append(row)
#     return pets

def load_pets():
    pets = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Photo handling
                try:
                    if pd.notna(row.get("primary_photo_cropped", "")):
                        photo_dict = ast.literal_eval(str(row["primary_photo_cropped"]))
                        if isinstance(photo_dict, dict):
                            row["PhotoURL"] = photo_dict.get("small", "/static/images/default.jpg")
                        else:
                            row["PhotoURL"] = "/static/images/default.jpg"
                    else:
                        row["PhotoURL"] = "/static/images/default.jpg"
                except:
                    row["PhotoURL"] = "/static/images/default.jpg"

                # Convert nested string fields to dict
                for key in ["Breed", "Color", "Attributes", "Environment"]:
                    if key in row and isinstance(row[key], str):
                        try:
                            row[key] = ast.literal_eval(row[key])
                        except:
                            row[key] = {}

                pets.append(row)
    return pets


# ------------------ Read/Write requests ------------------
def read_requests():
    requests_list = []
    try:
        with open(REQUESTS_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                requests_list.append(row)
    except FileNotFoundError:
        pass
    return requests_list
# def save_requests_to_csv(requests):
#     fieldnames = ['pet_id','user','name','email','phone','state','place','tal','district','date','time','datetime']
#     with open(requests_file, 'w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#         for r in requests:
#             writer.writerow({
#                 'pet_id': r.get('pet_id') or r.get('pet_index', ''),
#                 'user': r.get('user', ''),
#                 'name': r.get('name', ''),
#                 'email': r.get('email', ''),
#                 'phone': r.get('phone', ''),
#                 'state': r.get('state', ''),
#                 'place': r.get('place', ''),
#                 'tal': r.get('tal', ''),
#                 'district': r.get('district', ''),
#                 'date': r.get('date', ''),
#                 'time': r.get('time', ''),
#                 'datetime': r.get('datetime', '')
#             })

def save_requests_to_csv(requests):
    fieldnames = ['pet_id','user','name','email','phone','state','place','tal','district','date','time','datetime']
    with open(REQUESTS_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for r in requests:
            writer.writerow({
                'pet_id': r.get('pet_id'),
                'user': r.get('user', ''),
                'name': r.get('name', ''),
                'email': r.get('email', ''),
                'phone': r.get('phone', ''),
                'state': r.get('state', ''),
                'place': r.get('place', ''),
                'tal': r.get('tal', ''),
                'district': r.get('district', ''),
                'date': r.get('date', ''),
                'time': r.get('time', ''),          # ✅ keep AM/PM format
                'datetime': r.get('datetime', '')   # ✅ keep AM/PM format
            })

# ------------------ Passwords ------------------
ADMIN_PASS = "123"
USER_PASS = "123"

# ------------------ Routes ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == ADMIN_PASS:
            session["user"] = "admin"
            return redirect(url_for("admin_dashboard"))
        elif username == "user" and password == USER_PASS:
            session["user"] = "user"
            return redirect(url_for("available_pets"))
        else:
            flash("Invalid Credentials!")
    return render_template("login.html")




# ------------------ User Pages ------------------
# @app.route("/available")
# def available_pets():
#     if session.get("user") != "user":
#         return redirect(url_for("login"))
#     pets = load_pets()
#     available = [p for p in pets if p.get("Status", "Available") == "Available"]
#     return render_template("available_pets.html", pets=available)

@app.route("/available")
def available_pets():
    user_role = session.get("user")
    if user_role not in ["user", "admin"]:
        return redirect(url_for("login"))

    pets = load_pets()
    available = [p for p in pets if p.get("Status", "Available") == "Available"]
    return render_template("available_pets.html", pets=available)

# @app.route("/adopted")
# def adopted_pets():
#     pets = load_pets()
#     requests = read_requests()
    
#     adopted = []
#     for pet in pets:
#         if pet.get("Status") == "Adopted":
#             adopter = next((r for r in requests if r["pet_name"] == pet["name"]), None)
#             if adopter:
#                 pet["AdoptedBy"] = adopter["name"]
#                 pet["Email"] = adopter["email"]
#                 pet["Phone"] = adopter["phone"]
#                 pet["Place"] = f"{adopter['place']}, {adopter['tal']}, {adopter['district']}"
#                 dt_parts = adopter["datetime"].split(" ")
#                 pet["Date"] = dt_parts[0]
#                 pet["Time"] = dt_parts[1]
#             else:
#                 pet["AdoptedBy"] = ""
#                 pet["Email"] = ""
#                 pet["Phone"] = ""
#                 pet["Place"] = ""
#                 pet["Date"] = "Not recorded"
#                 pet["Time"] = "Not recorded"
#             adopted.append(pet)
#     return render_template("adopted_pets.html", pets=adopted)
import ast
import ast
# @app.route("/adopted")
# def adopted_pets():
#     # Allow both user and admin to view
#     if session.get("user") not in ["user", "admin"]:
#         return redirect(url_for("login"))

#     pets = load_pets()  # load all pets from CSV
#     adopted = []

#     for pet in pets:
#         if pet.get("Status") == "Adopted":
#             # Ensure Name field exists
#             if not pet.get("Name"):
#                 pet["Name"] = pet.get("name") or "Unknown Pet"

#             # Parse AdoptedBy string into a dictionary if needed
#             adopted_by = pet.get("AdoptedBy")
#             if isinstance(adopted_by, str):
#                 try:
#                     pet["AdoptedBy"] = ast.literal_eval(adopted_by)
#                 except Exception:
#                     pet["AdoptedBy"] = None
#             adopted.append(pet)

#     return render_template("adopted_pets.html", pets=adopted)

# from datetime import datetime
# @app.route('/adopt/<int:pet_index>', methods=['GET', 'POST'])
# def adopt_pet(pet_index):
#     pets = load_pets()
#     if not (0 <= pet_index < len(pets)):
#         flash("Pet not found!", "error")
#         return redirect(url_for('available_pets'))
    
#     pet = pets[pet_index]

#     if request.method == 'POST':
#         adopter = {
#             'pet_id': pet_index,
#             'pet_name': pet.get('Name', 'Unknown'),
#             'user': session.get('user', 'Guest'),
#             'name': request.form.get('name', ''),
#             'email': request.form.get('email', ''),
#             'phone': request.form.get('phone', ''),
#             'state': request.form.get('state', ''),
#             'place': request.form.get('place', ''),
#             'tal': request.form.get('tal', ''),
#             'district': request.form.get('district', ''),
#             'date': datetime.now().strftime('%Y-%m-%d'),
#             'time': datetime.now().strftime('%I:%M:%S %p'),  # AM/PM format
#             'datetime': datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
#         }

#         # Save to CSV
#         requests_list = read_requests()
#         requests_list.append(adopter)
#         save_requests_to_csv(requests_list)

#         flash(f"You have successfully applied to adopt {pet.get('Name', 'pet')}!", "success")
#         return redirect(url_for('available_pets'))

#     return render_template("adopt_form.html", pet=pet)
from datetime import datetime

@app.route('/adopt/<int:pet_index>', methods=['GET', 'POST'])
def adopt_pet(pet_index):
    pets = load_pets()
    if not (0 <= pet_index < len(pets)):
        flash("Pet not found!", "error")
        return redirect(url_for('available_pets'))
    
    pet = pets[pet_index]

    if request.method == 'POST':
        now = datetime.now()
        adopter = {
            'pet_id': pet_index,
            'pet_name': pet.get('Name', 'Unknown'),
            'user': session.get('user', 'Guest'),
            'name': request.form.get('name', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'state': request.form.get('state', ''),
            'place': request.form.get('place', ''),
            'tal': request.form.get('tal', ''),
            'district': request.form.get('district', ''),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%I:%M:%S %p'),  # ✅ 12-hour AM/PM format
            'datetime': now.strftime('%Y-%m-%d %I:%M:%S %p')  # also in 12-hour format
        }

        # Save to CSV
        requests_list = read_requests()
        requests_list.append(adopter)
        save_requests_to_csv(requests_list)

        flash(f"You have successfully applied to adopt {pet.get('Name', 'pet')}!", "success")
        return redirect(url_for('available_pets'))

    return render_template("adopt_form.html", pet=pet)


# @app.route("/adopted")
# def adopted_pets():
#     if session.get("user") not in ["user", "admin"]:
#         return redirect(url_for("login"))

#     pets = load_pets()
#     requests = read_requests()
#     adopted = []

#     for pet in pets:
#         if pet.get("Status") == "Adopted":
#             # Ensure Name field exists
#             if not pet.get("Name"):
#                 pet["Name"] = pet.get("name") or "Unknown Pet"

#             # Parse AdoptedBy string if needed
#             adopted_by = pet.get("AdoptedBy")
#             if isinstance(adopted_by, str):
#                 try:
#                     adopted_by = ast.literal_eval(adopted_by)
#                 except Exception:
#                     adopted_by = None
#             # Convert time to 12-hour format with AM/PM
#             if adopted_by and adopted_by.get("time"):
#                 try:
#                     t = datetime.strptime(adopted_by["time"], "%H:%M")  # parse 24-hour
#                     adopted_by["time"] = t.strftime("%I:%M %p")          # convert to 12-hour
#                 except:
#                     pass
#             pet["AdoptedBy"] = adopted_by
#             adopted.append(pet)

#     return render_template("adopted_pets.html", pets=adopted)

# @app.route("/adopted")
# def adopted_pets():
#     # Allow both user and admin to view
#     if session.get("user") not in ["user", "admin"]:
#         return redirect(url_for("login"))

#     pets = load_pets()  # load all pets from CSV
#     adopted = []

#     for pet in pets:
#         if pet.get("Status") == "Adopted":
#             # Parse AdoptedBy string into a dictionary if needed
#             adopted_by = pet.get("AdoptedBy")
#             if isinstance(adopted_by, str):
#                 try:
#                     pet["AdoptedBy"] = ast.literal_eval(adopted_by)
#                 except Exception:
#                     pet["AdoptedBy"] = None
#             adopted.append(pet)

#     return render_template("adopted_pets.html", pets=adopted)

# @app.route("/adopted")
# def adopted_pets():
#     # ✅ Allow both user & admin to view
#     if session.get("user") not in ["user", "admin"]:
#         return redirect(url_for("login"))

#     pets = load_pets()
#     adopted = []

#     for pet in pets:
#         if pet.get("Status") == "Adopted":
#             # 🧩 If AdoptedBy is a string (from CSV), safely convert to dict
#             adopted_by = pet.get("AdoptedBy")
#             if isinstance(adopted_by, str):
#                 try:
#                     pet["AdoptedBy"] = ast.literal_eval(adopted_by)
#                 except Exception:
#                     pet["AdoptedBy"] = None
#             adopted.append(pet)

#     return render_template("adopted_pets.html", pets=adopted)


# @app.route("/adopted")
# def adopted_pets():
#     if session.get("user") != "user":
#         return redirect(url_for("login"))
#     pets = load_pets()
#     adopted = [p for p in pets if p.get("Status", "") == "Adopted"]
#     return render_template("adopted_pets.html", pets=adopted)

# @app.route("/pet/<int:pet_index>")
# def pet_detail(pet_index):
#     pets = load_pets()
#     if 0 <= pet_index < len(pets):
#         pet = pets[pet_index]
#         pet["index"] = pet_index
#         return render_template("pet_detail.html", pet=pet)
#     return "Pet not found", 404
# @app.route("/pet/<pet_name>")
# def pet_detail(pet_name):
#     pets = load_pets()
#     pet = next((p for p in pets if p["name"] == pet_name), None)
#     if pet:
#         return render_template("pet_detail.html", pet=pet)
#     else:
#         flash("Pet not found!", "error")
#         return redirect(url_for("available_pets"))
@app.route("/pet/<string:pet_name>")
def pet_detail(pet_name):
    pets = load_pets()
    for i, pet in enumerate(pets):
        if pet["name"] == pet_name:
            # ✅ Make a copy of pet and add index to it
            pet_detail = pet.copy()
            pet_detail["index"] = i
            return render_template("pet_detail.html", pet=pet_detail)
    flash("Pet not found!", "error")
    return redirect(url_for("available_pets"))

def adopt(pet_index):
    pets = load_pets()
    if not (0 <= pet_index < len(pets)):
        flash("Pet not found!", "error")
        return redirect(url_for('available_pets'))

    pet = pets[pet_index]

    if request.method == 'POST':
        adopter = {
            'pet_index': pet_index,
            'pet_name': pet.get('Name', pet.get('name', 'Unknown')),
            'user': session.get('user', 'Guest'),
            'name': request.form.get('name', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'state': request.form.get('state', ''),
            'place': request.form.get('place', ''),
            'tal': request.form.get('tal', ''),
            'district': request.form.get('district', ''),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%I:%M:%S %p'),
            'datetime': datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        }

        # ✅ Save adoption request
        requests_list = read_requests()
        requests_list.append(adopter)
        save_requests_to_csv(requests_list)

        flash(f"You have successfully applied to adopt {pet.get('Name', 'pet')}!", "success")
        return redirect(url_for('available_pets'))

    return render_template("adopt_form.html", pet=pet)


# @app.route("/adopt/<int:pet_id>", methods=["GET", "POST"])
# def adopt(pet_id):
#     pets = pd.read_csv("data/pets.csv").to_dict("records")
#     pet = next((p for p in pets if p["id"] == pet_id), None)

#     if not pet:
#         flash("Pet not found!", "error")
#         return redirect(url_for("available_pets"))

#     if request.method == "POST":
#         user = session.get("user", "Guest")
#         name = request.form["name"]
#         email = request.form["email"]
#         phone = request.form["phone"]
#         state = request.form.get("state", "")
#         place = request.form.get("place", "")
#         tal = request.form.get("tal", "")
#         district = request.form.get("district", "")
#         now = datetime.now()

#         fieldnames = ['pet_index','user','name','email','phone','state','place','tal','district','date','time','datetime']

#         with open(requests_file, "a", newline="") as f:
#             writer = csv.DictWriter(f, fieldnames=fieldnames)
#             if f.tell() == 0:
#                 writer.writeheader()
#             writer.writerow({
#                 "pet_index": pet_id,  # ✅ use pet_index (not pet_id)
#                 "user": user,
#                 "name": name,
#                 "email": email,
#                 "phone": phone,
#                 "state": state,
#                 "place": place,
#                 "tal": tal,
#                 "district": district,
#                 "date": now.strftime("%Y-%m-%d"),
#                 "time": now.strftime("%H:%M:%S"),
#                 "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
#             })

#         flash("Adoption request submitted successfully!", "success")
#         return redirect(url_for("available_pets"))

#     return render_template("adopt_form.html", pet=pet)

# @app.route("/adopt/<pet_name>", methods=["GET", "POST"])
# def adopt_pet(pet_name):
#     pets = load_pets()
#     pet = next((p for p in pets if p["name"] == pet_name), None)
#     if not pet:
#         flash("Pet not found.")
#         return redirect(url_for("available_pets"))
    
#     if request.method == "POST":
#         adopter = {
#             "pet_name": pet_name,
#             "user": session.get("user"),
#             "name": request.form.get("name"),
#             "email": request.form.get("email"),
#             "phone": request.form.get("phone"),
#             "place": request.form.get("place"),
#             "tal": request.form.get("tal"),
#             "district": request.form.get("district"),
#             "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         }
#         requests_list = read_requests()
#         requests_list.append(adopter)
#         save_requests_to_csv(requests_list)

#         # Mark pet as adopted
#         pet["Status"] = "Adopted"
#         save_pets(pets)

#         flash(f"You have successfully adopted {pet_name}!")
#         return redirect(url_for("available_pets"))
    
#     return render_template("adopt_form.html", pet=pet)

# @app.route("/adopt/<pet_name>", methods=["GET", "POST"])
# def adopt_pet(pet_name):
#     if session.get("user") != "user":
#         return redirect(url_for("login"))
        
#     pets = load_pets()
#     pet = next((p for p in pets if p["name"] == pet_name), None)
#     if not pet:
#         flash("Pet not found.")
#         return redirect(url_for("available_pets"))

#     if request.method == "POST":
#         adopter = {
#             "pet_name": pet_name,
#             "user": session.get("user"),
#             "name": request.form.get("name"),
#             "email": request.form.get("email"),
#             "phone": request.form.get("phone"),
#             "state": request.form.get("state"),
#             "place": request.form.get("place"),
#             "tal": request.form.get("tal"),
#             "district": request.form.get("district"),
#             "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         }

#         requests_list = read_requests()
#         requests_list.append(adopter)
#         save_requests_to_csv(requests_list)
#         flash(f"Adoption request sent for {pet_name}!")
#         return redirect(url_for("available_pets"))

#     return render_template("adopt_form.html", pet=pet)


# ------------------ Admin Pages ------------------
@app.route("/admin")
def admin_dashboard():
    if session.get("user") != "admin":
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

@app.route("/admin/available")
def admin_available_pets():
    if session.get("user") != "admin":
        return redirect(url_for("login"))
    pets = load_pets()
    available = [p for p in pets if p.get("Status", "Available") == "Available"]
    return render_template("available_pets.html", pets=available)

# @app.route("/adopted")
# def adopted_pets():
#     if session.get("user") != "user":
#         return redirect(url_for("login"))
#     pets = load_pets()
#     adopted = [p for p in pets if p.get("Status") == "Adopted"]
#     return render_template("adopted_pets.html", pets=adopted)
# @app.route("/adopted")
# def adopted_pets():
#     # Allow both admin and user
#     if session.get("user") not in ["user", "admin"]:
#         return redirect(url_for("login"))

#     pets = load_pets()
#     adopted = []

#     for p in pets:
#         if p.get("Status") == "Adopted":
#             # Ensure AdoptedBy is a dictionary
#             adopter_info = p.get("AdoptedBy")
#             if isinstance(adopter_info, str):
#                 # If stored as string, convert to dict with only name
#                 adopter_info = {"name": adopter_info}

#             # Add missing keys to avoid template errors
#             adopter_info.setdefault("email", "N/A")
#             adopter_info.setdefault("phone", "N/A")
#             adopter_info.setdefault("place", "")
#             adopter_info.setdefault("tal", "")
#             adopter_info.setdefault("district", "")
#             adopter_info.setdefault("date", "Not recorded")
#             adopter_info.setdefault("time", "Not recorded")

#             pet_copy = p.copy()
#             pet_copy["AdoptedBy"] = adopter_info
#             adopted.append(pet_copy)

#     return render_template("adopted_pets.html", pets=adopted)
import ast
@app.route("/adopted")
def adopted_pets():
    if session.get("user") not in ["user", "admin"]:
        return redirect(url_for("login"))

    pets = load_pets()
    adopted = []

    for p in pets:
        if p.get("Status") == "Adopted":
            adopter_info = p.get("AdoptedBy", {})

            # Convert string representation of dict to actual dict
            if isinstance(adopter_info, str):
                try:
                    adopter_info = ast.literal_eval(adopter_info)
                except Exception:
                    adopter_info = {"name": adopter_info}

            # Ensure all keys exist
            for key in ["name","email","phone","state","place","tal","district","date","time"]:
                adopter_info.setdefault(key, "N/A" if key in ["email","phone","date","time"] else "")

            # ✅ Convert time to 12-hour format with AM/PM
            try:
                t = datetime.strptime(adopter_info["time"], "%H:%M:%S")
                adopter_info["time"] = t.strftime("%I:%M %p")  # 12-hour format
            except:
                pass  # leave as is if parsing fails

            p_copy = p.copy()
            p_copy["AdoptedBy"] = adopter_info
            adopted.append(p_copy)

    return render_template("adopted_pets.html", pets=adopted)

# @app.route("/adopted")
# def adopted_pets():
#     if session.get("user") not in ["user", "admin"]:
#         return redirect(url_for("login"))

#     pets = load_pets()
#     adopted = []

#     for p in pets:
#         if p.get("Status") == "Adopted":
#             adopter_info = p.get("AdoptedBy", {})

#             # Convert string representation of dict to actual dict
#             if isinstance(adopter_info, str):
#                 try:
#                     adopter_info = ast.literal_eval(adopter_info)
#                 except Exception:
#                     adopter_info = {"name": adopter_info}

#             # Ensure all fields exist
#             for key in ["name","email","phone","state","place","tal","district","date","time"]:
#                 adopter_info.setdefault(key, "N/A" if key in ["email","phone","date","time"] else "")

#             p_copy = p.copy()
#             p_copy["AdoptedBy"] = adopter_info
#             adopted.append(p_copy)

#     return render_template("adopted_pets.html", pets=adopted)


@app.route("/admin/requests")
def admin_requests():
    if session.get("user") != "admin":
        return redirect(url_for("login"))
    requests_list = read_requests()
    pets = load_pets()
    return render_template("admin_requests.html", requests=requests_list, pets=pets)
    
@app.route("/approve/<int:req_index>")
def approve_request(req_index):
    if session.get('user') != 'admin':
        return redirect(url_for('login'))

    requests_list = read_requests()
    if 0 <= req_index < len(requests_list):
        req = requests_list.pop(req_index)
        pet_id = int(req.get('pet_id') or req.get('pet_index', -1))

        df = pd.read_csv("data/pets.csv")

        pet_row = df[df['id'] == pet_id]
        if pet_row.empty:
            flash("⚠️ Invalid pet reference. Cannot approve request.")
            return redirect(url_for('admin_requests'))

        pet_index = pet_row.index[0]

        # ✅ Update pet info with adopter details
        df.at[pet_index, 'Status'] = 'Adopted'
        df.at[pet_index, 'AdoptedBy'] = str({
            'name': req.get('name', ''),
            'email': req.get('email', ''),
            'phone': req.get('phone', ''),
            'state': req.get('state', ''),
            'district': req.get('district', ''),
            'tal': req.get('tal', ''),
            'place': req.get('place', ''),
            'date': req.get('date', ''),
            'time': req.get('time', '')
        })

        # ✅ Save updated data
        df.to_csv("data/pets.csv", index=False)
        save_requests_to_csv(requests_list)

        global pets_list
        pets_list = df.to_dict(orient='records')

        flash(f"✅ Adoption approved for {df.loc[pet_index, 'name']}!")

    return redirect(url_for('admin_requests'))

# @app.route("/approve/<int:req_index>")
# def approve_request(req_index):
#     if session.get("user") != "admin":
#         return redirect(url_for("login"))

#     requests_list = read_requests()
#     pets = load_pets()

#     if 0 <= req_index < len(requests_list):
#         req = requests_list.pop(req_index)
#         idx = int(req["pet_index"])
#         if 0 <= idx < len(pets):
#             pets[idx]["Status"] = "Adopted"
#             pets[idx]["AdoptedBy"] = req["name"]

#         flash(f"Adoption of {pets[idx]['name']} approved!")

#     save_requests_to_csv(requests_list)
#     return redirect(url_for("admin_requests"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

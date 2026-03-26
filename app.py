from flask import Flask, render_template, request, redirect
import json, os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": [], "meals": []}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")

@app.route("/")
@login_required
def index():
    data = load_data()
    meals = [m for m in data["meals"] if m["user_id"] == current_user.id]
    return render_template("index.html", meals=meals)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = load_data()
        user = {
            "id": str(len(data["users"]) + 1),
            "username": request.form["username"],
            "password": request.form["password"]
        }
        data["users"].append(user)
        save_data(data)
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = load_data()
        for user in data["users"]:
            if user["username"] == request.form["username"] and user["password"] == request.form["password"]:
                login_user(User(user["id"]))
                return redirect("/")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/add", methods=["POST"])
@login_required
def add():
    data = load_data()

    file = request.files["image"]
    filename = ""

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    meal = {
        "id": len(data["meals"]) + 1,
        "name": request.form["name"],
        "calories": int(request.form["calories"]),
        "type": request.form["type"],
        "image": filename,
        "user_id": current_user.id
    }

    data["meals"].append(meal)
    save_data(data)

    return redirect("/")

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    data = load_data()
    data["meals"] = [m for m in data["meals"] if m["id"] != id]
    save_data(data)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
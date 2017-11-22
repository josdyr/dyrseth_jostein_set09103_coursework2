from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import json
import os


class User(object):

    def __init__(self, username, full_name, email, password):
        self.username = username
        self.full_name = full_name
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


user_logged_in = False
UPLOAD_FOLDER = '/Users/josdyr/university/modules/advanced_web_technologies/dyrseth_jostein_set09103_coursework2/static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
categories = ["Popular", "Dishes", "Drinks", "Healthy"]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# read .json recipes
with open('static/recipes.json') as in_file:
    recipes_dict = json.load(in_file)
    in_file.close()


@app.route('/')
def index():
    return redirect("/popular")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def do_search(recipes_dict, search_word):
    for key, value in recipes_dict:
        if search_word in key["title"]:
            return value


def map_form_to_recipes(form, filename):
    current_recipe = {}
    current_recipe["title"] = form["title"]
    current_recipe["description"] = form["description"]
    current_recipe["ingredients"] = form["ingredients"].split(",")
    current_recipe["method"] = form["method"].split(",")
    current_recipe["rating"] = form["rating"]
    current_recipe["cooking_time"] = form["cooking_time"]
    current_recipe["serves"] = form["serves"]
    current_recipe["difficulty"] = form["difficulty"]
    current_recipe["filename"] = filename
    return current_recipe


def map_to_user(form):
    current_reg_user2 = {}
    current_reg_user = User(form["user_name"], form["full_name"], form["email"], form["password"])
    current_reg_user2["username"] = current_reg_user.username
    current_reg_user2["full_name"] = current_reg_user.full_name
    current_reg_user2["email"] = current_reg_user.email
    current_reg_user2["pw_hash"] = current_reg_user.pw_hash
    return current_reg_user2


def map_to_only_user(current_user, current_password):
    current_reg_user = User(current_user["username"], current_user["full_name"],
                            current_user["email"], current_password)
    return current_reg_user


@app.route('/popular', methods=['GET', 'POST'])
def popular():

    # read .json users
    with open('static/users_info.json') as in_file:
        user_dict = json.load(in_file)
        in_file.close()

    if request.method == "POST" and "filename" in request.files:
        file = request.files['filename']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if request.method == "POST" and "title" in request.form:
        # append
        recipes_dict[request.form["title"]] = map_form_to_recipes(request.form, filename)

        # write dictionary to .json file
        with open('static/recipes.json', 'w') as outfile:
            json.dump(recipes_dict, outfile)

    # if Post and registered email is in the form / Login:
    if request.method == 'POST' and "reg_email" in request.form:

        # check if local file corresponds with the provided form values
        if request.form['reg_email'] in user_dict:

            user_current = user_dict[request.form["reg_email"]]
            current_password = request.form["reg_password"]

            user_current_object = map_to_only_user(user_current, current_password)

            if check_password_hash(user_current_object.pw_hash, current_password):
                print("Granted Access")
                user_logged_in = True
                return render_template("recipes.html", recipes_dict=recipes_dict, categorie=categories[0], user_logged_in=user_logged_in)

    elif request.method == 'POST' and "password" in request.form:  # if POST / Signup

        # append
        user_dict[request.form["email"]] = map_to_user(request.form)

        # write .json users
        with open('static/users_info.json', 'w') as outfile:
            json.dump(user_dict, outfile)

        # return thank you
        return render_template('thank_you.html')

    if request.method == "POST" and "reg_search" in request.input:
        print("DID SEARCH...")

    return render_template('recipes.html', recipes_dict=recipes_dict, categorie=categories[0])


@app.route('/<current_recipe>')
def current_recipe(current_recipe=None):
    return render_template("recipe.html", recipes_dict=recipes_dict, current_recipe=current_recipe)


@app.route('/dishes', methods=['GET', 'POST'])
def dishes():
    return render_template('recipes.html', recipes_dict=recipes_dict, categorie=categories[1])


@app.route('/drinks', methods=['GET', 'POST'])
def drinks():
    return render_template('recipes.html', recipes_dict=recipes_dict, categorie=categories[2])


@app.route('/healthy', methods=['GET', 'POST'])
def healthy():
    return render_template('recipes.html', recipes_dict=recipes_dict, categorie=categories[3])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

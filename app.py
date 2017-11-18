from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
import json
import pdb

app = Flask(__name__)


@app.route('/')
def index():
    return redirect("/recipes")


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():

    # read .json recipes
    with open('static/recipes.json') as in_file:
        recipes_dict = json.load(in_file)
        in_file.close()

    if request.method == "POST" and "title_of_recipe" in request.form:
        print("post recipe")

        # append
        recipes_dict[request.form["title_of_recipe"]] = request.form

        # write dictionary to .json file
        with open('static/recipes.json', 'w') as outfile:
            json.dump(recipes_dict, outfile)

        print(recipes_dict["title_of_recipe"])

    if request.method == "POST" and "user_name" in request.form:
        print("sign up")
    if request.method == "POST" and "reg_email" in request.form:
        print("log in")

    return render_template('recipes.html', recipes_dict=recipes_dict["j"])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

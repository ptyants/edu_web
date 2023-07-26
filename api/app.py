from flask import Flask, redirect, url_for, render_template, request, flash, session
from bardapi import Bard
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os


os.environ["_BARD_API_KEY"] ="YAhweL-TB02BIuIt3w7DiJKmQu2oHGwZdJOrtdjuXvbTqVa4dg0DdlJSDf2aOvmd1DX2qA."


app = Flask(__name__)

app.secret_key = "Key-chốnghacker-TB02BIuIt3w7DiJKmQu2oHGwZdJOrtdjuXvbTqVa4dg0DdlJSDf2aOvmd1DX2qA."
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fact.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "jfif"}

db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    fact_title = db.Column(db.String(20))
    fact = db.Column(db.String(200))
    img_fact = db.Column(db.String(100))

    def __init__(self, fact_title, fact, img_fact):
        self.fact_title = fact_title
        self.fact = fact
        self.img_fact = img_fact

@app.route('/')
def home():
    return  render_template("view_page.html", Dashboard=True)

@app.route("/chatbot")
def chatbot():
    #return render_template("index.html")
    return render_template("chatbot.html", Chatbot=True)

@app.route("/funfact")
def funfact():
    fact_index = int(request.args.get("fact_index", 0))
    facts = User.query.all()
    total_facts = len(facts)
    if total_facts > 0:
        current_fact_index = fact_index % total_facts
        prev_fact_index = (fact_index - 1) % total_facts
        next_fact_index = (fact_index + 1) % total_facts
        current_fact = facts[current_fact_index]
    else:
        current_fact_index = 0
        prev_fact_index = 0
        next_fact_index = 0
        current_fact = None
    return render_template(
        "funfact.html",
        current_fact=current_fact,
        current_fact_index=current_fact_index,
        prev_fact_index=prev_fact_index,
        next_fact_index=next_fact_index,
        funfactbutton=True
    )
    
    """if request.method == "POST":
        fact_title = request.form["fact_title"]
        fact = request.form["fact"]
        image = request.files["image"]
        if fact_title and fact and image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            new_fact = User(fact_title=fact_title, fact=fact, img_fact=filename)
            db.session.add(new_fact)
            db.session.commit()"""

    """facts = User.query.all()
    return render_template("funfact.html", facts=facts, funfact=True)"""
    
@app.route("/funfact/edit", methods=["GET", "POST"])    
def funfact_edit():
    if request.method == "POST":
        fact_title = request.form["fact_title"]
        fact = request.form["fact"]
        image = request.files["image"]
        
        """allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        if image and image.filename.split(".")[-1].lower() not in allowed_extensions:
            return "Invalid file format. Please choose an image file."
        """
        
        if fact_title and fact and image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            new_fact = User(fact_title=fact_title, fact=fact, img_fact=filename)
            db.session.add(new_fact)
            db.session.commit()
            
            return redirect(url_for("funfact", funfact=True))
    
    return render_template("funfact_edit.html", funfact=True)




    
@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    quest_user = str("Intructions: if the question is academically inclined then prompted Answer this question briefly and separate each idea with a \".\".  If the question is simple or just a polite greeting, just say hello back in a friendly manner, no further analysis is required.\nQuest: {}").format(userText)
    bot_replies = str(Bard().get_answer(quest_user)['content']).split(".")
    return ".\n".join(bot_replies)    





if __name__=="__main__":
    if not os.path.exists("fact.db"):
        with app.app_context():
            db.create_all()
            print("Created database!")
    app.run(debug=True)
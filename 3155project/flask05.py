# imports
import os                 # os is used to get environment variables IP & PORT
from flask import Flask   # Flask is the web app that we will customize
from flask import render_template # render the HTML
from flask import request # checking request
from flask import redirect, url_for # send the reuest to another function to complete response
from database import db
from models import Note as Note
from models import User as User
from forms import RegisterForm
import bcrypt
from flask import session

app = Flask(__name__)     # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_project_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = 'SE3155'
#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Setup models
with app.app_context():
    db.create_all()   # run under the app context

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page

@app.route('/')
@app.route('/index')
def index():
    #get user from database
    a_user = db.session.query(User).filter_by(email='user@uncc.edu').one()
    return render_template('index.html',user = a_user)

@app.route('/projects')
def get_projects():
    #retrieve user from database
    a_user = db.session.query(User).filter_by(email='user@uncc.edu').one()
    #retrieve notes from database
    my_notes = db.session.query(Note).all()
    return render_template('projects.html', notes=my_notes, user = a_user)

@app.route('/projects/<project_id>')
def get_project(project_id):
    #retrieve user from database
    a_user = db.session.query(User).filter_by(email='user@uncc.edu').one()
    #retrieve note from data base
    my_note = db.session.query(Note).filter_by(id=project_id).one()
    return render_template('project.html', note=my_note, user = a_user)

@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    #check method used for request
    if request.method == 'POST':
        # get title data
        title = request.form['title']
        #get note data
        text = request.form['projectText']
        # create date stamp
        from datetime import date
        today = date.today()
        #format date mm/dd/yyyy
        today = today.strftime("%m-%d-%y")
        new_record = Note(title, text, today)
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('get_projects'))
    else:
        #GET request - show new note from
        #request - show new not form
        a_user = db.session.query(User).filter_by(email='user@uncc.edu').one()
        return render_template('new.html', user=a_user)
    
@app.route('/projects/edit/<project_id>', methods=['GET', 'POST'])
def update_project(project_id):
    #check method used for request
    if request.method == 'POST':
        #get title data
        title = request.form['title']
        #get note data
        text = request.form['projectText']
        note = db.session.query(Note).filter_by(id=project_id).one()
        #update note data
        note.title = title
        note.text = text
        #update note in DB
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('get_projects'))
    else:
        #GET request - show new note form to edit note
        # retrieve user from database
        a_user = db.session.query(User).filter_by(email ='user@uncc.edu').one()
        # retrive note from database
        my_note = db.session.query(Note).filter_by(id=project_id).one()

        return render_template('new.html', note=my_note, user=a_user)

@app.route('/projects/delete/<project_id>', methods=['POST'])
def delete_project(project_id):
    #retrieve note from database
    my_note = db.session.query(Note).filter_by(id=project_id).one()
    db.session.delete(my_note)
    db.session.commit()
    return redirect(url_for('get_projects'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_notes'))

    # something went wrong - display register view
    return render_template('register.html', form=form)

app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=False)

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.


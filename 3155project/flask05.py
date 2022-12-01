# imports
import os                 # os is used to get environment variables IP & PORT
import bcrypt
from flask import Flask   # Flask is the web app that we will customize
from flask import render_template
from flask import request
from flask import redirect, url_for
from database import db
from models import User, Project
from flask import session
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm

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
    #check if a user is saved in session
    if session.get('user'):
        return render_template('index.html', user=session['user'])

    return render_template('index.html')

@app.route('/projects')
def get_projects():
    #check if saved in session
    if session.get('user'):
        #get notes from database
        my_projects = db.session.query(Project).filter_by(user_id=session['user_id']).all()

        return render_template('projects.html', projects=my_projects, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/projects/<project_id>')
def get_project(project_id):
    # check if saved in session
    if session.get('user'):
        #get note from database
        my_project = db.session.query(Project).filter_by(id=project_id, user_id=session['user_id']).one()

        form = CommentForm()

        return render_template('project.html', project=my_project, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))

@app.route('/projects/edit/<project_id>', methods=['GET', 'POST'])
def update_project(project_id):
    # check if a user is saved in session
    if session.get('user'):
    #check method used for request
        if request.method == 'POST':
            #get title
            title = request.form['title']
            #get note data
            text = request.form['projectText']
            project = db.session.query(Project).filter_by(id=project_id).one()
            #update note data
            project.title = title
            project.text = text
            #update note in db
            db.session.add(project)
            db.session.commit()

            return redirect(url_for('get_projects'))
        else:
            #get request - show new note form to edit note

            #get note from database
            my_project = db.session.query(Project).filter_by(id=project_id).one()

            return render_template('new.html', project=my_project, user=session['user'])
    else:
        #user is not in session redirect to login
        return redirect(url_for('login'))


@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    # check if a user is saved in session
    if session.get('user'):
    #check method used for request
        if request.method == 'POST':
            #get title data
            title = request.form['title']
            #get note data
            text = request.form['projectText']
            #create data stamp
            from datetime import date
            today = date.today()
            #format date mm/dd/yyyy
            today = today.strftime("%m-%d-%Y")
            new_record = Project(title, text, today, session['user_id'])
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_projects'))
        else:
            #Get request - show new note form

            return render_template('new.html', user=session['user'])
    else:
        #user is not in session redirect
        return redirect(url_for('login'))

@app.route('/projects/project/<project_id>')
def delete_project(project_id):
    # check if a user is saved in session
    if session.get('user'):
        #get note from database
        my_project = db.session.query(Project).filter_by(id=project_id).one()
        db.session.delete(my_project)
        db.session.commit()

        return redirect(url_for('get_projects'))
    else:
        #user is not signed in
        return redirect(url_for('login'))

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
        return redirect(url_for('get_projects'))

    # something went wrong - display register view
    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_projects'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

@app.route('/projects/<project_id>/comment', methods=['POST'])
def new_comment(project_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(project_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_project', project_id=project_id))

    else:
        return redirect(url_for('login'))

app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 8080)), debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.
from flask import Flask, render_template, redirect, request, flash, session, url_for
from model import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, ResetPasswordRequestForm, ResetPasswordForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized, NotFound


import secrets
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["SECRET_KEY"] = "abc123"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:17273185@localhost/feedback"
app.config["DEBUG"] = True # Enable Debug mode
app.config["SQLALCHEMY_ECHO"] = False

# Mail server address
app.config["MAIL_SERVER"] = "smtp.gmail.com"
# Port number for the mail server
app.config["MAIL_PORT"] = 587
# Use TLS 
app.config["MAIL_USE_TLS"] = True
# Use SSL (if True, set MAIL_USE_TLS to False)
app.config['MAIL_USE_SSL'] = False
# Your emaill address (for authentication)
app.config["MAIL_USERNAME"] = 'chowben956@gmail.com'
# Your email password (for authentication)
app.config['MAIL_PASSWORD'] = 'bc12345678'

mail = Mail(app)

connect_db(app)
with app.app_context():
    # Creating Tables with SQL Alchemy
    db.create_all()

@app.route('/')
def home_page():
    """ Homepage of the site """

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    """ Register a user """

    if "username" in session:
        return redirect(f"/users/{session["username"]}")

    form = UserForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)

        try: 
            db.session.commit()

        except IntegrityError: # sqlalchemy.exc.IntegrityError
            form.username.errors.append("Username taken. Please pick another.")
            return render_template("/users/register.html", form=form)
        
        session["username"] = new_user.username
        flash("Welcom! Successfully Created Your Account!", "success")
        return redirect(f"/users/{new_user.username}")
        
    return render_template('/users/register.html', form=form)

@app.route("/login", methods=["GET", "Post"])
def login_user():
    """ Handle login form """

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcom Back, {user.username}!", "primary")
            session["username"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]
    return render_template("/users/login.html", form = form)

@app.route("/users/<username>")
def show_user(username):
    """ Show a logged-in user page """

    # Check if the logged-in user matches the profile being viewed
    if "username" not in session or session["username"] != username:
        raise Unauthorized()
    
    # # This will automatically raise a 404 error
    user = User.query.get_or_404(username)
    return render_template("/users/users.html", user=user)

@app.route("/<username>/delete", methods=["POST"])
def delete_user(username):
    """ Delete a user and its feedbacks """

    # Check if the logged-in user matches the profile being viewed
    if "username" not in session or session["username"] != username:
        raise Unauthorized()
    
    # This will automatically raise a 404 error
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash("User Deleted", "danger")
    return redirect("/")

@app.route("/logout")
def logout_user():
    """ Logout user route """

    session.pop("username")
    flash("Goodbye", "info")
    return redirect("/")

# Display a form to add feedback  Make sure that only the user who is logged in can see this form.
@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def add_feedback(username):
    """ Handle add feedback form """

    if "username" not in session or session["username"] != username:
        raise Unauthorized()

    form = FeedbackForm()
    
    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=username)

        db.session.add(new_feedback)
        db.session.commit()
        flash("Feedback Created.", "success")
        return redirect(f"/users/{username}")

    return render_template("/feedback/new.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """ Handle edit feedback form """

    # # This will automatically raise a 404 error
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session["username"] != feedback.username:
        raise Unauthorized()

    # Pre-populate the form fields
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        flash("Feedback Updated.", "info")
        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit.html", form=form)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """ delete a feedback """

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session["username"] != feedback.username:
        raise Unauthorized()

    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback Deleted", "danger")

    return redirect(f"/users/{feedback.username}")


# Custom 404 handler
@app.errorhandler(NotFound)
def handle_404(e):
    """Custom 404 page."""
    return render_template('404.html', error=e), 404

# Custom 401 handler
@app.errorhandler(Unauthorized)
def handle_401(e):
    """Custom 401 page."""
    return render_template('401.html', error=e), 401


@app.route("/password-reset-request", methods=["GET", "POST"])
def request_reset_password():

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # if user exists
        if user:

            # Create and store reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            db.session.commit()

            # Send reset email
            msg = Message(
                subject="Password Reset Request",
                sender=user.email,
                recipients=[user.email]
            )
            msg.body = f"""
                To reset your password, visit the following link: 
                {url_for("reset_password", token=token, _external=True)}

            """
            # mail.send(msg)

            flash("Request Sent", "info")
        return redirect("/login")

    return render_template("/users/reset.html", form=form)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):

    user = User.query.filter_by(reset_token=token).first()

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password = User.hash_password(form.password.data)

        # Clear the token 
        user.reset_token = None
        db.session.commit()
        flash("Your password has been reset.", "success")
        return redirect("/login")

    return render_template("/users/reset-password.html", form=form)
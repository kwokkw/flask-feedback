from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """ Connect to database. """

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    # a unique primary key that is no longer than 20 characters
    username = db.Column(db.String(20), primary_key=True)

    # Using `db.text` because password hashes are often longer than typical strings. 
    password = db.Column(db.Text, nullable=False)

    # Ensures no two users can have the same email to enforce uniqueness.
    email = db.Column(db.String(50), nullable=False, unique=True)

    # Ensures every user has a first and last name. 
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    # To store a password reset token
    reset_token = db.Column(db.String, nullable=True)

    # `backref` creates a reverse relationship, all feedback is accessible from a given user using `user.feedbacks`.
    feedbacks = db.relationship("Feedback", backref="user", cascade="all, delete-orphan")

    @classmethod
    def hash_password(cls, password):

        # Hashing the password using `bcrypt`.
        hashed = bcrypt.generate_password_hash(password)

        # Ensures the stored password in the database as a string.
        return hashed.decode("utf8")

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        
        hashed_utf8 = cls.hash_password(password)

        return cls(
            username=username, 
            password=hashed_utf8,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

    @classmethod
    def authenticate(cls, username, password):

        # Queries the database for a user
        user = User.query.filter_by(username=username).first()

        # Check if the user exists, and the password matches.
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Establishes a foreign key relationship between `Feedback.username` and `User.username`
    username = db.Column(
        db.String(20),
        db.ForeignKey("users.username"),
        nullable=False
    )

    

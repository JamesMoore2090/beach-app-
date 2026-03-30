from datetime import date, datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    birthday = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(10), nullable=False, default='user')  # admin | user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class BeachWeek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    room_assignments = db.relationship('RoomAssignment', backref='beach_week', lazy=True)
    menu_items = db.relationship('MenuItem', backref='beach_week', lazy=True)
    chores = db.relationship('Chore', backref='beach_week', lazy=True)
    pictures = db.relationship('Picture', backref='beach_week', lazy=True)
    blog_posts = db.relationship('BlogPost', backref='beach_week', lazy=True)


class RoomAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beach_week_id = db.Column(db.Integer, db.ForeignKey('beach_week.id'), nullable=False)
    room_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='room_assignments')


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beach_week_id = db.Column(db.Integer, db.ForeignKey('beach_week.id'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(10), nullable=False)  # breakfast | lunch | dinner
    description = db.Column(db.Text, nullable=False)
    rsvps = db.relationship('DinnerRSVP', backref='menu_item', lazy=True)
    assigned_users = db.relationship('User', secondary='menu_assignment', backref='menu_assignments')


menu_assignment = db.Table('menu_assignment',
    db.Column('menu_item_id', db.Integer, db.ForeignKey('menu_item.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)


class DinnerRSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='attending')  # attending | not_here
    user = db.relationship('User', backref='dinner_rsvps')


class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beach_week_id = db.Column(db.Integer, db.ForeignKey('beach_week.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    day = db.Column(db.Date, nullable=True)
    assigned_users = db.relationship('User', secondary='chore_assignment', backref='chores')


chore_assignment = db.Table('chore_assignment',
    db.Column('chore_id', db.Integer, db.ForeignKey('chore.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beach_week_id = db.Column(db.Integer, db.ForeignKey('beach_week.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    uploader = db.relationship('User', backref='pictures')


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beach_week_id = db.Column(db.Integer, db.ForeignKey('beach_week.id'), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    author = db.relationship('User', backref='blog_posts')
    pictures = db.relationship('Picture', secondary='blog_post_picture', backref='blog_posts')


blog_post_picture = db.Table('blog_post_picture',
    db.Column('blog_post_id', db.Integer, db.ForeignKey('blog_post.id'), primary_key=True),
    db.Column('picture_id', db.Integer, db.ForeignKey('picture.id'), primary_key=True),
)

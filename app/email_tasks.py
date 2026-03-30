from datetime import date
from flask_mail import Message
from app import db, mail
from app.models import User


def check_birthdays(app):
    """Check for birthdays today and send email to all users."""
    with app.app_context():
        today = date.today()
        birthday_users = User.query.filter(
            db.extract('month', User.birthday) == today.month,
            db.extract('day', User.birthday) == today.day,
        ).all()

        if not birthday_users:
            return []

        all_users = User.query.all()
        recipients = [u.email for u in all_users]
        sent = []

        for bday_user in birthday_users:
            msg = Message(
                subject=f"Happy Birthday, {bday_user.name}!",
                recipients=recipients,
                body=f"Today is {bday_user.name}'s birthday! Wish them a happy birthday!",
            )
            mail.send(msg)
            sent.append(bday_user.name)

        return sent

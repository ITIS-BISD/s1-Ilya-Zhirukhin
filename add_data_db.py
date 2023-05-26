from Tema import db
from Tema.models import User, Classroom, Membership, Message, Note, Assignment, Channel, AssignmentSubmission, \
    DirectMessage
from datetime import datetime


# Creating Users
# Создаем экземпляры User
def create_user():
    user1 = User(first_name='John', last_name='Doe', username='johndoe', email='john@example.com', status='active',
                 password='password1')
    user2 = User(first_name='Jane', last_name='Smith', username='janesmith', email='jane@example.com', status='active',
                 password='password2')
    user3 = User(first_name='Mike', last_name='Johnson', username='mikejohnson', email='mike@example.com',
                 status='active', password='password3')
    db.session.add_all([user1, user2, user3])
    db.session.commit()
    print(user1)


def create_classroom():
    classroom1 = Classroom(code='classroom1', name='Classroom 1', description='This is classroom 1')
    classroom2 = Classroom(code='classroom2', name='Classroom 2', description='This is classroom 2')
    classroom3 = Classroom(code='classroom3', name='Classroom 3', description='This is classroom 3')
    db.session.add_all([classroom1, classroom2, classroom3])
    db.session.commit()
    print(classroom1)


create_user()
create_classroom()
print("ok")

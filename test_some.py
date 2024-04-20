import pytest
from flask import url_for
from conftest import client
from Tema import app, db
from flask_login import login_user, logout_user
from Tema.models import *

import uuid


def test_home_page(client):
    # Создание и сохранение пользователя в базе данных перед выполнением запроса
    base_username = '212142141124234'
    base_email = 'iluu1221312423@mail.ru'
    username = base_username
    email = base_email

    # Проверка на существующего пользователя с таким именем
    existing_user = User.query.filter_by(email=email).first()
    while existing_user is not None:
        # Если пользователь существует, добавляем к имени случайный суффикс и проверяем снова
        email = base_email + str(uuid.uuid4())
        existing_user = User.query.filter_by(email=email).first()

    new_user = User(first_name='ilu', last_name='johndoe123', username=username,
                    email=email, status='student', password='123456')
    db.session.add(new_user)
    db.session.commit()

    with client.application.test_request_context('/'):
        login_user(new_user)  # Вход пользователя

    response = client.get('/')
    assert response.status_code == 200


def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data


def test_invalid_route(client):
    response = client.get('/invalid_route')
    assert response.status_code == 404


def test_register(client):
    response = client.post('/register', data={
        'name': 'John112413221424',
        'last_name': 'Doe114212424132',
        'username': 'johndoe121241231244',
        'email': 'johndoe411324122412@example.com',
        'password': 'password',
        'confirm_password': 'password',
        'student_or_teacher': 'student'
    }, follow_redirects=True)

    assert response.status_code == 200


def test_login(client):
    response = client.post('/login', data={
        'email': 'johndoe@example.com',
        'password': 'password',
        'remember': False
    }, follow_redirects=True)

    assert response.status_code == 200


def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

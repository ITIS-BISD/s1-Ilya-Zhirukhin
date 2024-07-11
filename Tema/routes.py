from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from Tema.forms import RegistrationForm, LoginForm, EditProfileForm, DeleteProfileForm, ResetPasswordForm, \
    ResetPasswordForm_2
from Tema import app, bcrypt, db, socketio

from flask_login import login_user, current_user, logout_user, login_required
from Tema.utils import generate_code
from werkzeug.utils import secure_filename
from types import SimpleNamespace
from dateutil import parser
import os
from flask import session, make_response, g, abort, session, redirect, request, Flask, render_template, url_for, flash
from flask_dance.contrib.github import make_github_blueprint, github
from flask_oauthlib.client import OAuth
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import render_template
from flask_login import current_user
from Tema.models import *

app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'for_semestr_work@mail.ru'
app.config['MAIL_PASSWORD'] = '4UyJ8bda8KgvyC27xZAi'
app.config['MAIL_DEFAULT_SENDER'] = 'for_semestr_work@mail.ru'
app.config['MAIL_USE_MANAGEMENT_COMMANDS'] = True

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@app.route("/")
@app.route("/home")
def home():
    """
    Отображает главную страницу.

    Returns:
        Возвращает шаблон home.html с заголовком 'Home Page'.
    """
    return render_template("home.html", title='Home Page')


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Регистрация нового пользователя.

    Returns:
        Если пользователь уже аутентифицирован, перенаправляет на страницу '__app__'.
        Если форма заполнена корректно, добавляет нового пользователя в базу данных и перенаправляет на страницу 'login'.
        Возвращает шаблон register.html с формой регистрации и заголовком 'Register'.
    """
    if current_user.is_authenticated:
        return redirect(url_for("__app__"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(first_name=form.name.data, last_name=form.last_name.data, username=form.username.data,
                        email=form.email.data, status=form.student_or_teacher.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Аутентификация пользователя.

    Returns:
        Если пользователь уже аутентифицирован, перенаправляет на страницу 'home'.
        Если форма заполнена корректно, аутентифицирует пользователя и перенаправляет на следующую страницу,
        сохраненную в параметре 'next'.
        Возвращает шаблон login.html с формой входа и заголовком 'Login'.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    form_2 = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('__app__'))
        else:
            flash('Login unsuccessful, please try again.', 'error')

    github_login_url = url_for('login_github')

    return render_template('login.html', form=form, title='Login', github_login_url=github_login_url)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """
    Сброс пароля пользователя.

    Returns:
        Если форма заполнена корректно, отправляет письмо на указанный адрес электронной почты с инструкциями по сбросу пароля.
        Возвращает шаблон reset_password.html с формой сброса пароля и заголовком 'Сброс пароля'.
    """
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(email, salt='reset-password')
            reset_link = url_for('confirm_reset_password', token=token, _external=True)
            message = Message('Сброс пароля', recipients=[email])
            message.body = f'Для сброса пароля пройдите по ссылке: {reset_link}'
            mail.send(message)
            flash('Инструкции по сбросу пароля были отправлены на вашу почту.', 'info')
            return redirect(url_for('login'))
        flash('Адрес электронной почты не найден.', 'error')
    return render_template('reset_password.html', form=form, title='Сброс пароля')


@app.route('/confirm_reset_password/<token>', methods=['GET', 'POST'])
def confirm_reset_password(token):
    """
    Подтверждение сброса пароля.

    Args:
        token (str): Токен для сброса пароля.

    Returns:
        Если форма заполнена корректно и пользователь существует, обновляет пароль пользователя и перенаправляет на страницу 'login'.
        Возвращает шаблон confirm_reset_password.html с формой подтверждения сброса пароля и заголовком 'Подтверждение сброса пароля'.
    """
    form = ResetPasswordForm_2()
    if form.validate_on_submit():
        email = serializer.loads(token, salt='reset-password', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            db.session.commit()
            flash('Пароль успешно изменен.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь не найден.', 'error')
            return redirect(url_for('login'))

    return render_template('confirm_reset_password.html', form=form, token=token, title='Подтверждение сброса пароля')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key='fcea9d2bf64321447a57',
    consumer_secret='64e2c48ba1b1c3f9c0dfde7417a96014bb544113',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)


@github.tokengetter
def get_github_token():
    return session.get('github_token')


@app.route('/login/github')
def login_github():
    return github.authorize(callback=url_for('github_authorized', _external=True))


@app.route('/login/github/callback')
@github.authorized_handler
def github_authorized(resp):
    next_page = request.args.get('next') or url_for('home')
    if resp is None:
        flash('Authorization failed.', 'danger')
        return redirect(next_page)

    access_token = resp['access_token']
    session['github_token'] = access_token

    user_info = github.get('user').data
    email = user_info['login'] + '@mail.ru'

    # Check if the user with the given email already exists in the database
    user = User.query.filter_by(email=email).first()

    if user is None:
        # User doesn't exist, create a new user with the GitHub information
        new_user = User(first_name=user_info['name'], last_name=user_info['name'], username=user_info['login'],
                        email=email, image_file=user_info['avatar_url'], status='github',
                        password=access_token)  # Set a dummy password for GitHub users
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    login_user(user)
    flash('Successfully logged in via Github!', 'success')
    return redirect(url_for('user_profile'))


yandex = oauth.remote_app(
    'yandex',
    consumer_key='86d4d51e635144e49df6fd48b5b64321',
    consumer_secret='ed6c48bcac5f426891e47f666330f657',
    request_token_params={'scope': 'login:email'},
    base_url='https://login.yandex.com/info',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://oauth.yandex.com/token',
    authorize_url='https://oauth.yandex.com/authorize'
)


@yandex.tokengetter
def get_yandex_token():
    return session.get('yandex_token')


@app.route('/login/yandex')
def login_yandex():
    return yandex.authorize(callback=url_for('yandex_authorized', _external=True))


@app.route('/login/yandex/callback')
@yandex.authorized_handler
def yandex_authorized(resp):
    next_page = request.args.get('next') or url_for('home')
    if resp is None:
        flash('Authorization failed.', 'danger')
        return redirect(next_page)

    access_token = resp['access_token']
    session['yandex_token'] = access_token

    user_info_data = yandex.get('https://login.yandex.ru/info', headers={'Authorization': f'OAuth {access_token}'}).data

    # Check response
    if not user_info_data:
        flash('Failed to fetch user data.', 'danger')
        return redirect(next_page)

    email = user_info_data['login'] + '@yandex.ru'

    user = User.query.filter_by(email=email).first()

    if user is None:
        new_user = User(
            first_name=user_info_data.get('first_name', ''),
            last_name=user_info_data.get('last_name', ''),
            username=user_info_data['login'],
            email=email,
            image_file=user_info_data.get('default_avatar_id', ''),
            status='yandex',
            password=access_token
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    login_user(user)
    flash('Successfully logged in via Yandex!', 'success')
    return redirect(url_for('user_profile'))


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if 'file' not in request.files:
        flash('Файл не найден', 'error')
        return redirect(url_for('user_profile'))
    file = request.files['file']
    if file.filename == '':
        flash('Не выбран файл', 'error')
        return redirect(url_for('user_profile'))
    # Здесь добавьте код для сохранения и обновления аватара пользователя в базе данных
    if file:
        # Генерируем уникальное имя файла
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))

        # Обновляем поле image_file у пользователя
        current_user.image_file = filename
        db.session.commit()

        flash('Аватар успешно изменен', 'success')
    else:
        flash('Ошибка при загрузке файла', 'error')

    return redirect(url_for('user_profile'))


@app.route("/user-profile", methods=["POST", "GET"])
@login_required
def user_profile():
    return render_template('profile.html', title='Профиль', user=current_user)


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('user_profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('edit_profile.html', form=form)


@app.route("/delete-profile", methods=["POST"])
@login_required
def delete_profile():
    # Additional logic for profile deletion, e.g., deleting related data
    db.session.delete(current_user)
    db.session.commit()
    response = {'success': True, 'message': 'Профиль успешно удален'}
    return jsonify(response)


@app.route('/join-team', methods=['POST'])
def join_team():
    team_code = request.form['code']
    print(team_code)
    if team_code:
        classroom_id = Classroom.query.filter(Classroom.code == team_code).first()
        print(classroom_id)
        if classroom_id:
            new_membership = Membership(user_id=current_user.get_id(), classroom_id=classroom_id.id, role='regular')
            db.session.add(new_membership)
            db.session.commit()
            return jsonify({'result': {'id': classroom_id.id,
                                       'name': classroom_id.name},
                            'url_for_img': url_for('static', filename='imgs/' + classroom_id.image_file)})
        return jsonify({'error': "given code has either expired or is not valid"})
    return jsonify({'error': 'given code is invalid'})


@app.route("/app")
@login_required
def __app__():
    return render_template("app.html", title='Application', user=current_user)


@app.route('/app/chats', methods=['POST'])
def app_chats():
    users, contacts = set(), []
    messages = DirectMessage.query.filter(
        (DirectMessage.receiver_id == current_user.get_id()) | (DirectMessage.sender_id == current_user.get_id())).all()
    [users.add(message.receiver_id) if int(message.receiver_id) != int(current_user.get_id()) else users.add(
        int(message.sender_id)) for message in messages]
    for user in User.query.filter(User.id.in_(users)).all():
        contact = SimpleNamespace()
        contact.id = user.id
        contact.name = user.username
        contact.image_file = user.image_file
        contacts.append(contact)
        
    return render_template('chats.html', title='Contacts', data=contacts, type='contact')

@app.route('/add-contact', methods=['POST'])
def add_contact():
    contact = User.query.filter(User.username == request.form['username']).first()
    if contact and int(contact.id) == int(current_user.get_id()):
        contact = None  #
    return jsonify({'name': contact.username, 'id': contact.id, 'img_url': url_for('static',
                                                                                   filename='imgs/' + contact.image_file )}) if contact and contact.id != current_user.get_id() else jsonify(
        {'error': 'user not found.'})


@app.route('/retrieve-directmessages/<user_id>', methods=['POST'])
def retrieve_directmessages(user_id):
    messages = DirectMessage.query.filter(
        (DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == current_user.get_id()) | (
                    DirectMessage.sender_id == current_user.get_id()) & (DirectMessage.receiver_id == user_id))
    print("fack off")
    return jsonify({'messages': [{'content': message.content, 'date': message.date,
                                  'author': User.query.filter(User.id == message.sender_id).first().username,
                                  'mein': int(current_user.get_id()) == (message.sender_id)} for message in messages]})


'''
@app.route('/retrieve-contacts', methods=['POST'])
def retrieve_contacts():
    pass'''

@app.route('/json_route')
def json_route():
    data = {
        'user': {
            'name': 'John Doe',
            'age': 30,
            'email': 'johndoe@example.com',
            'address': {
                'street': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA'
            },
            'interests': ['programming', 'reading', 'traveling'],
            'projects': [
                {
                    'title': 'Project A',
                    'description': 'Lorem ipsum dolor sit amet.',
                    'status': 'in progress'
                },
                {
                    'title': 'Project B',
                    'description': 'Consectetur adipiscing elit.',
                    'status': 'completed'
                },
                {
                    'title': 'Project C',
                    'description': 'Nulla eu mi ut erat fringilla elementum.',
                    'status': 'planned'
                }
            ]
        }
    }  # Замените этот пример на свои данные
    return jsonify(data)


@app.route('/app/classrooms', methods=['POST'])
def app_classrooms():
    memberships = Membership.query.filter(Membership.user_id == current_user.get_id()).all()
    classrooms = Classroom.query.filter(Classroom.id.in_([membership.classroom_id for membership in memberships])).all()
    return render_template('classrooms.html', title='Classrooms', data=classrooms, type='classroom')

@app.route('/add-note', methods=['POST'])
def add_note():
    if request.form['note_title'] and request.form['note_text'] and request.form['channel_id']:
        note_title = request.form['note_title']
        note_text = request.form['note_text']
        note_channel_id = request.form['channel_id']
        if request.files["note_image"]:
            image = request.files["note_image"]
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
        new_note = Note(author_id=current_user.get_id(), title=note_title, note_text=note_text, note_imgs=filename,
                        channel_id=note_channel_id)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'new_note': {'note_title': new_note.title, 'note_id': new_note.id,
                                     'note_text': new_note.note_text,
                                     'note_img': url_for('static', filename='imgs/' + new_note.note_imgs)}})
    else:
        pass


@app.route('/classroom-settings/<classroom_id>', methods=['POST'])
def classroom_settings(classroom_id):
    specified_classroom = Classroom.query.filter(Classroom.id == classroom_id).first()
    if specified_classroom:
        membership = Membership.query.filter(Membership.classroom_id == classroom_id,
                                             Membership.user_id == current_user.get_id()).first()
        members = Membership.query.filter(Membership.classroom_id == classroom_id)
        members = User.query.filter(User.id.in_([member.user_id for member in members]))
        permission = membership.role == 'super'
        return jsonify({'room_code': specified_classroom.code,
                        'permission': permission,
                        'members': [{'name': member.first_name + ' ' + member.last_name,
                                     'id': member.id} for member in members if
                                    int(member.id) != int(current_user.get_id())],
                        'channels': [{'id': channel.id, 'name': channel.name} for channel in
                                     Channel.query.filter(Channel.classroom_id == classroom_id)]})
    return jsonify({'error': 'Classroom wasn\'t found.'})


@app.route('/create-team', methods=['POST'])
def create_team():
    # getting data from the form
    team_name = request.form['team_name']
    team_description = request.form['team_description']
    if team_name:
        # creating the classroom
        new_classroom = Classroom(name=team_name, description=team_description)
        db.session.add(new_classroom)  # adding the new classroom
        db.session.flush()  # using flush just so we can get the id of the classroom
        new_classroom.code = generate_code(new_classroom.id)
        print(new_classroom.code)
        db.session.flush()
        new_channel = Channel(name="General",
                              classroom_id=new_classroom.id)  # creating general channel for the classroom
        db.session.add(new_channel)
        db.session.flush()  # same here...
        # Creating membership for the user and classroom
        new_membership = Membership(user_id=current_user.get_id(), classroom_id=new_classroom.id, role='super')
        db.session.add(new_membership)
        db.session.commit()
        # sending back the classroom object
        return jsonify({'new_classroom': {
            'name': new_classroom.name,
            'id': new_classroom.id,
            'imgurl': url_for('static', filename="imgs/" + new_classroom.image_file)
        },
            'channel': new_channel.id
        })
    return jsonify({'error': 'given name is invalid.'})  #Returning an error if the given name is empty


@app.route('/retrieve-notes/<channel>', methods=['POST'])
def retrieve_notes(channel):
    notes = Note.query.filter(Note.channel_id == channel)
    return jsonify([{'author_id': note.author_id, 'note_title': note.title, 'note_id': note.id,
                     'note_text': note.note_text,
                     'note_img': url_for('static', filename='imgs/' + note.note_imgs) if note.note_imgs else None} for
                    note in notes])


@app.route('/retrieve-assignments/<channel>', methods=['POST'])
def retrieve_assignments(channel):
    assignments = Assignment.query.filter(Assignment.channel_id == channel)
    role = Membership.query.filter(
        Membership.classroom_id == Channel.query.filter(Channel.id == channel).first().classroom_id,
        Membership.user_id == current_user.get_id()).first().role
    return jsonify({'role': role, 'assignments': [
        {'id': assignment.id, 'text': assignment.assignment_text, 'duedate': assignment.due_date,
         'submission_state': AssignmentSubmission.query.filter(assignment.id == AssignmentSubmission.assignment_id,
                                                               AssignmentSubmission.user_id == current_user.get_id()).first() is not None}
        for assignment in assignments]})

@app.route('/add-assignment', methods=['POST'])
def add_assignment():
    get_date = parser.parse(request.form['assignment_date'])
    new_assignment = Assignment(author_id=current_user.get_id(), due_date=get_date,
                                assignment_text=request.form['assignment_text'], channel_id=request.form['channel_id'])
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({'id': new_assignment.id, 'text': new_assignment.assignment_text, 'duedate': new_assignment.due_date})

@app.route('/homework-submit', methods=['POST'])
def homework_submit():
    if request.files["homework"]:
        homework_file = request.files["homework"]
        filename = secure_filename(homework_file.filename)
        homework_file.save(os.path.join(app.config['FILE_UPLOADS'], filename))
        new_submission = AssignmentSubmission(user_id=current_user.get_id(),
                                              assignment_id=request.form['assignment_id'], file_location=filename)
        db.session.add(new_submission)
        db.session.commit()
    return jsonify({'message': 'successfuly submitted'})


@app.route('/retrieve-submissions/<assignment_id>', methods=['POST'])
def retrieve_submissions(assignment_id):
    assignments = AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id == assignment_id)
    return jsonify([{'name': User.query.filter(User.id == assignment.user_id).first().username,
                     'file': url_for('static', filename='submissions/' + str(assignment.file_location))} for assignment
                    in assignments])


@app.route('/retrieve-channels/<classroom>', methods=['POST'])
def retrieve_channels(classroom):
    channels = Channel.query.filter(classroom == Channel.classroom_id)
    return jsonify({'result': [{'id': channel.id, 'name': channel.name} for channel in channels ] })

@app.route('/retrieve-messages/<channel>', methods=['POST'])
def retrieve_messages(channel):
    POSTS_COUNT_ONLOAD = 50
    messages = Message.query.filter(Message.channel_id == channel, Message.ischild == -1)
    return jsonify({'result': [{'id': message.id,
                                'content': message.contents,
                                'date': message.date,
                                'author': {
                                    'id': message.author_id,
                                    'name': User.query.filter(User.id == message.author_id)[0].first_name + ' ' +
                                            User.query.filter(User.id == message.author_id)[0].last_name,
                                    'avatar': url_for('static', filename="imgs/" + User.query.filter(
                                        User.id == message.author_id)[0].image_file)}
                                } for message in messages][-POSTS_COUNT_ONLOAD:]
                    # returning the last ten messages in this channel
                    })

@app.route('/app/activity', methods=['POST'])
def app_activity():
    messages = Message.query.filter(Message.author_id == current_user.get_id())
    return render_template('activity.html', data=messages)

@app.route('/app/meetings', methods=['POST'])
def app_meetings():
    return render_template('meetings.html')

@app.route('/app/calls', methods=['POST'])
def app_calls():
    return render_template('calls.html')

// selected_user - переменная, используемая для хранения идентификатора выбранного пользователя чата.
let selected_user = null;

// toggle_username_input - функция, переключающая видимость поля ввода имени пользователя при добавлении нового контакта.
const toggle_username_input = () => {
    if ($('#username_input_id').is(':visible')) {
        $('#username_input_id').hide();
    } else {
        $('#username_input_id').show();
    }
}

// add_user_message - функция для добавления сообщения пользователя в блок чата.
// Принимает объект сообщения в качестве параметра.
const add_user_message = (message) => {
    $('#user_chat_box').append(`<div class='message bg-light'><span><b>${message.author}</b> ${message.date}</span> <p>${message.content}</p></div>`);
    $('#user_chat_box').scrollTop(10000);
}

// set_user_chat_title - функция для установки заголовка чата пользователя.
// Принимает заголовок в качестве параметра.
const set_user_chat_title = (title) => {
    $('#chat_title').html(title);
}

// clear_chat - функция для очистки содержимого чата пользователя.
const clear_chat = () => {
    $('#user_chat_box').html('');
}

// Обработчик события submit для формы с id "username_input_id".
// Вызывается при отправке формы (например, нажатие на кнопку "Добавить новый контакт").
$(document).on('submit', '#username_input_id', function (event) {
    event.preventDefault();
    // Отправляем AJAX POST-запрос на сервер на адрес '/add-contact' с введенным именем пользователя.
    $.ajax({url: '/add-contact', type: 'POST', data: {'username': $('#username_input').val()}}).done(function (data) {
        if (data.error) {
            console.log(data.error);
        } else {
            // Если добавление контакта прошло успешно, добавляем ссылку на контакт в блок меню.
            $('#menulist').append(`<div><a class="w3-bar-item w3-button user" id='*${data.id}' style='text-decoration:none'><img width=35 class="user-avatar" src="${data.img_url}"> ${data.name}</a></div>`);
        }
    });
    $('#username_input').val('');
});

// Обработчик события click для элементов с классом "user".
// Вызывается при клике на ссылку контакта.
$(document).on('click', '.user', function () {
    // Получаем идентификатор контакта из атрибута id элемента.
    const id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10);
    // Сохраняем выбранный идентификатор контакта в переменной selected_user.
    selected_user = id;
    this_element = $(this);
    console.log(1)
    // Отправляем AJAX POST-запрос на сервер для получения сообщений с выбранным контактом.
    $.ajax({url: `retrieve-directmessages/${id}`, type: 'POST'}).done(function (data) {
        console.log(data);
        // Очищаем содержимое чата и устанавливаем заголовок чата.
        clear_chat();
        set_user_chat_title(this_element.html());
        // Добавляем каждое сообщение в блок чата с помощью функции add_user_message.
        for (let i = 0; i < data.messages.length; i++) {
            add_user_message(data.messages[i]);
        }
    });
});

// Обработчик события submit для формы с id "message_input".
// Вызывается при отправке формы (например, нажатие на клавишу Enter при вводе сообщения).
$(document).on('submit', '#message_input', function (e) {
    e.preventDefault();
    // Получаем текст сообщения из поля ввода.
    const message = $('#message_input input').val()
    // Проверяем, выбран ли контакт и есть ли сообщение.
    if (selected_user && message) {
        // Отправляем событие 'direct_message' с помощью сокета и передаем получателя и сообщение.
        socket.emit('direct_message', {'to': selected_user, 'message': message});
    }
    // Очищаем поле ввода.
    $(this).children('input').val('');
});

// Обработчик события 'direct_message' от сервера через сокет.
socket.on('direct_message', function (data) {
    // Добавляем сообщение пользователя в блок чата.
    add_user_message(data);
});
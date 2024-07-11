// selected_channel - переменная, используемая для хранения идентификатора выбранного канала.
let selected_channel = null;
// selected_classroom - переменная, используемая для хранения идентификатора выбранного класса.
let selected_classroom = null;

// clear_chatbox - функция для очистки содержимого блока чата.
const clear_chatbox = () => {
    const chat_box = $('#channel_display .messagescontainer').first();
    chat_box.html('');
}

// set_chat_title - функция для установки заголовка чата.
// Принимает заголовок сервера и заголовок канала в качестве параметров.
const set_chat_title = (server_title, channel_title) => {
    const chat_title = $('#channel_display .upper_part .title').first();
    chat_title.html(`<b>${server_title}</b> ${channel_title}`);
    $(chat_title).find('i').remove();
}

// clear_submissions - функция для очистки содержимого блока подачи работ.
const clear_submissions = () => {
    $('#submissions').html('');
}

// add_message - функция для добавления сообщения в блок чата.
// Принимает объект данных сообщения в качестве параметра.
const add_message = (message_data) => {
    const chat_box = $('#channel_display .messagescontainer').first();
    chat_box.append(`<div class="message bg-light"><span><b>${message_data.author.name}</b> ${message_data.date}</span><p>${message_data.content}</p></div>`);
    $(chat_box).scrollTop(10000);
}

// clear_notes - функция для очистки содержимого блока заметок.
const clear_notes = () => {
    const notes = $('#note-container');
    const notes_list = $('#note-list');
    notes.html('');
    notes_list.html('');
}

// add_note - функция для добавления заметки в блок заметок.
// Принимает объект данных заметки и флаг активности в качестве параметров.
const add_note = (note_data, active) => {
    const note_list = $('#note-list');
    const note_container = $('#note-container');
    let id = note_data.note_title.replaceAll(' ', '') + note_data.note_id.toString(10);
    note_list.append(`<a class="list-group-item list-group-item-action ${active}" data-toggle="list" href="#${id}" role="tab" style='z-index:0;'>${note_data.note_title}</a>`);
    additional_text = '';
    if (note_data.note_img) {
        additional_text += `<img src="${note_data.note_img}" style='max-width:600px; max-height:600px;' />`;
    }
    note_container.append(`<div class="tab-pane ${active}" id="${id}" role="tabpanel">${additional_text}<p>${note_data.note_text}</p></div>`);
}

// add_assignment - функция для добавления задания в блок заданий.
// Принимает объект данных задания и флаг суперпользователя в качестве параметров.
const add_assignment = (assignment_data, is_super) => {
    const assignment_list = $('#assignments-list');
    if (assignment_data.id) {
        if (is_super) {
            assignment_list.append(`<tr value=${assignment_data.id}><td>${assignment_data.text}</td><td>${assignment_data.duedate}</td><td><button class='show_submission_button' data-target='#submissions'>View submissions</button> </td> </tr>`);
        } else {
            if (assignment_data.submission_state) {
                assignment_list.append(`<tr value=${assignment_data.id}><td>${assignment_data.text}</td><td>${assignment_data.duedate}</td><td>Already submitted</td> </tr>`);
            } else {
                assignment_list.append(`<tr value=${assignment_data.id}><td>${assignment_data.text}</td><td>${assignment_data.duedate}</td><td><form id='homework_submission'><input type=file name=homework><button>submit</button></form></td></tr>`);
            }
        }
    }
}

// clear_assignments - функция для очистки содержимого блока заданий.
const clear_assignments = () => {
    const assignment_list = $('#assignments-list');
    assignment_list.html('');
}

// toggle_submissions_menu - функция для переключения видимости блока подачи работ.
const toggle_submissions_menu = () => {
    $('#testest').css('display', 'block');
}

// Обработчик события document.ready, выполняется при загрузке страницы.
$(document).ready(function () {
    // Обработчик события клика по body.
    $('body').click(function (e) {
        var target = $(e.target);
        // Проверяем, является ли целью клика форма new_conversation_form или ее дочерние элементы.
        if (!target.is('#new_conversation_form') && !target.is('#new_conversation_form input')) {
            // Если форма new_conversation_form или ее дочерние элементы не являются целью клика, скрываем форму и отображаем кнопку newconversation.
            is_visible = $('#new_conversation_form').css('display');
            if (is_visible !== 'none') {
                $('#new_conversation_form').css('display', 'none');
                $('#newconversation').css('display', 'block');
            }
        }
    });

    // Обработчик события submit для формы note_form.
    $(document).on('submit', '#note_form', function (event) {
        let form_data = new FormData($('#note_form')[0]);
        form_data.append('channel_id', selected_channel);
        event.preventDefault();
        if (selected_channel != null) {
            $.ajax({
                data: form_data,
                contentType: false,
                processData: false,
                url: 'add-note',
                method: 'POST'
            }).done(function (data) {
                $("#note_form").trigger("reset");
                add_note(data['new_note'], '');
            });
        }
    });

    // Обработчик события клика по элементу с классом "classroom".
    $(document).on('click', '#menulist .classroom', function () {
        let id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10);
        selected_classroom = id;
        $.ajax({url: `retrieve-channels/${id}`, type: 'POST'}).done((data) => {
            console.log(data);
            if (data['result'].length > 0) {
                let result = '';
                for (let i = 0; i < data['result'].length; i++) {
                    result += `<li id="$${data['result'][i].id}" class='w3-bar-item w3-button' style='text-decoration: none; width:100%'><i class="fas fa-hashtag"></i>${data['result'][i].name}</li>`;
                }
                $('#menulist ul').html('');
                $(this).parent().children('.channels').first().html(result);
            }
        });
    });

    // Обработчик события клика по элементу i внутри элемента с классом "classroom".
    $(document).on('click', '.classroom i', function () {
        $('#classroom_settings').css('width', '100%');
        let id = parseInt($(this).parent().attr('id').slice(1, $(this).parent().attr('id').length), 10);
        $.ajax({url: `classroom-settings/${id}`, type: 'POST'}).done(function (data) {
            console.log(data);
            $('#code_id').html(data['room_code']);
            $('#channel_selection').html('<option value=-1>none</option>');
            $('#user_selection').html('<option value=-1>none</option>');
            for (let i = 0; i < data.channels.length; i++) {
                $('#channel_selection').append(`<option value='${data.channels[i].id}'>${data.channels[i].name}</option>`);
            }
            for (let i = 0; i < data.members.length; i++) {
                $('#user_selection').append(`<option value='${data.members[i].id}'>${data.members[i].name}</option>`);
            }
            if (data.permission) {
                $('.permission').show();
            } else {
                $('.permission').hide();
            }
        });
    });

    // Обработчик события клика по элементу с id "channels_action_submission_button".
    $(document).on('click', '#channels_action_submission_button', function () {
        channel_id = $('#channel_selection').children("option:selected").val();
        socket.emit('channel_action', {
            'classroom_id': selected_classroom,
            'action': $('#action_selection').children("option:selected").html(),
            'channel_id': channel_id,
            'name_input': $('#name_input').val()
        });
    });

    // Обработчик события клика по элементу с id "users_action_submission_button".
    $(document).on('click', '#users_action_submission_button', function () {
        user_id = $('#user_selection').children("option:selected").val();
        socket.emit('user_action', {
            'classroom_id': selected_classroom,
            'action': $('#action_selection_users').children("option:selected").html(),
            'user_id': user_id
        });
    });

    // Обработчик события изменения выбранного значения в элементе с id "action_selection".
    $(document).on('change', '#action_selection', function () {
        let selectedAction = $(this).children("option:selected").html();
        if (selectedAction === 'rename' || selectedAction === 'add') {
            console.log('selected action is rename');
            $('#name_input').css('display', 'block');
        } else {
            $('#name_input').css('display', 'none');
        }
    });

    // Обработчик события клика по элементам li внутри элемента с классом "channels".
    $(document).on('click', '.channels li', function () {
        let id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10);
        selected_channel = id;
        set_chat_title($(this).parent().parent().children('a').first().html(), $(this).html());
        $.ajax({url: `retrieve-messages/${id}`, type: 'POST'}).done((data) => {
            clear_chatbox()
            if (data.result.length) {
                for (let i = 0; i < data.result.length; i++) {
                    add_message(data.result[i]);
                }
            } else {
                let message = {'author': {'name': 'SC. Bot'}, 'content': 'No messages to display', 'date': 'just now'};
                add_message(message);
            }
        });
        $.ajax({url: `retrieve-notes/${id}`, type: 'POST'}).done((data) => {
            clear_notes();
            if (data.length) {
                for (let i = 0; i < data.length; i++) {
                    if (i === 0) {
                        add_note(data[i], 'active');
                    } else {
                        add_note(data[i], '');
                    }
                }
            } else {
                new_note = {'note_title': 'No data', 'note_text': 'No data', 'note_id': -1};
                add_note(new_note, 'active');
            }
        });
        $.ajax({url: `retrieve-assignments/${id}`, type: 'POST'}).done((data) => {
            console.log(data);
            clear_assignments();
            if (data.assignments.length) {

                result = data.role === 'super';
                for (let i = 0; i < data.assignments.length; i++) {
                    add_assignment(data.assignments[i], result);
                }
            } else {
                new_assignment = {'text': 'none', 'duedate': 'none', 'submission_state': '.'};
                add_assignment(new_assignment);
            }
        });
    });

    // Обработчик события клика по элементу с id "newconversation".
    $(document).on('click', '#newconversation', function () {
        $('#new_conversation_form').css('display', 'block');
        $('#newconversation').css('display', 'none');
    });

    // Обработчик события нажатия клавиши внутри формы с id "new_conversation_form".
    $(document).on('keydown', '#new_conversation_form', function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            const user_input = $('#new_conversation_input').val();
            $('#new_conversation_input').val('');
            if (selected_channel != null) {
                socket.emit('channel_conversation', {'channel_id': selected_channel, 'message': user_input});
            }
        }
    });

    // Обработчик события клика по элементу с id "regenerate_code".
    $(document).on('click', '#regenerate_code', function () {
        socket.emit('code_regeneration_req', {'classroom_id': selected_classroom});
    });

    // Обработчик события клика по элементу с id "leave_classroom".
    $(document).on('click', '#leave_classroom', function () {
        socket.emit('classroom_leave', {'classroom_id': selected_classroom});
        set_chat_title('', 'No channel to display...');
        clear_notes();
        clear_chatbox();
        close_settings_menu();
        $(`[id='%${selected_classroom}']`).parent().remove();
    });

    // Обработчик события submit для формы assignment_form.
    $(document).on('submit', "#assignment_form", function (event) {
        event.preventDefault();
        $('#selected_channel_input').val(selected_channel);
        $.ajax({
            url: '/add-assignment', type: 'POST', data: $('#assignment_form').serialize(), success: function (data) {
                add_assignment(data, true);
            }
        });
    });

    // Обработчик события submit для формы homework_submission.
    $(document).on('submit', '#homework_submission', function (event) {
        event.preventDefault();
        let form_data = new FormData($('#homework_submission')[0]);
        form_data.append('channel_id', selected_channel);
        form_data.append('assignment_id', parseInt($('#homework_submission').closest('tr').attr('value'), 10));
        event.preventDefault();
        if (selected_channel != null) {
            $.ajax({
                data: form_data,
                contentType: false,
                processData: false,
                url: '/homework-submit',
                method: 'POST'
            }).done(function (data) {
                $('#homework_submission').html('Already submitted');
            });
        }
    });

    // Обработчик события клика по элементу с классом "show_submission_button".
    $(document).on('click', '.show_submission_button', function () {
        id = parseInt($(this).closest('tr').attr('value'), 10);
        console.log(id);
        $.ajax({url: `retrieve-submissions/${id}`, type: 'POST'}).done(function (data) {
            clear_submissions();
            $('#submissions').append('<tr><th>Username</th> <th>Homework File</th></tr>');
            for (i = 0; i < data.length; i++) {
                $('#submissions').append(`<tr><td>${data[i].name}</td><td><a href='${data[i].file}' download>Download submission file</a></td></tr>`);
            }
        });
    });
});

// Обработчик события "channel_conversation" от сокета.
socket.on('channel_conversation', function (data) {
    if (data.channel_id === selected_channel) {
        console.log(data);
        add_message(data);
    } else {
        //Code for notification goes here
    }
});

// Обработчик события "channel_delete" от сокета.
socket.on('channel_delete', function (data) {
    if (selected_channel === parseInt(data['id'], 10)) {
        set_chat_title('', 'No channel to display...');
        clear_notes();
        clear_chatbox();
    }
    if (selected_classroom === data['classroom_id']) {
        $(`[id='%${data['classroom_id']}']`).parent().children('ul').children().each(function () {
            if ($(this).attr('id') === '$' + String(data['id'])) {
                $(this).remove();
                $('#channel_selection').children().each(function () {
                    if ($(this).val() === parseInt(data['id'], 10)) {
                        $(this).remove();
                    }
                });
            }
        })
    }
});

// Обработчик события "new_channel" от сокета.
socket.on('new_channel', function (data) {
    if (selected_classroom === data['classroom_id']) {
        $(`[id='%${data['classroom_id']}']`).parent().children('ul').append(`<li id="$${data['id']}" class='w3-bar-item w3-button' style='text-decoration: none; width:100%'><i class="fas fa-hashtag"></i>${data['name']}</li>`);
        $('#channel_selection').append(`<option value='${data['id']}'>${data['name']}</option>`);
    }
});

// Обработчик события "channel_rename" от сокета.
socket.on('channel_rename', function (data) {
    if (selected_classroom === data['classroom_id']) {
        $(`[id='%${data['classroom_id']}']`).parent().children('ul').children().each(function () {
            if ($(this).attr('id') === '$' + String(data['id'])) {
                $(this).html('<i class="fas fa-hashtag"></i>' + data['new_name']);
            }
        });
        $('#channel_selection').children().each(function () {
            if ($(this).val() === parseInt(data['id'], 10)) {
                $(this).html(data['new_name']);
            }
        });
    }
});

// Обработчик события "code_regeneration" от сокета.
socket.on('code_regeneration', function (data) {
    if (selected_classroom === data['classroom_id']) {
        console.log(data)
        $('#code_id').html(data['code']);
        console.log(data)
    }
});

// Обработчик события "user_kick" от сокета.
socket.on('user_kick', function (data) {
    console.log(data);
    if (parseInt(data['user_id'], 10) === parseInt($('#user_id').attr('value'), 10)) {
        $(`[id='%${data['classroom_id']}']`).parent().remove();
        if (selected_classroom === data['classroom_id']) {
            set_chat_title('', 'No channel to display...');
            clear_notes();
            clear_chatbox();
        }
    }
});

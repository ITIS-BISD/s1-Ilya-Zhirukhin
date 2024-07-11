/* Client script */
document.body.style.zoom = 0.8; // Устанавливает уменьшенный масштаб для элемента body страницы.

const app_container = $('#app_container'); // Получение элемента с id "app_container" с помощью jQuery.
const app_body = app_container.children("#app_body"); // Получение дочернего элемента с id "app_body" у контейнера "app_container".
let selected_page = null; // Инициализация переменной selected_page, которая будет содержать выбранную страницу.
const socket = io('http://' + document.domain + ':' + location.port, {transports: ['websocket']}); // Инициализация WebSocket для соединения с сервером.

socket.on('connect', function () { // Обработчик события подключения к серверу WebSocket.
    console.log("Connected to the network server."); // Вывод сообщения в консоль браузера.
});

$(document).ready(function () { // Обработчик события готовности документа (DOM) для обработки jQuery.
    $('#mySidebar .w3-bar-item').on('click', function (event) { // Обработчик клика на элемент с классом "w3-bar-item" внутри элемента с id "mySidebar".
        let this_element = this; // Сохранение текущего элемента в переменную this_element.
        if ($(this).attr('name') !== selected_page) { // Проверка, если значение атрибута "name" текущего элемента не равно выбранной странице.
            selected_page = $(this).attr('name'); // Присвоение выбранной страницы значению атрибута "name" текущего элемента.
            $.ajax({url: '/app/' + $(this).attr('name'), type: 'POST'}).done(function (data) { // Отправка AJAX-запроса на сервер с указанием выбранной страницы.
                app_container.html(data); // Замена содержимого контейнера "app_container" на полученные данные.
                $(this_element).addClass('selected_item'); // Добавление класса "selected_item" к текущему элементу.
                $('#mySidebar > .w3-bar-item').each(function (index) { // Перебор каждого элемента с классом "w3-bar-item" внутри элемента с id "mySidebar".
                    if (this !== this_element) { // Проверка, если текущий элемент не равен сохраненному элементу.
                        $(this).removeClass('selected_item'); // Удаление класса "selected_item" у текущего элемента.
                    }
                });
            });
        }
    });

    //$('#joinclassform').on('submit', function (event) {` - отслеживание события отправки (submit) формы
    // с id "joinclassform". В случае отправки формы, функция, указанная вторым аргументом, будет выполнена.
    // 2. `event.preventDefault();` - предотвращение стандартного поведения
    // браузера при отправке формы (перезагрузка страницы).
    // 3. `$.ajax({data: {code: $('#classroom_code').val()}, type: 'POST', url: '/join-team'}).done(function (data)
    // {` - отправка AJAX-запроса на сервер. Объект, который передается методу `$.ajax()`,
    // содержит следующие свойства:
    //      - `data`: объект, который передается в качестве данных запроса. В данном случае, передается код класса, который пользователь ввел в поле с id "classroom_code".
    //      - `type`: тип HTTP-запроса (в данном случае, POST).
    //      - `url`: адрес, на который отправляется запрос.
    //      - `done(function (data) {...})`: функция, которая будет вызвана при успешном завершении запроса. `data` - это данные, полученные от сервера.
    // 4. `if (data.error) {` - проверка на наличие ошибки в данных, полученных от сервера.
    // 5. `console.log(data.error);` - вывод ошибки в консоль браузера.
    // 6. `$('#join_notice').css('display', 'block');` -
    // изменение CSS-свойства "display" элемента с id "join_notice" на "block", т.е. делает его видимым.
    // 7. `$('#join_notice').html(data.error);` - вставка текста ошибки в элемент с id "join_notice".
    // 8. `} else {` - если ошибки нет, то выполняется код в этом блоке.
    // 9. `$('#menulist').append(...);` - добавление нового элемента в
    // конец элемента с id "menulist".
    // Элемент представляет собой ссылку на класс,
    // сгенерированную с использованием данных, полученных от сервера.
    // 10. `socket.emit('join-room', data.result.id);` -
    // отправка события 'join-room' с использованием библиотеки socket.io. Вторым аргументом передается id комнаты, который был получен от сервера.
    // 11. `});` - закрытие блока функции `done()` и функции-обработчика события отправки формы.
    // Когда пользователь отправляет форму (например, нажимает кнопку "Подключиться к классу"),
    // этот обработчик будет вызван.


    $('#joinclassform').on('submit', function (event) {

        // Предотвращаем стандартное поведение формы (отправку формы).
        event.preventDefault();

        // Отправляем AJAX POST-запрос на сервер на адрес '/join-team' с кодом класса, введенным пользователем.
        $.ajax({data: {code: $('#classroom_code').val()}, type: 'POST', url: '/join-team'}).done(function (data) {
            // Если сервер возвращает ошибку, выводим ее в консоль и отображаем пользователю.
            if (data.error) {
                console.log(data.error);
                $('#join_notice').css('display', 'block');
                $('#join_notice').html(data.error);
            } else {
                // Если все в порядке, добавляем новую комнату в список и подключаемся к ней с помощью сокета.
                $('#menulist').append(`<div><a class="w3-bar-item w3-button classroom" id='%${data.result.id}' style='text-decoration: none; width:100%'><img src="${data.url_for_img}" width=25></img> ${data.result.name} <i class='fas fa-cog float-right'></i></a><ul class="channels"></ul></div>`);
                socket.emit('join-room', data.result.id);
            }
        });
    });


    $('#teamcreationform').on('submit', function (event) {
        $.ajax({
            data: {
                team_name: $('#teamname').val(),
                team_description: $('#teamdescription').val()
            },
            type: 'POST',
            url: '/create-team'
        }).done(function (data) {
            const notice_field = $('#notice');
            if (data.error) {
                notice_field.html(data.error);
                notice_field.addClass('alert-danger');
                notice_field.css('display', 'block');
                console.log("error: team was not created due to the following < " + data.error + " >");
            } else {
                notice_field.css('display', 'block');
                notice_field.addClass('alert-success');
                notice_field.html("classroom `" + $('#teamname').val() + "` has been created.");
                socket.emit('join-room', data.new_classroom.id);
                $('#teamname').val('');
                $('#teamdescription').val('');
                setTimeout(() => {
                    notice_field.html('');
                    notice_field.hide();
                    $("#teammodal").hide();
				}, 1624);
                if ($('#classrooms').hasClass('selected_item')) {
                    $('#menulist').append(`<div><a class='classroom w3-bar-item w3-button' style='text-decoration: none; width:100%' id="%${data.new_classroom.id}"><img src=${data.new_classroom.imgurl} width=25> ${data.new_classroom.name} <i class='fas fa-cog float-right'></i></a><ul class='channels'></ul></div>`);
                }
			}
		});
		event.preventDefault();
	});
});

const toggle_class_creator = () => {
	$('#teammodal').css('display', 'block');
	$('#teammodal').find('.alert').css('display', 'none');
}
const toggle_class_join = () => {
	$('#joinclass_modal').css('display', 'block');
	$('#join_notice').css('display', 'none');
}
const close_settings_menu = () => {
	$('#classroom_settings').css('width', '0%');
}





function vote(participate_id) {
    $.ajax({
        type: "GET",
        url: "/vote/"+participate_id,
        data: {},
        success: function (data) {
            if (data == 'OK') {
                notif({
                    type: "success",
                    msg: "Ваш голос принят!",
                    opacity: 0.9
                });
            } else if (data == 'DONE') {
                notif({
                    type: "info",
                    msg: "Вы уже голосовали за этого участника!",
                    position: 'center',
                    opacity: 0.9
                });
            } else {
                notif({
                    type: "error",
                    msg: "Ошибка:" + data,
                    multiline: true,
                    opacity: 0.9
                });
            }
        },
        error: function () {
            notif({
                type: "error",
                msg: "Ошибка отправки данных на сервер",
                multiline: true,
                opacity: 0.9
            });
        },
        complete: function () {
        }
    });
}
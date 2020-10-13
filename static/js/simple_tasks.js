let openNewTaskFrm = () => {
    App.openPanel($("#data-task-form-template").html(), "Nueva Tarea");
}
let create_new_task = () => {
    if(App.validate_required_fields("#data-task-form")) {
        $.post(
            url_tarea_new,
            $('#data-task-form').serialize(),
            function(data, textStatus, jqXHR) {
                App.closePanel();
                if('ok' == data.status) {
                    try {
                        getall_tasks();
                    } catch(error){
                        if(error.message.indexOf('url_tarea_getall') >= 0) {
                            App.openPanel(`Tarea creada con éxito`, "Nueva Tarea");
                        }
                    }
                } else {
                    alert("Ha ocurrido un error creando la tarea\n\n" + data.reason);
                }
            },
            'json').fail(function(jqXHR, textStatus, errorThrown) {
                alert("Ha ocurrido un error creando la tarea\n\n" + textStatus + ":\n" + errorThrown);
            });
    }
}
let getall_tasks = () => {
    $.get(
        url_tarea_getall,
        function(data) {
            $("td.day div.task").remove();
            for(idx in data) {
                tarea = data[idx];
                add_task(tarea);
            }
            $('[data-toggle="tooltip"]').tooltip(); 
        },
        'json').fail(function(jqXHR, textStatus, errorThrown) {
            alert("Ha ocurrido un error creando la tarea\n\n" + textStatus + ":\n" + errorThrown);
        });
}
let add_task = (task) => {
    task.fecha_limite = new Date(task.fecha_limite + "T23:59:59");
    let container = $(`td.day[data-day="${task.fecha_limite.getDate()}"] div.task-list`);
    let template = Handlebars.compile(
        $("#data-task-list-template").html());
    tarea.responsable = {
        "id": tarea.responsable,
        "nombre": (responsables[tarea.responsable].nombre + " " + 
            responsables[tarea.responsable].apellido).trim(),
        "iniciales": 
            (responsables[tarea.responsable].nombre.length ? 
                responsables[tarea.responsable].nombre[0] 
                : '') + 
            (responsables[tarea.responsable].apellido.length ? 
                responsables[tarea.responsable].apellido[0] 
                : '')
    }
    let html = template(tarea);
    container.append(html);
}
let task_vinculos = [];
let see_task = (id) => {
    $.get(
        url_tarea_see + id,
        function(tarea) {
            let template = Handlebars.compile($("#data-task-readonly-template").html());
            let html = template(tarea);
            App.openPanel(html, `${id} - ${tarea.titulo}`);
            $("#pk").attr('value', id);
            task_vinculos = tarea.vinculos;
        },
        'json').fail(function(jqXHR, textStatus, errorThrown){
            alert("Ha ocurrido un error obteniendo la tarea\n\n" + textStatus + ":\n" + errorThrown);
        });
}
let update_task = (id) => {
    App.closePanel();
    $.get(
        url_tarea_see + id,
        function(tarea) {
            App.openPanel($("#data-task-form-template").html(), `${id} - ${tarea.titulo}`);
            $("#pk").attr('value', id);
            $("#btn-save")[0].onclick = save_updated_task;
            $("#titulo").attr('value', tarea.titulo);
            $("#descripcion")[0].innerHTML = tarea.descripcion_raw;
            $("#fecha_limite").attr('value', tarea.fecha_limite_en);
            $(`#responsable option[value="${tarea.responsable.pk}"]`).attr("selected", true);
            $(`#estado_actual option[value="${tarea.estado_actual}"]`).attr("selected", true);
            for(let idx = 0; idx < tarea.vinculos.length; idx++) {
                let lnk = tarea.vinculos[idx];
                switch(lnk.tipo) {
                    case 'Cliente':
                        $(`#lnk_cte option`).each(function(idx, elem) {
                            if($(elem).text() == lnk.texto) {
                                elem.selected = true;
                            }
                        });
                        break;
                    case 'Historia Laboral':
                        let txt = lnk.texto.replace("Historia Laboral ", '');
                        txt = txt.substr(0, txt.indexOf('(') - 1);
                        $(`#lnk_hl option`).each(function(idx, elem) {
                            if($(elem).text() == txt) {
                                elem.selected = true;
                            }
                        });
                        break;
                    case 'Actividad':
                        $(`#lnk_act option`).each(function(idx, elem) {
                            if($(elem).text() == lnk.texto) {
                                elem.selected = true;
                            }
                        });
                        break;
                }
            }
        },
        'json').fail(function(jqXHR, textStatus, errorThrown){
            alert("Ha ocurrido un error obteniendo la tarea\n\n" + textStatus + ":\n" + errorThrown);
        });
}
let save_updated_task = () => {
    if(App.validate_required_fields("#data-task-form")) {
        $.post(
            url_tarea_update,
            $('#data-task-form').serialize(),
            function(data, textStatus, jqXHR) {
                for(let idx = 0; idx < task_vinculos.length; idx++) {
                    $.post(url_tarea_delete_link, {
                        "pk": task_vinculos[idx].pk,
                        "csrfmiddlewaretoken": $(`input[name="csrfmiddlewaretoken"]`).val()
                    });
                }
                let lnks_type = {"lnk_cte": "Cliente", "lnk_hl": "Historia Laboral", "lnk_act": "Actividad"};
                $("#lnk_cte, #lnk_hl, #lnk_act").each(function(idx, lnk) {
                    if($(lnk).val()) {
                        data_send = {
                            "id": $(lnk).val(),
                            "tipo": lnks_type[lnk.id],
                            "idtarea": $("#pk").val(),
                            "csrfmiddlewaretoken": $(`input[name="csrfmiddlewaretoken"]`).val()
                        };
                        $.post(url_tarea_new_link, data_send);
                    }
                });
                App.closePanel();
                if(simple_task_reloading) {
                    location.reload();
                }
                if('ok' == data.status) {
                    getall_tasks();
                } else {
                    alert("Ha ocurrido un error actualizando la tarea\n\n" + data.reason);
                }
            },
            'json').fail(function(jqXHR, textStatus, errorThrown) {
                alert("Ha ocurrido un error actualizando la tarea\n\n" + textStatus + ":\n" + errorThrown);
            });
    }
}
let delete_task = (id) => {
    App.closePanel();
    $.get(`${url_tarea_delete}${id}`, getall_tasks).fail(
        function(jqXHR, textStatus, errorThrown) {
            alert("Ha ocurrido un error eliminando la tarea\n\n" + textStatus + ":\n" + errorThrown);
        });
    if(simple_task_reloading) {
        location.reload();
    }
}
let create_new_comment = () => {
    if(App.validate_required_fields("#comment-task-form")) {
        idtarea = $('#comment-task-form #id').val();
        $.post(
            url_tarea_add_comment,
            $('#comment-task-form').serialize(),
            function(data, textStatus, jqXHR) {
                App.closePanel();
                if('ok' == data.status) {
                    see_task(idtarea);
                } else {
                    alert("Ha ocurrido un error agregando el comentario\n\n" + data.reason);
                }
            },
            'json').fail(function(jqXHR, textStatus, errorThrown) {
                alert("Ha ocurrido un error agregando el comentario\n\n" + textStatus + ":\n" + errorThrown);
            });
    }
}   
let delete_comment = (id) => {
    let id_tarea = $("#pk").val();
    $.get(
        `${url_tarea_delete_comment}${id}`,
        function(data) {
            App.closePanel();
            see_task(id_tarea);
        },
        'json').fail(function(jqXHR, textStatus, errorThrown) {
            alert("Ha ocurrido un error eliminando el comentario\n\n" + textStatus + ":\n" + errorThrown);
        });
}
let update_comment = (id) => {
    $(`.comment-display[data-idcomment="${id}"]`).addClass('d-none');
    $(`.comment-frm-upd[data-idcomment="${id}"]`).removeClass('d-none');
}
let save_updated_comment = (id) => {
    let idtarea = $("#pk").val();
    let comentario = $(`#comentario-${id}`).val();
    $.post(
        url_tarea_update_comment,
        {"pk": id, "comentario": comentario, "csrfmiddlewaretoken": $(`input[name="csrfmiddlewaretoken"]`).val()},
        function(data, textStatus, jqXHR) {
            App.closePanel();
            if('ok' == data.status) {
                see_task(idtarea);
            } else {
                alert("Ha ocurrido un error actualizando el comentario\n\n" + data.reason);
            }
        },
        'json').fail(function(jqXHR, textStatus, errorThrown) {
            alert("Ha ocurrido un error actualizando el comentario\n\n" + textStatus + ":\n" + errorThrown);
        });
}

function submit_item_form(controls, method, url, location) {
    var data = { };
    for(var i=0; i<controls.length; ++i) {
        var control = controls[i];
        var element = $("#"+control);

        var encoder = window["encode_"+element.data("rm-type")] || default_encoder;
        var value = encoder(element) || null;

        data[control] = value;
    }

    $.ajax({
        type: method, url: url,
        data: JSON.stringify(data), contentType: "application/json",
        dataType: "json",
        success: function (data, text, xhr) {
            window.location.href = location || xhr.getResponseHeader("Location") || window.location;
        },
        error: function (xhr, status, error) {
            $("html").html(xhr.responseText);
        }
    });
}

function default_encoder(element) {
    var data = element.val();
    return data;
}

function encode_list(element) {
    var data = element.val();
    if(data != "") {
        return data.split(/[\s,]+/);
    }
    else {
        return  [];
    }
}

function encode_media_content(element) {
    var regex = /data:[^,]+,(.*)+/;
    var match = $(element).attr("src").match(regex);
    return match[1];
}

function format_dates(dates) {
    for(var i=0; i<dates.length; ++i) {
        var element = $(dates[i]);
        var content = element.html();
        if(content != "") {
            var date = new Date(content);
            element.html(date.toLocaleString());
        }
    }
}

function archive_item(url) {
    $("#status").val(
        ($("#status").val() != "archived")?"archived":"published");
    submit_item_form(["status"], "PATCH", url);
}

function delete_item(url) {
    submit_item_form([], "DELETE", url, "/");
}

function move_item(method, url) {
    var overlay = $("#overlay");
    overlay.show();
    $(document).keypress(function(e) {
        if (e.keyCode == 27) { $('#overlay').hide(); }
    });

    $('ul.tree span').hover(
        function() { $(this).addClass('hover'); },
        function() { $(this).removeClass('hover'); }
    );

    $('ul.tree span').click(function() {
        if($(this).attr('disabled') != 'disabled') {
            $('ul.tree span').removeClass('selected');
            $(this).addClass('selected');
            $('#overlay_move').removeAttr('disabled');
        }
    });

    var move = $("#overlay_move");
    move.click(function() {
        var newParentId = parseInt(
            $('ul.tree .selected').attr('data-rm-id')) || null;
        data = {parent_id: newParentId};

        $.ajax({
            type: method, url: url,
            data: JSON.stringify(data), contentType: "application/json",
            dataType: "json",
            success: function (data, text, xhr) {
                window.location.href = url;
            },
            error: function (xhr, status, error) {
                $("html").html(xhr.responseText);
            }
        });
    });

    var cancel = $("#cancel_move");
    cancel.click(function() { $('#overlay').hide(); });
}

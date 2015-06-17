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

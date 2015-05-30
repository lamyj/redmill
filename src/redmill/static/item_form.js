function submit_item_form(controls, url) {
    var data = { };
    for(var i=0; i<controls.length; ++i) {
        var control = controls[i];
        var element = $("#"+control);

        var encoder = window["encode_"+element.data("rm-type")];
        var value = null;
        if(typeof(encoder) != "undefined") {
            value = encoder(element.val());
        }
        else {
            value = element.val();
        }

        data[control] = value;
    }

    $.ajax({
        type: "PATCH", url: url,
        data: JSON.stringify(data), contentType: "application/json",
        dataType: "json",
        success: function (data, text, xhr) {
            window.location.href = window.location;
        },
        error: function (xhr, status, error) {
            $("html").html(xhr.responseText);
        }
    });
}

function encode_list(data) {
    if(data != "") {
        return data.split(/[\s,]+/);
    }
    else {
        return  [];
    }
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

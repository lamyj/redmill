function make_editable(name, url, encode, decode, after_success)
{
    if(typeof(encode) == "undefined")
    {
        encode = function(x) { return x; };
    }
    if(typeof(decode) == "undefined")
    {
        decode = function(x) { return x; };
    }
    if(typeof(after_success) == "undefined")
    {
        after_success = function(x) {  };
    }

    var label = $("*[data-rm-editable=\""+name+"\"]");
    var input = $("<input type=\"text\">");
    label.after(input);

    label.click(function()
        {
            label.hide();
            input.val(label.html());
            input.show().focus();
        }
    );

    input.keypress(function(event)
        {
            var done = false;
            if(event.keyCode == 13)
            {
                var data = { };
                data[name] = encode(input.val());
                $.ajax({
                    type: "PATCH", url: url,
                    data: JSON.stringify(data), dataType: "json",
                    contentType: "application/json",
                    success: function(data, text, xhr)
                        {
                            var decoded = decode(data[name]);
                            label.html(decoded);
                            after_success(decoded);
                        }
                });
                done = true;
            }
            else if(event.keyCode == 27)
            {
                input.val(label.html());
                done = true;
            }

            if(done)
            {
                input.blur();
            }
        }
    );

    input.blur(function()
        {
            label.show();
            input.hide();
        }
    );

    input.hide();
}

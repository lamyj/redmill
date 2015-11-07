var submitItem = {};

/// @brief Initialize the submit form.
submitItem.init = function(method, url, controls, deleteURL) {
    [].forEach.call(
        document.querySelectorAll('[data-rm-type="date"]'),
        function(element) {
            var content = element.innerHTML;
            if(content !== '') {
                var date = new Date(content);
                element.innerHTML = date.toLocaleString();
            }
        }
    );

    var submit = document.querySelector('#submit');
    if(submit) {
        submit.addEventListener(
            'click',
            submitItem.submit.bind(undefined, method, url, controls, null)
        );
    }
    document.querySelector('#archive').addEventListener(
        'click', submitItem.archive.bind(undefined, url)
    );
    if(deleteURL) {
        document.querySelector('#delete').addEventListener(
            'click', submitItem.delete.bind(undefined, deleteURL));
    }
};

/// @brief Submit the item.
submitItem.submit = function(method, url, controls, location) {
    var data = { };
    controls.forEach(function(control) {
        var element = document.querySelector('#'+control);

        var encoder =
            submitItem.encoders[element.dataset.rmType]
            || submitItem.encoders.default;
        var value = encoder(element) || null;

        data[control] = value;
    });

    var failure = function(xhr) {
        document.querySelector('html').innerHTML = xhr.responseText;
    };

    var request = new XMLHttpRequest();
    request.addEventListener('load', function(event) {
        if(event.target.status !== 200) {
            return failure(event.target);
        }
        else {
            window.location.href =
                location ||
                event.target.getResponseHeader('Location') ||
                window.location;
        }
    });
    request.addEventListener('error', function(event) {
        return failure(event.target);
    });
    request.open(method, url);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(data));
}

/// @brief Archive the item.
submitItem.archive = function(url) {
    var status = document.querySelector('#status');
    status.value = (status.value !== 'archived')?'archived':'published';
    submitItem.submit('PATCH', url, ['status']);
}

/// @brief Delete the item.
submitItem.delete = function(url) {
    submitItem.submit('DELETE', url, '/', []);
};

/**
 * @brief Encoders for the various field types.
 *
 * An encoder is a function taking an element as parameter, and returing an
 * arbitrary Javascript object.
 */
submitItem.encoders = {};

submitItem.encoders.default = function(element) {
    var data = element.value;
    return data;
};

submitItem.encoders.list = function(element) {
    var data = element.value;
    if(data !== '') {
        return data.split(/[\s,]+/);
    }
    else {
        return [];
    }
};

submitItem.encoders.media_content = function(element) {
    var match = element.getAttribute('src').match(/data:[^,]+,(.*)+/);
    return match[1];
};

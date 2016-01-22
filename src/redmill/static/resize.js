var resize = {};

resize.init = function(derivative_url, media_url, operations) {
    var image = new Image();
    image.addEventListener(
        'load',
        function(event) {
            var canvas = document.querySelector('#canvas');
            canvas.setAttribute('width', event.target.naturalWidth);
            canvas.setAttribute('height', event.target.naturalHeight);
            canvas.setAttribute('data-derivative', derivative_url);

            operations.forEach(function(operation) {
                if(operation[0] === 'crop') {
                    resize.setSelection({
                        left: operation[1][0], top: operation[1][1],
                        width: operation[1][2], height: operation[1][3]});
                }
            });
        });
    image.src = media_url;

    document.querySelector('#selection').drag = {
        action: null, position: null, corner: null };
    document.querySelector('#selection>rect').addEventListener(
        'mousedown', resize.onMoveStart);

    [].forEach.call(
        document.querySelectorAll('#selection>circle'),
        function(x) { x.addEventListener('mousedown', resize.onResizeStart); }
    );

    document.querySelector('#selection_ratio #free').addEventListener(
        'click', resize.setRatioType.bind(undefined, 'free'));
    document.querySelector('#selection_ratio #fixed').addEventListener(
        'click', resize.setRatioType.bind(undefined, 'fixed'));
}

resize.getSelection = function() {
    var matrix =
        /matrix\((.*)\)/.exec(
            selection.getAttribute('transform'))[1].split(' ').map(parseFloat);
    var left = matrix[4];
    var top = matrix[5];

    var rect = selection.querySelector('rect');
    var width = parseFloat(rect.getAttribute('width'));
    var height = parseFloat(rect.getAttribute('height'));

    return {left: left, top: top, width: width, height: height};
}

resize.setSelection = function(area) {
    var canvas = document.querySelector('#canvas');
    area.left = Math.max(
        0, Math.min(
            area.left, parseInt(canvas.getAttribute('width'))-area.width));
    area.top = Math.max(
        0, Math.min(
            area.top, parseInt(canvas.getAttribute('height'))-area.height));

    area.width = Math.max(0, area.width);
    area.height = Math.max(0, area.height);
    if(resize.getRatioType() === 'fixed') {
        var ratio =
            parseFloat(document.querySelector('#selection_ratio #width').value) /
            parseFloat(document.querySelector('#selection_ratio #height').value);
        area.height = Math.round(area.width / ratio);
    }

    var selection = document.querySelector('#selection');
    selection.setAttribute(
        'transform', 'matrix(1 0 0 1 '+area.left+' '+area.top+')');

    var rect = selection.querySelector('rect');
    rect.setAttribute('width', area.width);
    rect.setAttribute('height', area.height);

    var se_handle = selection.querySelector('#se');
    se_handle.setAttribute('cx', area.width);
    se_handle.setAttribute('cy', area.height);
}

resize.getRatioType = function() {
    var radio_free = document.querySelector('#selection_ratio #free');
    var radio_fixed = document.querySelector('#selection_ratio #fixed');

    if(radio_free.checked) {
        return 'free';
    }
    else if(radio_fixed.checked) {
        return 'fixed';
    }
    else {
        throw new Error('Invalid ratio type');
    }
}

resize.setRatioType = function(type) {
    var radio_free = document.querySelector('#selection_ratio #free');
    var radio_fixed = document.querySelector('#selection_ratio #fixed');
    var width_control = document.querySelector('#selection_ratio #width');
    var height_control = document.querySelector('#selection_ratio #height');
    if(type === 'free') {
        radio_free.checked = true;
        radio_fixed.checked = false;
        width_control.disabled = true;
        height_control.disabled = true;
    }
    else if(type === 'fixed') {
        radio_free.checked = false;
        radio_fixed.checked = true;
        width_control.disabled = false;
        height_control.disabled = false;

        if(width_control.value === '' || height_control.value === '') {
            var selection = resize.getSelection();
            width_control.value = selection.width;
            height_control.value = selection.height;
        }
    }
    else {
        throw new Error('Unknown ratio type: '+type);
    }
}

resize.onMoveStart = function(event) {
    // Make sure the browser does not select the element when clicking it.
    event.preventDefault();

    var selection = document.querySelector('#selection');
    selection.drag.action = 'move' ;
    selection.drag.position = [event.clientX, event.clientY];

    var canvas = document.querySelector('#canvas');
    canvas.addEventListener('mousemove', resize.onMove);
    canvas.addEventListener('mouseup', resize.onMoveStop);
};

resize.onMove = function(event) {
    var selection = document.querySelector('#selection');

    if(selection.drag.action !== 'move') {
        return;
    }

    var position = [event.clientX, event.clientY];

    var delta = [
        position[0]-selection.drag.position[0],
        position[1]-selection.drag.position[1]
    ];

    var area = resize.getSelection();

    area.left += delta[0];
    area.top += delta[1];
    resize.setSelection(area);

    selection.drag.position = position;
};

resize.onMoveStop = function(event) {
    var selection = document.querySelector('#selection');
    selection.drag.action = null;

    var canvas = document.querySelector('#canvas');
    canvas.removeEventListener('mousemove', resize.onMove);
    canvas.removeEventListener('mouseup', resize.onMoveStop);

    resize.notifyChange();
}

resize.onResizeStart = function(event) {
    // Make sure the browser does not select the element when clicking it.
    event.preventDefault();

    var selection = document.querySelector('#selection');
    selection.drag.action = 'resize' ;
    selection.drag.position = [event.clientX, event.clientY];
    selection.drag.corner = event.target.getAttribute('id');

    var canvas = document.querySelector('#canvas');
    canvas.addEventListener('mousemove', resize.onResize);
    canvas.addEventListener('mouseup', resize.onResizeStop);
}

resize.onResize = function(event) {
    var selection = document.querySelector('#selection');

    if(selection.drag.action !== 'resize') {
        return;
    }

    var position = [event.clientX, event.clientY];

    var delta = [
        position[0]-selection.drag.position[0],
        position[1]-selection.drag.position[1]
    ];

    var area = resize.getSelection();

    if(selection.drag.corner === 'nw') {
        area.left += delta[0];
        area.top += delta[1];

        area.width -= delta[0];
        area.height -= delta[1];
    }
    else if(selection.drag.corner === 'se') {
        area.width += delta[0];
        area.height += delta[1];
    }
    else {
        throw new Error('Unknown corner: '+selection.drag.corner);
    }

    resize.setSelection(area);

    selection.drag.position = position;
}

resize.onResizeStop = function(event) {
    var selection = document.querySelector('#selection');
    selection.drag.action = null;
    selection.drag.corner = null;

    var canvas = document.querySelector('#canvas');
    canvas.removeEventListener('mousemove', resize.onResize);
    canvas.removeEventListener('mouseup', resize.onResizeStop);

    resize.notifyChange();
}

resize.notifyChange = function() {
    var url = document.querySelector('#canvas').getAttribute('data-derivative');

    var selection = resize.getSelection();
    var cropList = [
        selection.left, selection.top, selection.width, selection.height];
    var data = {operations: [['crop', cropList]]};

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
    request.open('PATCH', url);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(data));
}

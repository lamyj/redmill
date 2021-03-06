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

            resize.setSizeType('original');
            operations.forEach(resize.applyOperation);
        });
    image.src = media_url;

    var thumbnail = document.querySelector("#thumbnail");
    thumbnail.src = derivative_url+'/content';

    document.querySelector('#selection').drag = {
        action: null, position: null, corner: null };
    document.querySelector('#selection__frame').addEventListener(
        'mousedown', resize.onMoveStart);

    [
        document.querySelector('#selection__nw-handle'),
        document.querySelector('#selection__se-handle'),
    ].forEach(
        function(x) { x.addEventListener('mousedown', resize.onResizeStart); }
    );

    document.querySelector('#selection-ratio__free').addEventListener(
        'click', resize.setRatioType.bind(undefined, 'free'));
    document.querySelector('#selection-ratio__fixed').addEventListener(
        'click', resize.setRatioType.bind(undefined, 'fixed'));

    document.querySelector('#thumbnail-size__original').addEventListener(
        'click', 
        function(event) { 
            resize.setSizeType('original');
            resize.notifyChange(); 
        }
    );
    document.querySelector('#thumbnail-size__user-defined').addEventListener(
        'click', 
        function(event) { 
            resize.setSizeType('user-defined'); 
            resize.notifyChange(); 
        }
    );

    document.querySelector('#thumbnail-size__resize').addEventListener(
        'click', resize.onResizeThumbnail);
};

resize.applyOperation = function(operation) {
    if(operation[0] === 'crop') {
        resize.setSelection({
            left: operation[1].left, top: operation[1].top,
            width: operation[1].width, height: operation[1].height});
        resize.setRatio(operation[1].ratio);
    }
    else if(operation[0] === 'resize') {
        resize.setSizeType('user-defined');
        resize.setSize([operation[1].width, operation[1].height]);
    }
};

resize.getSelection = function() {
    var selection = document.querySelector('#selection');

    var transform = selection.getAttribute('transform');
    if(transform === null) {
        throw new Error('No selection');
    }

    var matrix =
        /matrix\((.*)\)/.exec(transform)[1].split(' ').map(parseFloat);
    var left = matrix[4];
    var top = matrix[5];

    var frame = selection.querySelector('#selection__frame');
    var width = parseFloat(frame.getAttribute('width'));
    var height = parseFloat(frame.getAttribute('height'));

    return {left: left, top: top, width: width, height: height};
};

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

    var ratio = null;
    try {
        ratio = resize.getRatio();
    }
    catch(e) {
        // Ignore the error.
    }

    if(ratio !== null && ratio !== undefined) {
        ratio = ratio[0] / ratio[1];
        area.height = Math.round(area.width / ratio);
    }

    var selection = document.querySelector('#selection');
    selection.setAttribute(
        'transform', 'matrix(1 0 0 1 '+area.left+' '+area.top+')');

    var frame = selection.querySelector('#selection__frame');
    frame.setAttribute('width', area.width);
    frame.setAttribute('height', area.height);

    var se_handle = selection.querySelector('#selection__se-handle');
    se_handle.setAttribute('cx', area.width);
    se_handle.setAttribute('cy', area.height);
};

resize.getRatioType = function() {
    var radio_free = document.querySelector('#selection-ratio__free');
    var radio_fixed = document.querySelector('#selection-ratio__fixed');

    if(radio_free.checked) {
        return 'free';
    }
    else if(radio_fixed.checked) {
        return 'fixed';
    }
    else {
        throw new Error('Invalid ratio type');
    }
};

resize.setRatioType = function(type) {
    var radio_free = document.querySelector('#selection-ratio__free');
    var radio_fixed = document.querySelector('#selection-ratio__fixed');
    var width_control = document.querySelector('#selection-ratio__width');
    var height_control = document.querySelector('#selection-ratio__height');
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
            var selection = null;
            try {
                selection = resize.getSelection();
            }
            catch(e) {
                return;
            }
            width_control.value = selection.width;
            height_control.value = selection.height;
        }
    }
    else {
        throw new Error('Unknown ratio type: '+type);
    }

    resize.notifyChange();
};

resize.getRatio = function() {
    var ratio = undefined;

    var free = document.querySelector('#selection-ratio__free');
    var fixed = document.querySelector('#selection-ratio__fixed');

    if(free.checked) {
        ratio = null;
    }
    else if(fixed.checked) {
        var width = document.querySelector('#selection-ratio__width');
        var height = document.querySelector('#selection-ratio__height');
        if(!width.validity.valid || !height.validity.valid) {
            throw new Error('Invalid ratio');
        }
        ratio = [parseFloat(width.value), parseFloat(height.value)];
    }

    return ratio;
};

resize.setRatio = function(ratio) {
    var free = document.querySelector('#selection-ratio__free');
    var fixed = document.querySelector('#selection-ratio__fixed');
    var width = document.querySelector('#selection-ratio__width');
    var height = document.querySelector('#selection-ratio__height');

    if(ratio === null) {
        free.checked = true;
        fixed.checked = false;

        width.disabled = true;
        height.disabled = true;
    }
    else {
        free.checked = false;
        fixed.checked = true;

        width.disabled = false;
        width.value = ratio[0];

        height.disabled = false;
        height.value = ratio[1];
    }
};

resize.getSizeType = function() {
    var original = document.querySelector('#thumbnail-size__original');
    var user_defined = document.querySelector('#thumbnail-size__user-defined');

    if(original.checked) {
        return 'original';
    }
    else if(user_defined.checked) {
        return 'user-defined';
    }
    else {
        throw new Error('Invalid size type');
    }
};

resize.setSizeType = function(type) {
    var original = document.querySelector('#thumbnail-size__original');
    var user_defined = document.querySelector('#thumbnail-size__user-defined');
    var width_control = document.querySelector('#thumbnail-size__width');
    var height_control = document.querySelector('#thumbnail-size__height');
    var resize_control = document.querySelector('#thumbnail-size__resize');
    
    if(type === 'original') {
        original.checked = true;
        user_defined.checked = false;
        width_control.disabled = true;
        height_control.disabled = true;
        resize_control.disabled = true;
    }
    else if(type === 'user-defined') {
        original.checked = false;
        user_defined.checked = true;
        width_control.disabled = false;
        height_control.disabled = false;
        resize_control.disabled = false;
        
        if(width_control.value === '' || height_control.value === '') {
            var selection = null;
            try {
                selection = resize.getSelection();
            }
            catch(e) {
                return;
            }
            width_control.value = selection.width;
            height_control.value = selection.height;
        }
    }
    else {
        throw new Error('Unknown ratio type: '+type);
    }
};

resize.getSize = function() {
    var size = undefined;

    var original = document.querySelector('#thumbnail-size__original');
    var user_defined = document.querySelector('#thumbnail-size__user-defined');
    
    if(original.checked) {
        size = null;
    }
    else if(user_defined.checked) {
        var width = document.querySelector('#thumbnail-size__width');
        var height = document.querySelector('#thumbnail-size__height');
        if(!width.validity.valid || !height.validity.valid) {
            throw new Error('Invalid size');
        }
        size = [parseInt(width.value), parseInt(height.value)];
    }

    return size;
};

resize.setSize = function(size) {
    var original = document.querySelector('#thumbnail-size__original');
    var user_defined = document.querySelector('#thumbnail-size__user-defined');
    var width = document.querySelector('#thumbnail-size__width');
    var height = document.querySelector('#thumbnail-size__height');

    if(size === null) {
        original.checked = true;
        user_defined.checked = false;

        width.disabled = true;
        height.disabled = true;
    }
    else {
        original.checked = false;
        user_defined.checked = true;

        width.disabled = false;
        width.value = size[0];

        height.disabled = false;
        height.value = size[1];
    }
};

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
};

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
};

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

    if(selection.drag.corner === 'selection__nw-handle') {
        area.left += delta[0];
        area.top += delta[1];

        area.width -= delta[0];
        area.height -= delta[1];
    }
    else if(selection.drag.corner === 'selection__se-handle') {
        area.width += delta[0];
        area.height += delta[1];
    }
    else {
        throw new Error('Unknown corner: '+selection.drag.corner);
    }

    resize.setSelection(area);

    selection.drag.position = position;
};

resize.onResizeStop = function(event) {
    var selection = document.querySelector('#selection');
    selection.drag.action = null;
    selection.drag.corner = null;

    var canvas = document.querySelector('#canvas');
    canvas.removeEventListener('mousemove', resize.onResize);
    canvas.removeEventListener('mouseup', resize.onResizeStop);

    resize.notifyChange();
};

resize.onResizeThumbnail = function(event) {
    resize.notifyChange();
}

resize.notifyChange = function() {
    var url = document.querySelector('#canvas').getAttribute('data-derivative');

    var cropParameters = undefined;
    try {
        cropParameters = resize.getSelection();
        cropParameters.ratio = resize.getRatio();
    }
    catch(e) {
        console.log('Cannot notify changes: '+e)
        return;
    }

    var data = {operations: [['crop', cropParameters]]};
    
    if(resize.getSizeType() === 'user-defined') {
        var size = resize.getSize();
        data.operations.push(
            ['resize', { width: size[0], height: size[1] } ] );
    }

    var failure = function(xhr) {
        document.querySelector('html').innerHTML = xhr.responseText;
    };

    var request = new XMLHttpRequest();
    request.addEventListener('load', function(event) {
        if(event.target.status !== 200) {
            return failure(event.target);
        }
        else {
            resize.setSizeType('original');
            derivative = JSON.parse(event.target.response);
            derivative.operations.forEach(resize.applyOperation);

            var thumbnail = document.querySelector("#thumbnail");
            thumbnail.src =
                document.querySelector('#canvas').getAttribute('data-derivative')+
                '/content'
                + '#' + new Date().getTime();
        }
    });
    request.addEventListener('error', function(event) {
        return failure(event.target);
    });
    request.open('PATCH', url);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(data));
};

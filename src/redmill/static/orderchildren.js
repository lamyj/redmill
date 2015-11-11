var orderChildren = {};

/// @brief Initialize the drag and drop.
orderChildren.init = function(url) {
    // CAUTION: drag and drop is not a standard HTML 5 feature
    // It is however present in the working draft
    // http://www.w3.org/html/wg/drafts/html/master/editing.html#dnd
    // As of 2015-11-11, the draggable attribute is present in Firefox, but the
    // dropzone attribute is not.

    // Register events for the drag sources
    [].forEach.call(
        document.querySelectorAll('.children [draggable="true"]'),
        function(element) {
            element.addEventListener('dragstart', orderChildren.onDragStart);
            element.addEventListener('dragend', orderChildren.onDragEnd);
        }
    );

    // Register events for the drop targets
    [].forEach.call(
        document.querySelectorAll('.dropzone'),
        function(element) {
            element.addEventListener('dragenter', orderChildren.onDragEnter);
            element.addEventListener('dragover', orderChildren.onDragOver);
            element.addEventListener(
                'drop', orderChildren.onDrop.bind(undefined, url));
        }
    );
};

/// @brief Return the first parent of a node that matches a condition.
orderChildren.findParent = function(node, condition) {
    var target = node;
    var done=false;
    while(!done) {
        if(condition(target)) {
            done = true;
        }
        else if(target === document) {
            done = true;
        }
        else {
            target = target.parentNode;
        }
    }
    return target;
}

/// @brief Start the drag action.
orderChildren.onDragStart = function(event) {
    var target = orderChildren.findParent(
        event.target, function(x) { return (x.dataset.rmId !== undefined); });
    if(target === document) {
        return;
    }

    event.dataTransfer.setData('text/plain', target.dataset.rmId.toString());
    event.dataTransfer.effectAllowed = 'move';
    event.target.style.opacity = 0.5;
};

/// @brief Insert the drag target at its new location.
orderChildren.onDragEnter = function(event) {
    var destination = orderChildren.findParent(
        event.target, function(x) {
            return (
                x.classList !== undefined &&
                x.classList.contains('dropzone'));
        }
    );
    if(destination === document) {
        return;
    }

    var data = event.dataTransfer.getData('text/plain');
    var source = document.querySelector(
        'ul.children [data-rm-id="'+data+'"]').parentNode;

    if(source === destination) {
        return;
    }

    // Find <li> containing source
    var parent = document.querySelector('ul.children');
    var source_li = orderChildren.findParent(
        source, function(x) { return x.localName === 'li'});

    // Insert it after destination
    var destination_li = orderChildren.findParent(
        destination, function(x) { return x.localName === 'li'});
    parent.insertBefore(source_li, destination_li.nextSibling);
};

/// @brief Mark the event target as a drop zone.
orderChildren.onDragOver = function(event) {
    event.preventDefault();
};

/// @brief Re-order the children.
orderChildren.onDrop = function(url, event) {
    event.preventDefault();

    var ids = [];
    [].forEach.call(
        document.querySelectorAll('ul.children [data-rm-id]'),
        function(x) { ids.push(parseInt(x.dataset.rmId)); }
    );

    function onFailure(xhr) {
        document.querySelector('html').innerHTML = xhr.responseText;
    };

    var request = new XMLHttpRequest();
    request.addEventListener('load', function(event) {
        if(event.target.status !== 200) {
            return onFailure(event.target);
        }
        else {
            window.location.href = window.location;
        }
    });
    request.addEventListener('error', onFailure);
    request.open('POST', url);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(ids));
};

/// @brief Stop the drag action.
orderChildren.onDragEnd = function(event) {
    event.target.style.opacity = 1;
};

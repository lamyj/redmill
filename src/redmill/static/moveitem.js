var moveItem = {};

/// @brief Initialize the event handlers.
moveItem.init = function(url, lockRoot) {
    // Show and hide the dialog
    var move = document.querySelector('#move');
    if(move) {
        move.addEventListener('click', moveItem.showDialog);
    }
    document.addEventListener('keypress', moveItem.onEscape);

    if(lockRoot) {
        document.querySelector('ul.tree span[data-rm-id=""]').setAttribute(
            'disabled', 'disabled');
    }

    // Event handlers for each album item in the hierarchy
    [].forEach.call(
        document.querySelectorAll('ul.tree span'),
        function(album) {
            album.addEventListener('mouseover', moveItem.onAlbumMouseOver);
            album.addEventListener('mouseout', moveItem.onAlbumMouseOut);
            album.addEventListener('click', moveItem.onAlbumClick);
        }
    );

    // Dialog buttons
    document.querySelector('#overlay_move').addEventListener(
        'click', moveItem.onMoveClick.bind(undefined, url));
    document.querySelector('#cancel_move').addEventListener(
        'click', moveItem.onCancelClick);
};

/// @brief Show the move dialog.
moveItem.showDialog = function() {
    document.querySelector('#overlay').style.display = 'block';
    [].forEach.call(
        document.querySelectorAll('ul.tree span'),
        function(x) { x.classList.remove('selected'); });
    document.querySelector('#overlay_move').setAttribute('disabled', 'disabled');
};

/// @brief Hide the move dialog if ESC is pressed.
moveItem.onEscape = function(e) {
    if(e.keyCode === 27) {
        moveItem.onCancelClick();
    }
};

/// @brief Handler called when the mouse points is over an album.
moveItem.onAlbumMouseOver = function(e) { e.target.classList.add('hover'); };

/// @brief Handler called when the mouse points exits an album.
moveItem.onAlbumMouseOut = function(e) { e.target.classList.remove('hover'); };

/// @brief Handler called when an album is clicked.
moveItem.onAlbumClick = function(e) {
    if(!e.target.getAttribute('disabled')) {
        [].forEach.call(
            document.querySelectorAll('ul.tree span'),
            function(x) { x.classList.remove('selected'); });
        e.target.classList.add('selected');
        document.querySelector('#overlay_move').removeAttribute('disabled');
    }
};

/// @brief Handler called when the move button of the dialog is clicked.
moveItem.onMoveClick = function(url) {
    var newParentId =
        parseInt(document.querySelector('ul.tree .selected').dataset.rmId) || null;
    var data = { parent_id: newParentId };

    function onFailure(xhr) {
        document.querySelector('html').innerHTML = xhr.responseText;
    };

    var request = new XMLHttpRequest();
    request.addEventListener('load', function(event) {
        if(event.target.status !== 200) {
            return onFailure(event.target);
        }
        else {
            window.location.href = url;
        }
    });
    request.addEventListener('error', onFailure);
    request.open('PATCH', url);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(data));
};

/// @brief Handler called when the cancel button of the dialog is clicked.
moveItem.onCancelClick = function() {
    document.querySelector('#overlay').style.display = 'none';
};

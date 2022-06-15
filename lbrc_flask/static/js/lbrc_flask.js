function standard_status_actions(response) {
    if (response.status == 205) {
        console.log('Reloading')
        location.reload();
    } else if (response.status >= 200 && response.status < 300) {
        return response
    } else {
        response.text().then(function (text) {
            modal = $('#errorModal')
            modal.find('#error_status').text(response.status);
            modal.find('#error_status_text').text(response.statusText);
            modal.find('#error_text').text(text);
            modal.modal('show');
        });
    }
}


function parseJSON(response) {
    return response.json()
}


function enable_child_control_on_parent_value(parent_selector, child_selector, enabled_value) {
    let parent = document.querySelector(parent_selector);
    let child = document.querySelector(child_selector);

    updater = function () {
        if (parent.value == enabled_value) {
            child.removeAttribute('disabled');
        } else {
            child.setAttribute('disabled', ' ');
        }        
    }

    updater();
    parent.onchange = updater;
}

function select2_remote(select_selector, url) {
    $(select_selector).select2({
        ajax: {
            url: url,
            dataType: 'json',
            delay: 500,
        }
    });
}

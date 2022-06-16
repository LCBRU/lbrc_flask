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


function _render_modal_on_show(event){
    var mod_elem = this;

    [].forEach.call(event.relatedTarget.attributes, function(attr) {
        if (/^data-/.test(attr.name)) {
            var name = attr.name.substr(5);
            var input_elem = mod_elem.querySelector(`#${name}`);
            if (!!input_elem) {
                if (typeof input_elem.value !='undefined'){
                    input_elem.value = attr.value;
                } else {
                    input_elem.innerHTML = attr.value;
                }
            }
        }
    })
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', _render_modal_on_show);
});

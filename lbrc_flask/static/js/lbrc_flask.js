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

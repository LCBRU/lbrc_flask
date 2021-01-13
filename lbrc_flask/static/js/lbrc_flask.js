function standard_status_actions(response) {
    if (response.status == 205) {
        console.log('Reloading')
        location.reload();
    } else if (response.status >= 200 && response.status < 300) {
        return response
    } else {
        var error = new Error(response.statusText)
        error.response = response
        throw error
    }
}


function parseJSON(response) {
    return response.json()
}

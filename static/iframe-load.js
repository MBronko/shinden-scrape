let iframe = document.getElementById('iframe')
function show_player(iframe_data){
    iframe.innerHTML = iframe_data
    console.log(iframe_data)
}

function request_player(player_id) {
    iframe.innerHTML = '<div class="iframe-loading"></div>'

    let xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4){
            if (xmlHttp.status === 200){
                show_player(xmlHttp.responseText);
            }
            else {
                iframe.innerHTML = 'An unexpected error occured';
            }
        }
    }
    xmlHttp.open("GET", location.origin + '/player/' + player_id, true);
    xmlHttp.send(null);
}
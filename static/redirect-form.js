let base_shinden_url = 'https://shinden.pl'

document.getElementById('redirect-to-shinden').href = base_shinden_url + location.pathname;

document.getElementById('redirect-button').addEventListener('click', () => {
    let redirect_url = document.getElementById('redirect').value;

    if(redirect_url.startsWith(base_shinden_url)){
        window.location.href = location.origin + redirect_url.slice(base_shinden_url.length);
    }
    else{
        document.getElementById('redirect-error').innerText = 'Invalid url';
    }
});
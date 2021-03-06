from flask import Flask, request, Response, render_template, url_for, redirect
from Web_scraping import *

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/series/<path:series_id>')
def series(series_id):
    return episodes(series_id)


@app.route('/series/<path:series_id>/episodes')
def episodes(series_id):
    series_info = get_series_info(series_id)
    episode_list = get_episode_list(series_id)

    kwargs = {
        'include_series_template': True,
        'series_info': series_info,
        'episode_list': episode_list,
        'players_list': []
    }
    return render_template('index.html', **kwargs)


@app.route('/episode/<path:series_id>/view/<path:episode_id>')
def episode(series_id, episode_id):
    series_info = get_series_info(series_id)
    episode_data = get_episode_list(series_id)
    player_list = get_player_list(series_id, episode_id)

    kwargs = {
        'include_series_template': True,
        'series_info': series_info,
        'episode_list': episode_data,
        'player_list': player_list
    }
    return render_template('index.html', **kwargs)


@app.route('/player/<path:player_id>')
def player(player_id):
    return get_player(player_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

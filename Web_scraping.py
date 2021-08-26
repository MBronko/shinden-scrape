import requests
import re
from bs4 import BeautifulSoup
import json
import time
from typing import Union

base_shinden_url = 'https://shinden.pl'


def simple_get(url: str, cookies=None, headers=None) -> requests.Response:
    if not headers:
        headers = {
            "Accept-Language": "pl"
        }
    if not cookies:
        cookies = {}
    return requests.get(url, headers=headers, cookies=cookies)


def get_series_info(series_id: str):
    url = f'{base_shinden_url}/series/{series_id}'

    res = simple_get(url)
    container = BeautifulSoup(res.content, 'html.parser').find('div', class_='l-main-contantainer')

    title = container.find('h1', class_='page-title').text
    if title.startswith('Anime: '):
        title = title[len('Anime: '):]

    left_menu = container.find('aside', class_='info-aside aside-title')

    rating_data = left_menu.find('div', class_='bd')

    series_info = [a.text for a in left_menu.find('dl', class_='info-aside-list').find_all('dd')[:5]]

    try:
        episodes = int(series_info[3])
    except ValueError:
        episodes = series_info[4]

    series_data = {
        'title': title,
        'desc': container.find('div', id='description').find().text,
        'genres': [li.find().text for li in container.find('ul', class_='tags').find_all('li')],
        'cover_img': base_shinden_url + left_menu.find('img', class_='info-aside-img')['src'],
        'rating': f"{rating_data.find('span', class_='info-aside-rating-user').text}/10",
        'votes': rating_data.find('span', class_='h6').text.split(' ')[0],
        'anime_type': series_info[0],
        'status': series_info[1],
        'emission_date': series_info[2],
        'episodes': episodes
    }
    return series_data


def get_episode_list(series_id: str) -> list[dict[str, str]]:
    url = f'{base_shinden_url}/series/{series_id}/episodes'

    response = simple_get(url)
    body = BeautifulSoup(response.content, 'html.parser')
    episode_table = body.find('tbody', class_='list-episode-checkboxes')

    episode_list = []
    for row in episode_table.find_all('tr'):
        columns = row.find_all('td')

        languages = [span.attrs['class'] for span in columns[3].find_all()]

        buf = {
            'episode': columns[0].text,
            'title': columns[1].text,
            'online': 'cell-check' if columns[2].find().attrs['class'][2] == 'fa-check' else 'cell-times',
            'langs': [' '.join(classes) for classes in languages],
            'release_date': columns[4].text,
            'url': f"{base_shinden_url}{columns[5].find()['href']}"[len(base_shinden_url):]
        }
        episode_list.append(buf)

    print(episode_list)
    return episode_list


def get_player_list(series_id: str, episode_id: str) -> list[dict[str, Union[str, dict[str, str]]]]:
    url = f'{base_shinden_url}/episode/{series_id}/view/{episode_id}'
    response = simple_get(url)

    body = BeautifulSoup(response.content, 'html.parser')
    player_table = body.find('div', class_='table-responsive').find('tbody')

    episode_number = body.find('dl', class_='info-aside-list').find('dd').text

    player_list = []
    for row in player_table.find_all('tr'):
        columns: list[BeautifulSoup] = row.find_all('td')

        res_favicon = columns[1].find('span', class_='fav-ico')
        if res_favicon:
            subs_fav_icon = res_favicon.attrs['style'].split('(')[1][0:-1]
            subs_authors = res_favicon.attrs['title']
        else:
            subs_fav_icon = ''
            subs_authors = ''

        buf = {
            'subs-fav-icon-url': subs_fav_icon,
            'subs-authors': subs_authors,
            'episode_number': episode_number,
        }
        buf |= json.loads(columns[5].find('a').attrs['data-episode'])

        player_list.append(buf)
    return player_list


def get_player(player_id: str) -> str:
    auth = 'X2d1ZXN0XzowLDUsMjEwMDAwMDAsMjU1LDQxNzQyOTM2NDQ%3D'

    cookie = {
        "api.shinden": "s:ibHWJQMP1Xuf0iuR6qqaYOlE-_IliWzv.RwDfx0R2PmOu5Mso4S1VHksxEzmZNv2cmuhUYctoSck"
    }

    shinden_api_url = 'https://api4.shinden.pl/xhr'

    load_iframe_url = f'{shinden_api_url}/{player_id}/player_load?auth={auth}'
    show_iframe_url = f'{shinden_api_url}/{player_id}/player_show?auth={auth}&width=765&height=-1'

    load = simple_get(load_iframe_url, cookies=cookie)

    time.sleep(5)

    res = simple_get(show_iframe_url, cookies=cookie)

    iframe = BeautifulSoup(res.content, 'html.parser').find('iframe')

    if iframe:
        return str(iframe)
    else:
        return 'Video player not found'

import requests
import re
from bs4 import BeautifulSoup
import json
import time
from typing import Union

base_shinden_url = 'https://shinden.pl'

url_series = 'https://shinden.pl/series/57630-seirei-gensouki'
url_episode_list = 'https://shinden.pl/series/57630-seirei-gensouki/episodes'
url_episode = 'https://shinden.pl/episode/57630-seirei-gensouki/view/202535'

url_episode_list2 = 'https://shinden.pl/series/56421-isekai-maou-to-shoukan-shoujo-no-dorei-majutsu-omega/episodes'
url_episode2 = 'https://shinden.pl/episode/56421-isekai-maou-to-shoukan-shoujo-no-dorei-majutsu-omega/view/200409'

test_series_id = '57630-seirei-gensouki'


def simple_get(url: str, cookies=None, headers=None) -> requests.Response:
    if not headers:
        headers = {
            "Accept-Language": "pl"
        }
    if not cookies:
        cookies = {}
    return requests.get(url, headers=headers, cookies=cookies)


def get_series_info(series_id: str):
    return True  # todo


def get_episode_list(series_id: str) -> list[dict[str, str]]:
    url = f'{base_shinden_url}/series/{series_id}/episodes'

    response = simple_get(url)
    body = BeautifulSoup(response.content, 'html.parser')
    episode_table = body.find('tbody', class_='list-episode-checkboxes')

    episode_list = []
    for row in episode_table.find_all('tr'):
        columns = row.find_all('td')

        languages = [span['title'] for span in columns[3].find_all()]

        buf = {
            'episode': columns[0].text,
            'title': columns[1].text,
            'online': columns[2].find().attrs['class'][2] == 'fa-check',
            'languages': ', '.join(languages),
            'release_date': columns[4].text,
            'url': f"{base_shinden_url}{columns[5].find()['href']}"[len(base_shinden_url):]
        }
        episode_list.append(buf)

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
            **json.loads(columns[5].find('a').attrs['data-episode'])
        }
        player_list.append(buf)
    # print(player_list)
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

    try:
        iframe_url = iframe['src']
        if iframe_url.startswith('//'):
            iframe_url = 'https:' + iframe_url

        return iframe_url
    except TypeError:
        return ''

#
# for player in get_episode(url_episode):
#     src = get_player(player['data-episode']['online_id'])
#     iframe_string = f'<iframe allowfullscreen="" frameborder="0" height="431" src="{src}" width="765"></iframe>'
#     print(iframe_string)

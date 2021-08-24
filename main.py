import requests
import re
from bs4 import BeautifulSoup
import json
import time
from typing import Union

base_url = 'https://shinden.pl'

url_series = 'https://shinden.pl/series/57630-seirei-gensouki'
url_episode_list = 'https://shinden.pl/series/57630-seirei-gensouki/episodes'
url_episode = 'https://shinden.pl/episode/57630-seirei-gensouki/view/202535'

url_episode_list2 = 'https://shinden.pl/series/56421-isekai-maou-to-shoukan-shoujo-no-dorei-majutsu-omega/episodes'
url_episode2 = 'https://shinden.pl/episode/56421-isekai-maou-to-shoukan-shoujo-no-dorei-majutsu-omega/view/200409'


def simple_get(url: str, cookies=None, headers=None) -> requests.Response:
    if not headers:
        headers = {
            "Accept-Language": "pl"
        }
    if not cookies:
        cookies = {}
    return requests.get(url, headers=headers, cookies=cookies)


def get_episode_list(url: str) -> list[dict[str, str]]:
    if not re.match(f'{base_url}/series/.*/episodes', url):
        print('error')
        return []

    response = simple_get(url)
    print(sorted(response.headers.items()))
    print(response.content)
    body = BeautifulSoup(response.content, 'html.parser')
    episode_table = body.find('tbody', class_='list-episode-checkboxes')

    episode_list = []
    for row in episode_table.find_all('tr'):
        columns = row.find_all('td')

        buf = {
            'episode': columns[0].text,
            'title': columns[1].text,
            'online': columns[2].find().attrs['class'][2] == 'fa-check',
            'lang': columns[3].text,  # todo
            'release_date': columns[4].text,
            'url': f"{base_url}{columns[5].find()['href']}"
        }
        episode_list.append(buf)

    return episode_list


def get_episode(url: str) -> list[dict[str, Union[str, dict[str, str]]]]:
    if not re.match(f'{base_url}/episode/.*/view/.*', url):
        print('error')
        return []

    response = simple_get(url)

    body = BeautifulSoup(response.content, 'html.parser')
    player_table = body.find('div', class_='table-responsive').find('tbody')

    player_list = []
    for row in player_table.find_all('tr'):
        columns: list[BeautifulSoup] = row.find_all('td')

        res_favicon = columns[1].find('span', class_='fav-ico')
        if res_favicon:
            subs_fav_icon = res_favicon.attrs['style'].split('(')[1][0:-1]
            subs_authors = res_favicon.attrs['title']
        else:
            subs_fav_icon = ''
            subs_authors = 'noname'

        # subs_lang_spans = columns[3].find_all('span')
        # if len(subs_lang_spans) > 1:
        #     subs_lang = subs_lang_spans[1].text
        # else:
        #     subs_lang = ''

        buf = {
            # 'service': columns[0].text,
            # 'res': columns[1].text,
            'subs-fav-icon-url': subs_fav_icon,
            'subs-authors': subs_authors,
            # 'audio-lang': columns[2].find_all('span')[1].text,
            # 'subs-lang': subs_lang,
            # 'added-date': columns[4].text,
            'data-episode': json.loads(columns[5].find('a').attrs['data-episode'])
        }
        player_list.append(buf)
    print(player_list)
    return player_list


auth = 'X2d1ZXN0XzowLDUsMjEwMDAwMDAsMjU1LDQxNzQyOTM2NDQ%3D'

cookie = {
    "api.shinden": "s:ibHWJQMP1Xuf0iuR6qqaYOlE-_IliWzv.RwDfx0R2PmOu5Mso4S1VHksxEzmZNv2cmuhUYctoSck"
}

for player in get_episode(url_episode):
    player_id = player['data-episode']['online_id']

    iframe_load_url = f'https://api4.shinden.pl/xhr/{player_id}/player_load?auth={auth}'
    iframe_url = f'https://api4.shinden.pl/xhr/{player_id}/player_show?auth={auth}&width=765&height=-1'

    load = simple_get(iframe_load_url, cookies=cookie)

    time.sleep(5)

    res = simple_get(iframe_url, cookies=cookie)

    iframe = BeautifulSoup(res.content, 'html.parser').find('iframe')

    try:
        src = iframe['src']
        if src.startswith('//'):
            src = 'https:' + src

        iframe_string = f'<iframe allowfullscreen="" frameborder="0" height="431" scrolling="no" src="{src}" width="765"></iframe>'

        print(iframe_string)
    except TypeError:
        pass

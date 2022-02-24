from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from logging.handlers import RotatingFileHandler
import inspect
import json
import logging
import os
import random

app_name = os.path.splitext(os.path.basename(__file__))[0]
module_path = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)
log_file_path = os.path.join(module_path, f'{app_name}.log')
rfh = RotatingFileHandler(log_file_path, maxBytes=8388608, backupCount=8)
rfh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rfh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(rfh)
logger.addHandler(ch)

client_secrets_file_path = os.path.join(module_path, 'secrets', 'client_secrets.json')
users_file_path = os.path.join(module_path, 'secrets', 'users.json')
scopes = ['https://www.googleapis.com/auth/youtube']
api_service_name = 'youtube'
api_version = 'v3'
youtube = None
playlists: list[dict] = []
snippet = 'snippet'
title = 'title'
id = 'id'
playlistItems = 'playlistItems'

def choose_playlist() -> int:
    prompt = ''
    idx = 0
    for playlist in playlists:
        name = playlist[snippet][title]
        prompt += f'{idx} - {name}\n'
        idx += 1
    prompt += 'Playlist? '
    while True:
        answer = input(prompt)
        if not answer:
            return None
        try:
            idx = int(answer)
        except:
            continue
        if idx < 0 or idx >= len(playlists):
            continue
        break
    return idx


def cache_playlist_items(playlistId: str) -> list[dict]:
    playlist_items: list[dict] = []
    nextPageToken = None
    while True:
        print('.', end='')
        resp: dict = youtube.playlistItems().list(
            part=snippet,
            pageToken=nextPageToken,
            playlistId=playlistId,
            maxResults=50).execute()
        playlist_items.extend(resp['items'])
        if 'nextPageToken' in resp.keys():
            nextPageToken = resp['nextPageToken']
        else:
            break
    return playlist_items


def cache():
    global playlists
    playlists.clear()
    all_playlists = {
        id: None,
        snippet: {
            title: '< All Playlists >',
        }
    }
    playlists.append(all_playlists)
    nextPageToken = None
    print('Caching', end='')
    while True:
        print('.', end='')
        resp: dict = youtube.playlists().list(
            part=snippet,
            pageToken=nextPageToken,
            mine=True,
            maxResults=50).execute()
        for item in resp['items']:
            item[playlistItems] = cache_playlist_items(item[id])
        playlists.extend(resp['items'])
        if 'nextPageToken' in resp.keys():
            nextPageToken = resp['nextPageToken']
        else:
            break
    print()


def dump_playlist(playlist: list):
    if playlist[id] is None:
        return
    playlist_items = playlist[playlistItems]
    total = f'({len(playlist_items)} total)'
    logger.info(f'{playlist[snippet][title]} {total}')
    for playlist_item in playlist_items:
        logger.info(f'  {playlist_item[snippet][title]}')
    logger.info(f'  {total}')


def dump_playlists():
    for playlist in playlists:
        dump_playlist(playlist)


def dump():
    idx = choose_playlist()
    if idx is None:
        return
    if idx == 0:
        dump_playlists()
    else:
        dump_playlist(playlists[idx])


def by_title(playlist_item: dict):
    return playlist_item[snippet][title]


def sort_playlist(playlist: list, reverse: bool = False):
    if playlist[id] is None:
        return
    platlist_items: list = playlist[playlistItems]
    platlist_items.sort(key=by_title, reverse=reverse)
    dump_playlist(playlist)


def sort_playlists(reverse: bool = False):
    global playlists
    for playlist in playlists:
        sort_playlist(playlist, reverse)


def sort_a_to_z():
    global playlists
    idx = choose_playlist()
    if idx is None:
        return
    if idx == 0:
        sort_playlists()
    else:
        sort_playlist(playlists[idx])


def sort_z_to_a():
    global playlists
    idx = choose_playlist()
    if idx is None:
        return
    if idx == 0:
        sort_playlists(True)
    else:
        sort_playlist(playlists[idx], True)


def randomize_playlist(playlist: list):
    if playlist[id] is None:
        return
    random.shuffle(playlist[playlistItems])
    dump_playlist(playlist)


def randomize_playlists():
    global playlists
    for playlist in playlists:
        randomize_playlist(playlist)


def randomize():
    global playlists
    idx = choose_playlist()
    if idx is None:
        return
    if idx == 0:
        randomize_playlists()
    else:
        randomize_playlist(playlists[idx])


def update_playlist(playlist: list):
    if playlist[id] is None:
        return
    print(f'Updating "{playlist[snippet][title]}"', end='')
    idx = 0
    for playlist_item in playlist[playlistItems]:
        print('.', end='')
        body = {
            'id': playlist_item[id],
            snippet: {
                'playlistId': playlist[id],
                'resourceId': {
                    'kind': playlist_item[snippet]['resourceId']['kind'],
                    'videoId': playlist_item[snippet]['resourceId']['videoId']
                },
                'position': idx
            }
        }
        youtube.playlistItems().update(
            part=snippet,
            body=body).execute()
        idx += 1
    print()


def update_playlists():
    global playlists
    for playlist in playlists:
        update_playlist(playlist)


def update():
    global playlists
    idx = choose_playlist()
    if idx is None:
        return
    if idx == 0:
        update_playlists
    else:
        update_playlist(playlists[idx])


actions = {
    'Cache': cache,
    'Dump': dump,
    'Sort A-Z': sort_a_to_z,
    'Sort Z-A': sort_z_to_a,
    'Randomize': randomize,
    'Update': update,
}


def get_new_user_creds(name: str) -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file_path, scopes)
    creds = flow.run_local_server(
        host='localhost', port=8080, authorization_prompt_message='Please visit this URL: {url}',
        success_message='Authorization complete. You may close this window.', open_browser=True)
    user = {
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'name': name,
        'refresh_token': creds.refresh_token,
        'scopes': creds.scopes,
        'token_uri': creds.token_uri,
        'token': creds.token,
    }
    users = read_users()
    users.append(user)
    write_users(users)
    return creds


def json_dumps(obj) -> str:
    return json.dumps(obj, sort_keys=True, indent=2)


def write_users(users: list[dict]):
    f = open(users_file_path, 'w')
    f.write(json_dumps(users))
    f.close()


def read_users() -> list[dict]:
    f = open(users_file_path, 'r')
    users: list = json.load(f)
    f.close()
    return users


def main():
    global youtube

    logger.debug(f'@ {inspect.stack()[0][3]}')
    logger.debug(app_name)

    if not os.path.isfile(client_secrets_file_path):
        logger.warning(f'Could not file "{client_secrets_file_path}"')
        return

    if not os.path.isfile(users_file_path):
        write_users([])
    users = read_users()
    new_user = {
        'name': '< New User >'
    }
    users.insert(0, new_user)

    while True:
        prompt = ''
        idx = 0
        for user in users:
            prompt += f'{idx} - {user["name"]}\n'
            idx += 1
        name = None
        creds = None
        prompt += 'User? '
        answer = input(prompt)
        if not answer:
            return
        try:
            idx = int(answer)
        except:
            continue
        if idx < 0 or idx >= len(users):
            continue
        break

    if idx == 0:
        name = str(input('Name? '))
        creds = get_new_user_creds(name)
    else:
        user = users[idx]
        name = user['name']
        creds = Credentials.from_authorized_user_info(user)
    logger.info(f'User: {name}')
    youtube = build(api_service_name, api_version, credentials=creds)

    while True:
        prompt = ''
        idx = 0
        for action in actions:
            prompt += f'{idx} - {action}\n'
            idx += 1
        prompt += 'Action? '
        answer = input(prompt)
        if not answer:
            return
        try:
            idx = int(answer)
        except:
            continue
        if idx < 0 or idx >= len(actions):
            continue
        action = list(actions)[idx]
        logger.info(f'Action: {action}')
        actions[action]()


if __name__ == '__main__':
    main()


# https://developers.google.com/resources/api-libraries/documentation/youtube/v3/python/latest/

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

import os
import requests
import json
import time
from tqdm import tqdm
import multiprocessing
from functools import partial
from multiprocessing.pool import ThreadPool

public_matches_path = 'data/public_matches_p2.json'
matches_details_path = 'data/matches_details_p2.json'

api_key = os.getenv('OPENDOTA_KEY')
if api_key is not None:
    print('Using api key!')


def load_json(url):
    response = requests.get(url)
    return json.loads(response.text)

def save_to_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def _init(l):
    global lock
    lock = l

matches_details = []
def download_one_match(api_key, save, i_and_m_id):
    global matches_details

    i, m_id = i_and_m_id
    url = f'https://api.opendota.com/api/matches/{m_id}'
    if api_key is not None:
        url += f'?api_key={api_key}'
        time.sleep(0.05)
    else:
        time.sleep(0.5)  # free api limit

    try:
        json_response = load_json(url)
        if 'error' in json_response:
            print('Error:')
            print(json_response)
            time.sleep(1.0)
            return
        matches_details.append(json_response)
        if (i + 1) % 1_000 == 0:
            lock.acquire()
            save(matches_details)
            lock.release()
    except Exception as ex:
        print('Exception is handled:')
        print(ex)

def download_public_matches(last_match_id=6808764903, n=1_000):
    public_matches = []
    matches_data = []
    save = partial(save_to_json, public_matches_path)

    for i in (pbar := tqdm(range(n))):
        pbar.set_description(f'Public_matches: {len(public_matches)}')
        
        url = f'https://api.opendota.com/api/publicMatches?less_than_match_id={last_match_id}'
        if api_key is not None and False:
            # TEMP:
            # There is a bug in API for "publicMatches" with api_key request
            url += f'?api_key={api_key}'
            time.sleep(0.1)
        else:
            time.sleep(0.8)  # free api limit

        try:
            json_response = load_json(url)
            if 'error' in json_response:
                print('Error:')
                print(json_response)
                time.sleep(0.5)
            matches_data.extend(json_response)

            matches_id = [i['match_id'] for i in json_response]
            # sanity check for matches uniqueness, see tqdm while running
            public_matches = list(set(matches_id) | set(public_matches))
            last_match_id = min(matches_id)  # to download only unique matches
        except Exception as ex:
            print('Exception is handled:')
            print(ex)
            last_match_id -= 100
        
        if i % 100 == 0:
            save(matches_data)
        
    print(f'{len(set(public_matches))} unique matches downloaded')
    save(matches_data)


def download_matches_details(use_pool=True):
    global matches_details

    with open(public_matches_path) as f:
        public_matches = json.load(f)
    matches_id = set([m['match_id'] for m in public_matches])
    print(f'{len(matches_id)} matches in {public_matches_path}')

    if os.path.exists(matches_details_path):
        with open(matches_details_path) as f:
            matches_details = json.load(f)
        already_downloaded_matches = set([m.get('match_id') \
            for m in matches_details])
        print(f'{len(already_downloaded_matches)} matches already '
              f'downloaded (in {matches_details_path})')
        matches_id = matches_id - already_downloaded_matches
    matches_id = list(matches_id)

    save = partial(save_to_json, matches_details_path)
    download_match = partial(download_one_match, api_key, save)

    print(f'Downloading {len(matches_id)} matches details')
    if use_pool and api_key is not None:
        l = multiprocessing.Lock()
        # OR multiprocessing.Pool
        with ThreadPool(8, initializer=_init, initargs=(l,)) as p:
            _ = list(tqdm(p.imap(download_match,
                     enumerate(matches_id)), total=len(matches_id)))
    else:
        for i, m_id in tqdm(enumerate(matches_id),
                            total=len(matches_id)):
            download_match((i, m_id))

    print('All matches details downloaded')
    save(matches_details)


if __name__ == '__main__':
    # download_public_matches()
    download_matches_details()


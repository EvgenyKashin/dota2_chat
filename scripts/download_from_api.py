import os
import requests
import json
import time
from tqdm import tqdm

public_matches_path = 'data/public_matches.json'
matches_details_path = 'data/matches_details.json'

api_key = os.getenv('OPENDOTA_KEY')
if api_key is not None:
    print('Using api key!')


def load_json(url):
    response = requests.get(url)
    return json.loads(response.text)

def download_public_matches(last_match_id=6808764903, n=1_000):
    public_matches = []
    matches_data = []

    def save():
        with open(public_matches_path, 'w') as f:
            json.dump(matches_data, f)

    for i in (pbar := tqdm(range(n))):
        pbar.set_description(f'Public_matches: {len(public_matches)}')
        time.sleep(1)
        
        url = f'https://api.opendota.com/api/publicMatches?less_than_match_id={last_match_id}'
        try:
            json_response = load_json(url)
            matches_data.extend(json_response)

            matches_id = [i['match_id'] for i in json_response]
            public_matches = list(set(matches_id) | set(public_matches))
            last_match_id = min(matches_id)  # to download only unique matches
        except Exception as ex:
            print('Exception is handled:')
            print(ex)
            last_match_id -= 100
        
        if i % 50 == 0:
            save()
        
    print(f'{len(set(public_matches))} unique matches downloaded')
    save()


def download_matches_details():
    matches_details = []

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

    def save():
        with open(matches_details_path, 'w') as f:
            json.dump(matches_details, f)

    print(f'Downloading {len(matches_id)} matches details')
    for i, m_id in tqdm(enumerate(matches_id),
                        total=len(matches_id)):
        url = f'https://api.opendota.com/api/matches/{m_id}'
        if api_key is not None:
            url += f'?api_key={api_key}'
        else:
            time.sleep(0.5)  # free api limit

        try:
            json_responce = load_json(url)
            if 'error' in json_responce:
                print('Error:')
                print(json_responce)
                time.sleep(1)
                continue
            matches_details.append(json_responce)
            if i % 200 == 0:
                save()
        except Exception as ex:
            print('Exception is handled:')
            print(ex)

    print('All matches details downloaded')
    save()


if __name__ == '__main__':
    # download_public_matches()
    download_matches_details()


import requests
import json
import time
from tqdm import tqdm

# url = 'https://api.opendota.com/api/parsedMatches?id=6809572336'
# url = 'https://api.opendota.com/api/findMatches?id=6809753734'


def load_json(url):
    response = requests.get(url)
    return json.loads(response.text)

def download_public_matches(last_match_id=6808764903, n=1_000):
    public_matches = []
    matches_data = []

    def save():
        with open('data/public_matches.json', 'w') as f:
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
            print(ex.message)
            last_match_id -= 100
        
        if i % 50 == 0:
            save()
        
    print(f'{len(set(public_matches))} unique matches downloaded')
    save()


def download_matches_details():
    matches_details = []

    with open('data/public_matches.json') as f:
        public_matches = json.load(f)
    matches_id = list(set([m['match_id'] for m in public_matches]))

    def save():
        with open('data/matches_details.json', 'w') as f:
            json.dump(matches_details, f)

    print(f'Downloading {len(matches_id)} matches details')
    for i, m_id in (pbar := tqdm(enumerate(matches_id),
                    total=len(matches_id))):
        url = f'https://api.opendota.com/api/matches/{m_id}'
        try:
            json_responce = load_json(url)
            matches_details.append(json_responce)
            if i % 100 == 0:
                save()
        except Exception as ex:
            print(ex.message)

    print('All matches details downloaded')
    save()


if __name__ == '__main__':
    # download_public_matches()
    download_matches_details()


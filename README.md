# Winning Communication: Can the outcome of a Dota2 match be predicted from in-game chat?
## Data
We use the [OpenDota API](https://www.opendota.com/api-keys) to download matches and in-game chat. 
## Usage
To download data:
- `conda env create --name dota2_env -f environment.yml`
- `export OPENDOTA_KEY=YOUR_API_KEY`
- `python scripts/download_from_api.py`

Notebooks:
- `scripts/Data_collection_and_preprocessing.ipynb`
- `scripts/Dataset_EDA.ipynb`

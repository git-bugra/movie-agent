import json
import requests
import pathlib as pl

def load_config(filename):
    """

    """
    with open(filename, "r") as f:
        return json.load(f)

def download_file(url, destination):
    """

    """
    response=requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            return True
    else:
        raise Exception(f'Download failed. Server threw {response.status_code}.')

def print_progress():
    """

    """

def fetch_imdb_dataset():
    requests_config = load_config('dataset.json')
    folder = requests_config['download_dir']
    for dataset in requests_config['datasets']:
        url = dataset['url']
        filename = dataset['filename']
        destination = pl.Path(folder) / filename
        download_file(url, destination)

if __name__ == '__main__':
    fetch_imdb_dataset()

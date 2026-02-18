import json
import requests
import pathlib as pl
from tqdm import tqdm

class DatasetDownloader():

    def __init__(self):
        self.json='dataset.json'
        self.response=None

    def _load_config(self):
        """
        Load configuration file for file operations.
        """
        try:
            with open(self.json, "r") as f:
                return json.load(f)
        except ValueError:
            raise Exception('Failed to open .json config.')
        except FileNotFoundError:
            raise Exception('Failed to find .json config.')

    def _download_file(self, url, destination, stream=True):
        """
        Open and write dataset.
        """
        self.response=requests.get(url, stream=stream)
        total_chunks=(float(self.response.headers.get('Content-Length'))+8191)//8192
        if self.response.status_code == 200:
            with open(destination, "wb") as f:
                for chunk in tqdm(self.response.iter_content(chunk_size=8192), total=total_chunks, unit='B', unit_scale=True, bar_format='\033[37m{l_bar}\033[32m{bar}\033[37m{r_bar}', ncols=120, desc=f'downloading datasets'):
                    f.write(chunk)
                return True
        else:
            raise Exception(f'Download failed. Server threw status code: {self.response.status_code}.')

    def fetch_imdb_dataset(self):
        """
        Orchestrate full file operation.
        """
        requests_config=self._load_config()
        folder=requests_config['download_dir']
        for dataset in requests_config['datasets']:
            url=dataset['url']
            filename=dataset['filename']
            destination=pl.Path(__file__).parent.parent / folder / filename
            self._download_file(url, destination)

if __name__ == '__main__':
    dataset_obj=DatasetDownloader()
    dataset_obj.fetch_imdb_dataset()

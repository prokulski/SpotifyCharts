# %%
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from os.path import exists

# %%
DATA_DIR = 'data'
CHARTS_DATA_DIR = f'{DATA_DIR}/charts'
TRACKS_DATA_DIR = f'{DATA_DIR}/tracks'
ARTISTS_DATA_DIR = f'{DATA_DIR}/artists'
PARQUET_DATA_DIR = f'{DATA_DIR}/parquets'

# %%
base_url = 'https://spotifycharts.com/regional/global/weekly'

base_page = requests.get(base_url)
soup = BeautifulSoup(base_page.content, 'html.parser')

# %%
# lista krajów
country_list = soup.find('div', attrs={'data-type': 'country'})
country_list = country_list.find_all('li')
country_list = [el['data-value']
                for el in country_list if el['data-value'] != 'global']

# %%


def get_date_list(country):
    # idż na stronę kraju https://spotifycharts.com/regional/{c}/weekly/
    base_page = requests.get(
        f'https://spotifycharts.com/regional/{country}/weekly/')
    soup = BeautifulSoup(base_page.content, 'html.parser')

    # wyciągnij listę dat
    date_list = soup.find('div', attrs={'data-type': 'date'})
    date_list = date_list.find_all('li')
    date_list = [el['data-value'] for el in date_list]
    date_list = sorted(date_list)

    return date_list


# %%
for n, c in enumerate(country_list):
    print(f'Processing {c} ({n} / {len(country_list)})')
    # ze strony kraju wyciągnij listę dat
    date_list = get_date_list(c)

    for d in date_list:
        # budujemy nazwę pliku docelowego
        file_name = f'{CHARTS_DATA_DIR}/{c}_{d}.csv'

        # jeśli plik jeszcze nie istnieje to go ściągamy
        if not exists(file_name):
            file_url = f'https://spotifycharts.com/regional/{c}/weekly/{d}/download'
            file_res = requests.get(file_url)

            print(
                f'\tDownloading data for {c} / {d}: "{file_url}" | {file_res.status_code}')

            if file_res.status_code == 200:
                file_data = file_res.content

                with open(file_name, 'wb') as f:
                    f.write(file_data)

                try:
                    df = pd.read_csv(file_name, sep=',', skiprows=1)
                    df['TrackID'] = df['URL'].apply(lambda s: s.replace(
                        'https://open.spotify.com/track/', ''))
                    df['Country'] = c
                    df['Date'] = d[:10]
                    df.to_csv(file_name, index=False)
                except:
                    print(f'\t\tERROR reading CSV {file_name}')
            else:
                print(f'\t\tERROR! {file_res.status_code}')

            time.sleep(3)

    # pytając o kolejne kraje dajmy chwilę odsapnąć
    time.sleep(2)

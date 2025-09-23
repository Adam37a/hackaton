import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

PAGE_URL = "https://object.infra.data.gouv.fr/browser/ineris-prod/lcsqa/concentrations-de-polluants-atmospheriques-reglementes/temps-reel/2023/"
DOWNLOAD_DIR = "./data/2023"

# URL de base pour télécharger les fichiers CSV
BASE_DOWNLOAD_URL = "https://object.infra.data.gouv.fr/api/v1/buckets/ineris-prod/objects/download?prefix="

CSV_FILES = []
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
current_date = start_date

while current_date <= end_date:
    file_name = f"lcsqa/concentrations-de-polluants-atmospheriques-reglementes/temps-reel/2023/FR_E2_{current_date.strftime('%Y-%m-%d')}.csv"
    CSV_FILES.append(file_name)
    current_date += timedelta(days=1)

def download_file(url, download_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"Fichier téléchargé : {download_path}")
    else:
        print(f"Échec du téléchargement : {url}")

def download_csv_files():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    for csv_file in CSV_FILES:
        full_url = BASE_DOWNLOAD_URL + csv_file
        file_name = os.path.basename(csv_file)
        download_path = os.path.join(DOWNLOAD_DIR, file_name)
        print(f"Téléchargement de {full_url}...")
        download_file(full_url, download_path)

    print("Téléchargement terminé.")

if __name__ == "__main__":
    download_csv_files()

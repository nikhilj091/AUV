import os
import urllib.request

def download_cmapss_from_github():
    # Direct links to raw files from a public github repository hosting the CMAPSS dataset
    base_url = "https://raw.githubusercontent.com/cyrilli/TurboEngine_Dataset_NASA/master/"
    files = ["train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"]
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for filename in files:
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            print(f"Downloading {filename}...")
            url = base_url + filename
            try:
                urllib.request.urlretrieve(url, file_path)
                print(f"Downloaded {filename}")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    download_cmapss_from_github()

from pathlib import Path
import requests
import yaml

def fetch_air_data():
    repo_root = Path(__file__).resolve().parents[1]
    params_path = repo_root / "params.yaml"
    params = {}
    if params_path.exists():
        params = yaml.safe_load(params_path.read_text(encoding="utf-8")) or {}
    url = params.get("fetch", {}).get(
        "url",
        "https://www.arso.gov.si/xml/zrak/ones_zrak_urni_podatki_7dni.xml",
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.content
        file_path = repo_root / "data" / "raw" / "air" / "air_data.xml"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
        
        print("writing data successfull. data saved to: ", file_path)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_air_data()

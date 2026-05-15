from pathlib import Path
import requests

def fetch_air_data():
    try:
        response = requests.get("https://www.arso.gov.si/xml/zrak/ones_zrak_urni_podatki_7dni.xml") 
        response.raise_for_status()

        data = response.content
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / "data" / "raw" / "air" / "air_data.xml"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
        
        print("writing data successfull. data saved to: ", file_path)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_air_data()

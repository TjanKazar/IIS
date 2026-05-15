import numpy as np
import pandas as pd
from lxml import etree as ET
from pathlib import Path
import os

def preprocess_air_data():
    # Open XML file
    base_dir = Path(__file__).resolve().parent
    xml_path = base_dir / "data" / "raw" / "air" / "air_data.xml"
    with open(xml_path, "rb") as file:
        tree = ET.parse(file)
        root = tree.getroot()

    # Extract and print data
    print(f"Version: {root.attrib['verzija']}")
    print(f"Source: {root.find('vir').text}")
    print(f"Suggested Capture: {root.find('predlagan_zajem').text}")
    print(f"Suggested Capture Period: {root.find('predlagan_zajem_perioda').text}")
    print(f"Preparation Date: {root.find('datum_priprave').text}")

    sifra_vals = sorted(set(tree.xpath('//postaja/@sifra')))

    out_dir = base_dir / "data" / "preprocessed" / "air"
    os.makedirs(out_dir, exist_ok=True)
    for sifra in sifra_vals:
        print(f"Processing data for postaja with sifra: {sifra}")

    # Get all station codes and prepare output directory
    sifra_vals = sorted(set(tree.xpath('//postaja/@sifra')))
    out_dir = base_dir / "data" / "preprocessed" / "air"
    os.makedirs(out_dir, exist_ok=True)

    # Initialize column names
    columns = ["date_to", "PM10", "PM2.5"]

    # For each station code, build a DataFrame and write a CSV
    for sifra in sifra_vals:
        postaja_elements = tree.xpath(f'//postaja[@sifra="{sifra}"]')
        
        df = pd.DataFrame(columns=columns)

        for postaja in postaja_elements:
            date_to = postaja.find('datum_do').text
            pm10 = postaja.find('pm10').text if postaja.find('pm10') is not None else np.nan
            pm2_5 = postaja.find('pm2.5').text if postaja.find('pm2.5') is not None else np.nan
            df = pd.concat([df, pd.DataFrame([[date_to, pm10, pm2_5]], columns=columns)], ignore_index=True)

        if df.empty:
            continue

        df = df.sort_values(by="date_to")
        df = df.replace("", np.nan)
        df = df.replace("<1", 1)
        df = df.replace("<2", 2)

        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in sifra)
        out_path = out_dir / f"{safe_name}.csv"

        if out_path.exists():
            try:
                existing = pd.read_csv(out_path)
            except Exception:
                existing = pd.DataFrame(columns=columns)
            combined = pd.concat([existing, df], ignore_index=True)
            # keep the newest values for duplicate `date_to`
            combined = combined.drop_duplicates(subset=["date_to"], keep="last")
            combined = combined.sort_values(by="date_to").reset_index(drop=True)
            combined.to_csv(out_path, index=False)
            print(f"Appended {len(df)} rows to {out_path} (now {len(combined)} rows)")
        else:
            df = df.drop_duplicates(subset=["date_to"], keep="last")
            df = df.sort_values(by="date_to").reset_index(drop=True)
            df.to_csv(out_path, index=False)
            print(f"Created {out_path} with {len(df)} rows")

if __name__ == "__main__":
    preprocess_air_data()
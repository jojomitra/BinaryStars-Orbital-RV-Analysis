# orb6_loader.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Raw GitHub URL to your committed orb6.txt (replace USER/REPO/BRANCH as needed)
GITHUB_RAW_URL = "https://github.com/jojomitra/BinaryStars-Orbital-RV-Analysis/blob/main/orb6.txt"
LOCAL_FILE    = "orb6.txt"

def update_orb6_file():
    """
    Attempt to fetch orb6.txt from your GitHub repo (raw URL) and overwrite local file.
    """
    try:
        resp = requests.get(GITHUB_RAW_URL, timeout=10)
        resp.raise_for_status()
    except Exception:
        return

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        f.write(resp.text)

def fetch_orb6_lines():
    if not os.path.exists(LOCAL_FILE):
        return []
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def parse_orb6_table():
    lines = fetch_orb6_lines()
    if not lines:
        return pd.DataFrame(
            columns=["StarID","P","T","e","a","Omega","omega","i","StarRef"]
        )
    data_lines = [L for L in lines if L and L[0].isdigit()]
    colspecs = [
        (19, 28), (50, 62), (122,133), (142,148),
        (78, 84), (107,112), (157,162), (93, 98), (176,200)
    ]
    names = ["StarID","P","T","e","a","Omega","omega","i","StarRef"]
    df = pd.read_fwf(
        pd.io.common.StringIO("\n".join(data_lines)),
        colspecs=colspecs, names=names
    )
    df["StarID"]  = df["StarID"].str.strip()
    df["StarRef"] = df["StarRef"].str.strip()
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["StarID","P","T","e","a","Omega","omega","i","StarRef"])
    return df.reset_index(drop=True)

if __name__ == "__main__":
    update_orb6_file()
    catalog = parse_orb6_table()
    print(f"Loaded {len(catalog)} orbits.")

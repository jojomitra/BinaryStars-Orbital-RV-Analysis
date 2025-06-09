# orb6_loader.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

ORB6_URL = "https://www.astro.gsu.edu/wds/orb6/orb6frames.html"
LOCAL_FILE = "orb6.txt"


def update_orb6_file():
    """
    Fetch the live ORB6 catalog page, extract its <pre> block,
    and overwrite LOCAL_FILE with that text. If anything goes wrong
    (SSL, network, parsing), leave LOCAL_FILE unchanged.
    """
    try:
        # Suppress InsecureRequestWarning from urllib3
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Fetch without verifying SSL
        resp = requests.get(ORB6_URL, verify=False, timeout=10)
        resp.raise_for_status()
    except Exception:
        # On any error, do not overwrite the local file
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    pre = soup.find("pre")
    if pre is None:
        return

    text = pre.get_text()
    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        f.write(text)


def fetch_orb6_lines():
    """
    Read lines from LOCAL_FILE (orb6.txt). If the file does not exist
    or is empty, return [].
    """
    if not os.path.exists(LOCAL_FILE):
        return []

    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines


def parse_orb6_table():
    """
    Parse the fixed-width lines (from orb6.txt) into a DataFrame
    with columns ['StarID','P','T','e','a','Omega','omega','i','StarRef'].
    If orb6.txt is missing or empty, return an empty DataFrame with
    exactly those columns.
    """
    lines = fetch_orb6_lines()
    if not lines:
        return pd.DataFrame(
            columns=["StarID","P","T","e","a","Omega","omega","i","StarRef"]
        )

    # Keep only lines beginning with a digit (actual data entries)
    data_lines = [L for L in lines if L and L[0].isdigit()]

    # Fixed-width column specs (0-based byte indices)
    colspecs = [
        (19, 28),    # WDS → StarID
        (50, 62),    # P (period, days)
        (122,133),   # T (time of periastron, JD)
        (142,148),   # e (eccentricity)
        (78,  84),   # a (semimajor axis, arcsec)
        (107,112),   # Omega (ascending node, deg)
        (157,162),   # omega (argument of periastron, deg)
        (93,  98),   # i (inclination, deg)
        (176,200)    # StarRef (reference code)
    ]
    names = ["StarID","P","T","e","a","Omega","omega","i","StarRef"]

    df = pd.read_fwf(
        pd.io.common.StringIO("\n".join(data_lines)),
        colspecs=colspecs,
        names=names
    )

    # Strip whitespace
    df["StarID"] = df["StarID"].str.strip()
    df["StarRef"] = df["StarRef"].str.strip()

    # Convert numeric fields
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows missing any required field
    df = df.dropna(subset=["StarID","P","T","e","a","Omega","omega","i","StarRef"])
    return df.reset_index(drop=True)


if __name__ == "__main__":
    # If run standalone, update the local file and print a preview
    update_orb6_file()
    catalog = parse_orb6_table()
    print(f"Loaded {len(catalog)} orbits from orb6.txt")
    print(catalog.head())

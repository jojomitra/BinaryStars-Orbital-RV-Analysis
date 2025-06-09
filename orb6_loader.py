# orb6_loader.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_orb6_lines():
    """
    Download the ORB6 page and return the <pre> block as a list of text lines.
    """
    url = "https://www.astro.gsu.edu/wds/orb6/orb6frames.html"
    resp = requests.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    pre = soup.find("pre")
    if pre is None:
        raise RuntimeError("ORB6 <pre> block not found.")
    text = pre.get_text()
    return text.splitlines()

def parse_orb6_table():
    """
    Parse the fixed-width ORB6 lines into a DataFrame with columns:
      ['StarID','P','T','e','a','Omega','omega','i','StarRef'].

    StarID   (WDS code, bytes 19–28)
    P        (period, days, bytes 50–62)
    T        (time of periastron, JD, bytes 122–133)
    e        (eccentricity, bytes 142–148)
    a        (semimajor axis, arcsec, bytes 78–84)
    Omega    (ascending node Ω, deg, bytes 107–112)
    omega    (argument of periastron ω, deg, bytes 157–162)
    i        (inclination, deg, bytes 93–98)
    StarRef  (REF code, bytes 176–200)
    """
    lines = fetch_orb6_lines()

    # Keep only lines starting with a digit (actual data entries).
    data_lines = [L for L in lines if L and L[0].isdigit()]

    # Define fixed-width column specs (start, end). These are 0‐based indices.
    colspecs = [
        (19, 28),    # WDS designation → StarID
        (50, 62),    # P (period, days)
        (122,133),   # T (time of periastron, JD)
        (142,148),   # e (eccentricity)
        (78, 84),    # a (semimajor axis, arcsec)
        (107,112),   # Omega (ascending node, deg)
        (157,162),   # omega (argument of periastron, deg)
        (93, 98),    # i (inclination, deg)
        (176,200)    # REF code → StarRef
    ]
    names = ["StarID","P","T","e","a","Omega","omega","i","StarRef"]

    # Use pandas.read_fwf on the concatenated lines
    df = pd.read_fwf(
        pd.io.common.StringIO("\n".join(data_lines)),
        colspecs=colspecs,
        names=names
    )

    # Strip whitespace
    df["StarID"] = df["StarID"].str.strip()
    df["StarRef"] = df["StarRef"].str.strip()

    # Convert numeric columns to floats
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where essential data is missing
    df = df.dropna(subset=["StarID","P","T","e","a","Omega","omega","i","StarRef"])
    df = df.reset_index(drop=True)
    return df

if __name__ == "__main__":
    catalog = parse_orb6_table()
    print(f"Read {len(catalog)} orbits from ORB6 (including REF codes).")
    print(catalog.head())

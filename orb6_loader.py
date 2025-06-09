# orb6_loader.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_orb6_lines():
    """
    Download the ORB6 catalog page (skipping SSL verification),
    locate the <pre> block, and return it as a list of lines.
    If anything goes wrong (SSL error, timeout, etc.), return [].
    """
    url = "https://www.astro.gsu.edu/wds/orb6/orb6frames.html"
    try:
        # Suppress only the InsecureRequestWarning
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Perform the GET with SSL verification turned off
        resp = requests.get(url, verify=False, timeout=10)
        resp.raise_for_status()
    except Exception:
        # If request fails (SSL, timeout, etc.), return empty list
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    pre = soup.find("pre")
    if pre is None:
        return []
    raw_text = pre.get_text()
    return raw_text.splitlines()


def parse_orb6_table():
    """
    Parse the fixed-width ORB6 lines into a DataFrame with columns:
    ['StarID','P','T','e','a','Omega','omega','i','StarRef'].
    If fetch_orb6_lines() returned [], we return an empty DataFrame
    with those columns.
    """
    lines = fetch_orb6_lines()
    if not lines:
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(
            columns=["StarID","P","T","e","a","Omega","omega","i","StarRef"]
        )

    # Keep only lines that start with a digit (actual data lines)
    data_lines = [L for L in lines if L and L[0].isdigit()]

    # Fixed‐width column specs (0‐based)
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

    # Convert numerical fields to float
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop any rows missing required data
    df = df.dropna(subset=["StarID","P","T","e","a","Omega","omega","i","StarRef"])
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    catalog = parse_orb6_table()
    print(f"Extracted {len(catalog)} orbits (with REF codes).")
    print(catalog.head())

# orb6_loader.py

import pandas as pd
import os

# 1) Compute the folder where this file (orb6_loader.py) lives:
THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
# 2) Always look for orb6.txt in that same folder:
LOCAL_FILE = os.path.join(THIS_DIR, "orb6.txt")


def fetch_orb6_lines():
    """
    Read the committed 'orb6.txt' from disk (next to this script).
    Return a list of lines (strings), or [] if missing.
    """
    if not os.path.exists(LOCAL_FILE):
        return []
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def parse_orb6_table():
    """
    Parse the fixed-width ORB6 lines into a DataFrame
    with columns ['StarID','P','T','e','a','Omega','omega','i','StarRef'].

    If 'orb6.txt' is missing or empty, return an empty DataFrame
    with those exact columns.
    """
    lines = fetch_orb6_lines()
    if not lines:
        return pd.DataFrame(columns=[
            "StarID", "P", "T", "e", "a", "Omega", "omega", "i", "StarRef"
        ])

    # Keep only lines whose first non-whitespace character is a digit
    data_lines = [L for L in lines if L.lstrip() and L.lstrip()[0].isdigit()]

    # Fixed-width column specs (0-based indices) and names:
    colspecs = [
        (19, 28),    # WDS → StarID
        (50, 62),    # P  (period, days)
        (122,133),   # T  (time of periastron, JD)
        (142,148),   # e  (eccentricity)
        (78,  84),   # a  (semimajor axis, arcsec)
        (107,112),   # Omega  (ascending node, deg)
        (157,162),   # omega  (argument of periastron, deg)
        (93,  98),   # i  (inclination, deg)
        (176,200)    # StarRef  (reference code)
    ]
    names = ["StarID","P","T","e","a","Omega","omega","i","StarRef"]

    df = pd.read_fwf(
        pd.io.common.StringIO("\n".join(data_lines)),
        colspecs=colspecs,
        names=names
    )

    # Strip whitespace from the two string columns
    df["StarID"] = df["StarID"].astype(str).str.strip()
    df["StarRef"] = df["StarRef"].astype(str).str.strip()

    # Remove rows with blank StarRef
    df = df[df["StarRef"].str.len() > 0]
    
    # Convert numeric columns to floats (coerce on parse errors)
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop any rows missing required fields
    df = df.dropna(subset=[
        "StarID","P","T","e","a","Omega","omega","i","StarRef"
    ])
    return df.reset_index(drop=True)


if __name__ == "__main__":
    catalog = parse_orb6_table()
    print(f"Loaded {len(catalog)} orbits from orb6.txt")
    print(catalog.head())

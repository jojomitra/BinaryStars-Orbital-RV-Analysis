# orb6_loader.py

import pandas as pd
import os

THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
LOCAL_FILE = os.path.join(THIS_DIR, "orb6.txt")


def fetch_orb6_lines():
    if not os.path.exists(LOCAL_FILE):
        return []
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def parse_orb6_table():
    """
    Parse only the columns P,T,e,a,Omega,omega,i,StarRef from orb6.txt.
    Returns a DataFrame with exactly those eight columns. If orb6.txt is
    missing or contains no valid data, returns an empty DataFrame with
    those column names.
    """
    lines = fetch_orb6_lines()
    if not lines:
        return pd.DataFrame(columns=["P","T","e","a","Omega","omega","i","StarRef"])

    # Keep only lines whose first non‐whitespace character is a digit
    data_lines = [L for L in lines if L.lstrip() and L.lstrip()[0].isdigit()]

    # Now set up fixed‐width specs _just_ for the eight fields we need:
    #    P    → columns 50–62
    #    T    → columns 122–133
    #    e    → columns 142–148
    #    a    → columns 78–84
    #  Omega → columns 107–112
    #  omega → columns 157–162
    #     i  → columns 93–98
    # StarRef → columns 176–200
    colspecs = [
        (50, 62),    # P
        (122,133),   # T
        (142,148),   # e
        (78,  84),   # a
        (107,112),   # Omega
        (157,162),   # omega
        (93,  98),   # i
        (176,200)    # StarRef
    ]
    names = ["P","T","e","a","Omega","omega","i","StarRef"]

    df = pd.read_fwf(
        pd.io.common.StringIO("\n".join(data_lines)),
        colspecs=colspecs,
        names=names
    )

    # Strip whitespace from StarRef (the only string column)
    df["StarRef"] = df["StarRef"].str.strip()

    # Convert numeric fields to floats (anything unparseable → NaN)
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop any rows missing any of these eight columns
    df = df.dropna(subset=["P","T","e","a","Omega","omega","i","StarRef"])

    return df.reset_index(drop=True)


if __name__ == "__main__":
    catalog = parse_orb6_table()
    print(f"Loaded {len(catalog)} orbits (with only eight columns).")
    print(catalog.head())

# orb6_loader.py

import pandas as pd

def fetch_orb6_lines():
    """
    Read the static ORB6 catalog from local 'orb6.txt'.
    Returns a list of lines (strings), or [] if the file isn't found.
    """
    try:
        with open("orb6.txt", "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        # If the file isn't present, return an empty list
        return []

def parse_orb6_table():
    """
    Parse the fixed-width ORB6 lines (read from orb6.txt) into a DataFrame
    with columns ['StarID','P','T','e','a','Omega','omega','i','StarRef'].
    If orb6.txt was missing or empty, returns an empty DataFrame with those columns.
    """
    lines = fetch_orb6_lines()
    if not lines:
        # Return an empty DataFrame with the correct columns
        return pd.DataFrame(
            columns=["StarID","P","T","e","a","Omega","omega","i","StarRef"]
        )

    # Keep only lines that start with a digit (actual data entries)
    data_lines = [L for L in lines if L and L[0].isdigit()]

    # Fixed‐width column specs (0-based indices):
    colspecs = [
        (19, 28),    # WDS → StarID
        (50, 62),    # P  (period, days)
        (122,133),   # T  (time of periastron, JD)
        (142,148),   # e  (eccentricity)
        (78,  84),   # a  (semimajor axis, arcsec)
        (107,112),   # Omega (ascending node, deg)
        (157,162),   # omega (argument of periastron, deg)
        (93,  98),   # i  (inclination, deg)
        (176,200)    # StarRef (REF code)
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

    # Convert numeric columns to float
    for col in ["P","T","e","a","Omega","omega","i"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop any rows missing required data
    df = df.dropna(subset=["StarID","P","T","e","a","Omega","omega","i","StarRef"])
    return df.reset_index(drop=True)


if __name__ == "__main__":
    catalog = parse_orb6_table()
    print(f"Loaded {len(catalog)} orbits from orb6.txt.")
    print(catalog.head())

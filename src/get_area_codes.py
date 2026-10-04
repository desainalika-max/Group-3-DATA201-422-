# Reads the cleaned listings, looks up the Stats NZ area code of every coordinate with the
# Koordinates API, and saves Christchurch_with_area_codes.csv.
# Needs KOORDINATES_API_KEY in a .env file. Run it from the repo folder.

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from multiprocessing import Pool

load_dotenv()
API_KEY = os.environ["KOORDINATES_API_KEY"]
LAYER_ID = 123515

INPUT_FILE = "Christchurch Oct2025 to Jun2026 (cleaned).csv"
OUTPUT_FILE = "Christchurch_with_area_codes.csv"

N_PROCESSES = 20        # how many API calls run at the same time
TIMEOUT_SECONDS = 15    # give up on one API call after this long
CHECKPOINT_EVERY = 500  # save progress after this many coordinates

def get_area_code(coords):
    lat, lng = coords
    url = "https://koordinates.com/services/query/v1/vector.json"
    params = {"key": API_KEY, "layer": LAYER_ID, "x": lng, "y": lat}
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        data = r.json()
        features = data["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
        if not features:
            return None
        
        return features[0]["properties"]["SA22026_V1_00"]
    except Exception as e:
        print(f"Failed for {lat}, {lng}: {e}")
        return None

if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)

    # Only query unique coordinates, many listings share a building/complex
    unique_coords = df[["latitude", "longitude"]].drop_duplicates()
    coords = list(zip(unique_coords["latitude"], unique_coords["longitude"]))
    print(f"Querying {len(coords)} unique coordinates")

    area_codes = [None] * len(coords)
    start = time.time()

    # area_code must be text, not a number, force it now so nothing
    # crashes later trying to write string values into a numeric column
    df["area_code"] = pd.Series([None] * len(df), dtype="object")

    with Pool(processes=N_PROCESSES) as pool:
        for i, code in enumerate(pool.imap(get_area_code, coords)):
            area_codes[i] = code
            # save progress now and then, so a disconnect never loses everything
            if i % CHECKPOINT_EVERY == 0:
                elapsed = time.time() - start
                print(f"{i}/{len(coords)} done, {elapsed:.0f}s elapsed")
                lookup = dict(zip(coords[:i+1], area_codes[:i+1]))
                df["area_code"] = df.apply(
                    lambda row: lookup.get((row["latitude"], row["longitude"])),
                    axis=1,
                )
                df.to_csv(OUTPUT_FILE, index=False)

    print(f"Done in {time.time() - start:.1f}s")

    lookup = dict(zip(coords, area_codes))
    df["area_code"] = df.apply(
        lambda row: lookup.get((row["latitude"], row["longitude"])), axis=1
    )
    df.to_csv(OUTPUT_FILE, index=False)

    missing = df["area_code"].isna().sum()
    print(f"Missing area codes: {missing} out of {len(df)}")
    print(df[["latitude", "longitude", "area_code"]].head())

    # the file is already saved, but a listing without an area code must not pass silently
    if missing > 0:
        raise ValueError(f"{missing} listings have no area code. Check the 'Failed for' "
                         f"messages above and run the script again.")
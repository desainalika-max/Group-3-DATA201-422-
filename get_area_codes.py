# Looks up the Stats NZ SA2 area code of every listing coordinate with the Koordinates API,
# and writes the cleaned listings plus an area_code column. Needs KOORDINATES_API_KEY in .env.
# Run from the repo folder: python get_area_codes.py

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

N_PROCESSES = 20        # API calls made at the same time
TIMEOUT_SECONDS = 15    # give up on one API call after this long
CHECKPOINT_EVERY = 500  # save progress after this many coordinates

# Sanity check: a known Redcliffs listing ("Relaxing Redcliffs") must come back as
# area 332100, Redcliffs. A swapped latitude/longitude would give a wrong area.
CHECK_LAT = -43.55816
CHECK_LNG = 172.73536
CHECK_AREA_CODE = "332100"

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
    # stop before thousands of API calls if the known Redcliffs point comes back wrong
    check_code = get_area_code((CHECK_LAT, CHECK_LNG))
    if str(check_code) != CHECK_AREA_CODE:
        raise ValueError(f"Sanity check failed: Redcliffs gave {check_code}, "
                         f"expected {CHECK_AREA_CODE}. Check the API key, LAYER_ID "
                         f"and the order of x (longitude) and y (latitude).")
    print("Sanity check passed: Redcliffs is", check_code)

    # ids are labels, so read them as text
    df = pd.read_csv(INPUT_FILE, dtype={"id": str, "host_id": str})

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

    # the file is saved above so the API calls are not lost, but a failed lookup
    # must not pass silently
    if missing > 0:
        raise ValueError(f"{missing} listings have no area code. See the 'Failed for' "
                         f"messages above, fix the cause, and run again.")
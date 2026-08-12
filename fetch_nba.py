import time

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

SEASONS = [f"{y}-{str(y + 1)[2:]}" for y in range(1996, 2025)]


def fetch_season(season, measure_type):
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star="Regular Season",
        per_mode_detailed="Totals",
        measure_type_detailed_defense=measure_type,
    )
    df = stats.get_data_frames()[0]
    df["SEASON"] = season
    return df


def main():
    base_frames = []
    advanced_frames = []

    for season in SEASONS:
        print(f"Fetching {season}...")
        base_frames.append(fetch_season(season, "Base"))
        time.sleep(0.6)
        advanced_frames.append(fetch_season(season, "Advanced"))
        time.sleep(0.6)

    base_df = pd.concat(base_frames, ignore_index=True)
    advanced_df = pd.concat(advanced_frames, ignore_index=True)

    print("Base shape:", base_df.shape)
    print("Advanced shape:", advanced_df.shape)

    base_df.to_csv("data/nba_base_raw.csv", index=False)
    advanced_df.to_csv("data/nba_advanced_raw.csv", index=False)
    print("Saved data/nba_base_raw.csv and data/nba_advanced_raw.csv")


if __name__ == "__main__":
    main()

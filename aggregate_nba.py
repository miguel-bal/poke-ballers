import pandas as pd

BASE_COLS = ["PLAYER_ID", "PLAYER_NAME", "SEASON", "TEAM_ID", "GP", "MIN", "PTS", "STL", "BLK"]
ADVANCED_COLS = ["PLAYER_ID", "SEASON", "TEAM_ID", "AST_PCT", "DREB_PCT", "DEF_RATING", "PACE"]
MIN_CAREER_MINUTES = 1000

DECADE_LABELS = {
    1990: "Hand-Check Grind",
    2000: "Isolation Half-Court",
    2010: "Pace-and-Space Small-Ball",
    2020: "Positionless Spacing",
}


def season_decade(season):
    start_year = int(season[:4])
    return (start_year // 10) * 10


def main():
    base = pd.read_csv("data/nba_base_raw.csv", usecols=BASE_COLS)
    advanced = pd.read_csv("data/nba_advanced_raw.csv", usecols=ADVANCED_COLS)

    base = base.rename(columns={"MIN": "MIN_TOTAL"})
    merged = base.merge(advanced, on=["PLAYER_ID", "SEASON", "TEAM_ID"], how="inner")

    # Collapse multi-team stints (trades) into one row per player-season,
    # weighting rate stats by minutes played on each team.
    weight = merged["MIN_TOTAL"]
    for col in ["AST_PCT", "DREB_PCT", "DEF_RATING", "PACE"]:
        merged[f"{col}_W"] = merged[col] * weight

    season_rows = merged.groupby(["PLAYER_ID", "PLAYER_NAME", "SEASON"]).agg(
        GP=("GP", "sum"),
        MIN_TOTAL=("MIN_TOTAL", "sum"),
        PTS=("PTS", "sum"),
        STL=("STL", "sum"),
        AST_PCT_W=("AST_PCT_W", "sum"),
        DREB_PCT_W=("DREB_PCT_W", "sum"),
        DEF_RATING_W=("DEF_RATING_W", "sum"),
        PACE_W=("PACE_W", "sum"),
    ).reset_index()
    season_rows = season_rows[season_rows["MIN_TOTAL"] > 0].copy()

    season_rows["MIN_PER_GAME"] = season_rows["MIN_TOTAL"] / season_rows["GP"]
    season_rows["PTS_PER_36"] = season_rows["PTS"] / season_rows["MIN_TOTAL"] * 36
    season_rows["STL_PER_36"] = season_rows["STL"] / season_rows["MIN_TOTAL"] * 36
    season_rows["AST_PCT"] = season_rows["AST_PCT_W"] / season_rows["MIN_TOTAL"]
    season_rows["DREB_PCT"] = season_rows["DREB_PCT_W"] / season_rows["MIN_TOTAL"]
    season_rows["DEF_RATING"] = season_rows["DEF_RATING_W"] / season_rows["MIN_TOTAL"]
    season_rows["PACE"] = season_rows["PACE_W"] / season_rows["MIN_TOTAL"]

    season_rows["DECADE"] = season_rows["SEASON"].apply(season_decade)

    # Percentile-rank each stat within its own decade cohort. DEF_RATING is
    # inverted (ascending=False) since lower raw values mean better defense.
    grp = season_rows.groupby("DECADE")
    season_rows["HP_PCT"] = grp["MIN_PER_GAME"].rank(pct=True) * 100
    season_rows["ATTACK_PCT"] = grp["PTS_PER_36"].rank(pct=True) * 100
    season_rows["DEFENSE_PCT"] = grp["DEF_RATING"].rank(pct=True, ascending=False) * 100
    season_rows["SPATK_PCT"] = grp["AST_PCT"].rank(pct=True) * 100
    season_rows["DREB_PCT_RANK"] = grp["DREB_PCT"].rank(pct=True) * 100
    season_rows["STL_PCT_RANK"] = grp["STL_PER_36"].rank(pct=True) * 100
    season_rows["SPEED_PCT"] = grp["PACE"].rank(pct=True) * 100
    season_rows["SPDEF_PCT"] = (season_rows["DREB_PCT_RANK"] + season_rows["STL_PCT_RANK"]) / 2

    # Aggregate percentiles to career level, weighted by minutes played that season.
    pct_cols = ["HP_PCT", "ATTACK_PCT", "DEFENSE_PCT", "SPATK_PCT", "SPDEF_PCT", "SPEED_PCT"]
    for col in pct_cols:
        season_rows[f"{col}_W"] = season_rows[col] * season_rows["MIN_TOTAL"]

    career = season_rows.groupby(["PLAYER_ID", "PLAYER_NAME"]).agg(
        GP=("GP", "sum"),
        MIN_TOTAL=("MIN_TOTAL", "sum"),
        **{f"{col}_W": (f"{col}_W", "sum") for col in pct_cols},
    ).reset_index()
    for col in pct_cols:
        career[col] = career[f"{col}_W"] / career["MIN_TOTAL"]

    # Primary decade = whichever decade a player logged the most minutes in.
    decade_minutes = season_rows.groupby(["PLAYER_ID", "DECADE"])["MIN_TOTAL"].sum().reset_index()
    primary_decade = decade_minutes.loc[decade_minutes.groupby("PLAYER_ID")["MIN_TOTAL"].idxmax()]
    primary_decade = primary_decade[["PLAYER_ID", "DECADE"]].rename(columns={"DECADE": "PRIMARY_DECADE"})
    career = career.merge(primary_decade, on="PLAYER_ID", how="left")
    career["ERA_LABEL"] = career["PRIMARY_DECADE"].map(DECADE_LABELS)

    result = career[["PLAYER_ID", "PLAYER_NAME", "GP", "MIN_TOTAL", "PRIMARY_DECADE", "ERA_LABEL"] + pct_cols]

    print("Career rows before cutoff:", result.shape)
    filtered = result[result["MIN_TOTAL"] >= MIN_CAREER_MINUTES].reset_index(drop=True)
    print(f"Dropped {len(result) - len(filtered)} players below {MIN_CAREER_MINUTES} career minutes")
    print("Career rows after cutoff:", filtered.shape)
    print()
    print(filtered.groupby("ERA_LABEL")["PLAYER_ID"].count())
    print()
    print(filtered.sort_values("ATTACK_PCT", ascending=False)[
        ["PLAYER_NAME", "PRIMARY_DECADE", "ERA_LABEL", "ATTACK_PCT"]
    ].head(5).to_string())

    filtered.to_csv("data/nba_career_stats.csv", index=False)
    print("\nSaved data/nba_career_stats.csv")


if __name__ == "__main__":
    main()

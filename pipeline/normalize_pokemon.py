import pandas as pd

STAT_TO_PCT_COL = {
    "HP": "HP_PCT",
    "Attack": "ATTACK_PCT",
    "Defense": "DEFENSE_PCT",
    "Sp. Atk": "SPATK_PCT",
    "Sp. Def": "SPDEF_PCT",
    "Speed": "SPEED_PCT",
}


def main():
    df = pd.read_csv("data/pokemon_processed.csv")

    for stat, pct_col in STAT_TO_PCT_COL.items():
        df[pct_col] = df[stat].rank(pct=True) * 100

    print("Rows:", df.shape)
    print()
    print(df[list(STAT_TO_PCT_COL.values())].describe())
    print()
    print(df.sort_values("ATTACK_PCT", ascending=False)[
        ["DisplayName", "Attack", "ATTACK_PCT"]
    ].head(5).to_string())

    df.to_csv("data/pokemon_normalized.csv", index=False)
    print("\nSaved data/pokemon_normalized.csv")


if __name__ == "__main__":
    main()

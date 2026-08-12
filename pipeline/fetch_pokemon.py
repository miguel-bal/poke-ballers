import pandas as pd

URL = "https://raw.githubusercontent.com/lgreski/pokemonData/master/Pokemon.csv"


def main():
    df = pd.read_csv(URL)

    # Strip leading/trailing whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df["Form"] = df["Form"].fillna("")
    df["DisplayName"] = df.apply(
        lambda row: row["Name"] if row["Form"] == "" else f"{row['Name']} ({row['Form']})",
        axis=1,
    )

    print("Shape:", df.shape)
    print("Unique Name values:", df["Name"].nunique())
    print()
    print("Sample DisplayName values for forms:")
    print(df.loc[df["Form"] != "", ["Name", "Form", "DisplayName"]].head(10).to_string())

    df.to_csv("data/pokemon_processed.csv", index=False)
    print("\nSaved data/pokemon_processed.csv")


if __name__ == "__main__":
    main()

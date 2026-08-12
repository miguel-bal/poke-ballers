from nba_api.stats.endpoints import leaguedashplayerstats

stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season="2022-23",
    measure_type_detailed_defense="Advanced",
)
df = stats.get_data_frames()[0]

print("Shape:", df.shape)
print("Columns:", list(df.columns))
print()
print(df.head(5).to_string())

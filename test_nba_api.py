from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# LeBron James, a known player, as a smoke test
lebron = players.find_players_by_full_name("LeBron James")[0]
print("Found player:", lebron)

career = playercareerstats.PlayerCareerStats(player_id=lebron["id"])
df = career.get_data_frames()[0]

print()
print("Shape:", df.shape)
print("Columns:", list(df.columns))
print()
print(df.head(10).to_string())

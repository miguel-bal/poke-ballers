import numpy as np
import pandas as pd

STAT_COLS = ["HP_PCT", "ATTACK_PCT", "DEFENSE_PCT", "SPATK_PCT", "SPDEF_PCT", "SPEED_PCT"]

SAMPLE_PLAYERS = [
    "LeBron James", "Michael Jordan", "Kobe Bryant", "Zion Williamson",
    "Dennis Rodman", "Chris Paul", "Rudy Gobert",
]


def main():
    players = pd.read_csv("data/nba_career_stats.csv")
    pokemon = pd.read_csv("data/pokemon_normalized.csv")

    player_vecs = players[STAT_COLS].to_numpy()
    pokemon_vecs = pokemon[STAT_COLS].to_numpy()

    # Euclidean: smaller distance = more similar.
    diffs = player_vecs[:, None, :] - pokemon_vecs[None, :, :]
    euclidean_dist = np.sqrt((diffs ** 2).sum(axis=2))
    euclidean_idx = euclidean_dist.argmin(axis=1)

    # Cosine similarity: larger = more similar (direction, not magnitude).
    player_norms = np.linalg.norm(player_vecs, axis=1, keepdims=True)
    pokemon_norms = np.linalg.norm(pokemon_vecs, axis=1, keepdims=True)
    cosine_sim = (player_vecs @ pokemon_vecs.T) / (player_norms @ pokemon_norms.T)
    cosine_idx = cosine_sim.argmax(axis=1)

    players["EUCLIDEAN_MATCH"] = pokemon["DisplayName"].to_numpy()[euclidean_idx]
    players["EUCLIDEAN_DIST"] = euclidean_dist[np.arange(len(players)), euclidean_idx]
    players["COSINE_MATCH"] = pokemon["DisplayName"].to_numpy()[cosine_idx]
    players["COSINE_SIM"] = cosine_sim[np.arange(len(players)), cosine_idx]

    result = players[["PLAYER_NAME"] + STAT_COLS + [
        "EUCLIDEAN_MATCH", "EUCLIDEAN_DIST", "COSINE_MATCH", "COSINE_SIM"
    ]]
    result.to_csv("data/matches.csv", index=False)
    print("Saved data/matches.csv")
    print()

    sample = result[result["PLAYER_NAME"].isin(SAMPLE_PLAYERS)]
    print(sample[["PLAYER_NAME", "EUCLIDEAN_MATCH", "EUCLIDEAN_DIST", "COSINE_MATCH", "COSINE_SIM"]].to_string())

    agree_rate = (result["EUCLIDEAN_MATCH"] == result["COSINE_MATCH"]).mean()
    print(f"\nEuclidean and cosine agree on {agree_rate:.1%} of players")

    # Reverse direction: nearest player for each Pokemon. Not the inverse of
    # the above, since nearest-neighbor isn't symmetric - reuses the same
    # distance/similarity matrices, just argmin/argmax along the other axis.
    reverse_euclidean_idx = euclidean_dist.argmin(axis=0)
    reverse_cosine_idx = cosine_sim.argmax(axis=0)

    pokemon["EUCLIDEAN_MATCH"] = players["PLAYER_NAME"].to_numpy()[reverse_euclidean_idx]
    pokemon["EUCLIDEAN_DIST"] = euclidean_dist[reverse_euclidean_idx, np.arange(len(pokemon))]
    pokemon["COSINE_MATCH"] = players["PLAYER_NAME"].to_numpy()[reverse_cosine_idx]
    pokemon["COSINE_SIM"] = cosine_sim[reverse_cosine_idx, np.arange(len(pokemon))]

    pokemon_result = pokemon[["DisplayName"] + STAT_COLS + [
        "EUCLIDEAN_MATCH", "EUCLIDEAN_DIST", "COSINE_MATCH", "COSINE_SIM"
    ]]
    pokemon_result.to_csv("data/pokemon_matches.csv", index=False)
    print("\nSaved data/pokemon_matches.csv")

    sample_pokemon = pokemon_result[pokemon_result["EUCLIDEAN_MATCH"].isin(SAMPLE_PLAYERS)
                                     | pokemon_result["COSINE_MATCH"].isin(SAMPLE_PLAYERS)]
    print(sample_pokemon[["DisplayName", "EUCLIDEAN_MATCH", "EUCLIDEAN_DIST", "COSINE_MATCH", "COSINE_SIM"]].head(10).to_string())


if __name__ == "__main__":
    main()

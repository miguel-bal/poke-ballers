# poke-ballers

Matches each NBA player to the Pokémon whose base stats are most
statistically similar to theirs. NBA career stats are normalized into the
same six-axis shape as Pokémon base stats (HP, Attack, Defense, Sp. Atk,
Sp. Def, Speed), then compared via nearest-neighbor similarity.

## Design decisions

- **Granularity:** career averages, one row per player — not single-season
  stats.
- **Alt forms:** Mega Evolutions, regional forms, and alternate formes
  (e.g. Aegislash Blade/Shield) are separate match candidates, not
  collapsed into their base species.
- **Stat mapping:** direct/objective mapping from NBA stats to Pokémon
  stats, not hand-curated archetype labeling.
- **Power level:** left natural — superstars can match legendary-tier
  Pokémon, bench players can match low-stat-total commons.
- **Similarity algorithm:** both Euclidean distance and cosine similarity
  on the normalized 6D stat vectors, shown side by side rather than
  picking one as authoritative. In practice they surface different
  qualities of a match — Euclidean favors overall closeness across all
  axes, cosine favors matching "shape"/proportions even if every stat
  runs a bit high or low — and cosine similarity scores are compressed
  into a narrow band (~0.96–0.9999) since all stat vectors are
  non-negative, so its numbers shouldn't be read as confidence
  percentages.
- **NBA normalization:** each stat is converted to a percentile rank
  within the player's own era/peers (not all-time), since raw pace/stats
  differ too much across eras for all-time percentiles to be fair. Era is
  bucketed by decade, computed per player-season (not per career) so
  players whose careers span multiple decades are credited correctly for
  each season played, then aggregated into a minutes-weighted career
  percentile. Each player is also tagged with a "primary" decade/era
  label (whichever decade they logged the most minutes in), purely as
  descriptive metadata.
- **Small-sample handling:** players with under 1,000 career minutes are
  dropped from the matching pool — below that, per-36/percentage rate
  stats get noisy (e.g. a player with under a minute played can register
  an absurd points-per-36 rate).
- **NBA data source:** `nba_api` (live pull from stats.nba.com), covering
  the 1996-97 season onward — advanced tracking stats (usage%, def
  rating, pace, etc.) aren't reliably available before that.

## Stat mapping

| Pokémon stat | NBA stat | Source |
|---|---|---|
| HP | Minutes per game | Base |
| Attack | Points per 36 minutes | Base |
| Defense | Defensive Rating (inverted — lower is better) | Advanced (`DEF_RATING`) |
| Sp. Atk | Assist percentage | Advanced (`AST_PCT`) |
| Sp. Def | Defensive rebound % + steal rate | Advanced (`DREB_PCT`) + Base (`STL`) |
| Speed | Pace | Advanced (`PACE`) |

## File layout

```
pipeline/   data fetch + processing + matching scripts (run from repo root)
scratch/    exploration/smoke-test scripts, not part of the pipeline
data/       raw and processed CSVs (gitignored outputs land here)
```

All commands below are run from the repo root, since scripts read/write
paths like `data/...` relative to the current working directory.

## Data pipeline

### Pokémon

`pipeline/fetch_pokemon.py` downloads the static CSV from
[`lgreski/pokemonData`](https://github.com/lgreski/pokemonData), builds a
`DisplayName` column (e.g. `Charizard (Mega Charizard X)`), and saves
`data/pokemon_processed.csv` (1,215 rows / 1,026 unique species).

```
python pipeline/fetch_pokemon.py
```

### NBA

`pipeline/fetch_nba.py` pulls per-player, per-season Base and Advanced
stats via `nba_api` for every season from 1996-97 onward, and saves the
raw pulls to `data/nba_base_raw.csv` and `data/nba_advanced_raw.csv`.
These are not yet aggregated to career-level rows.

```
python pipeline/fetch_nba.py
```

Note: `nba_api`'s Advanced endpoint reports `MIN` as a per-game average
regardless of requested per-mode, while the Base endpoint's `MIN` is a
season total — when weighting seasons by playing time, use Base's `MIN`
(or `GP`), not Advanced's.

`scratch/test_nba_api.py` and `scratch/test_nba_api_advanced.py` are
smoke-test scripts used to confirm connectivity and inspect available
columns; not part of the pipeline.

`pipeline/aggregate_nba.py` merges the raw Base + Advanced pulls per
player-season (collapsing multi-team trade stints), percentile-ranks each
stat within its decade cohort, then aggregates to one minutes-weighted
career row per player, dropping anyone under 1,000 career minutes. Saves
`data/nba_career_stats.csv`.

```
python pipeline/aggregate_nba.py
```

`pipeline/normalize_pokemon.py` percentile-ranks each of the six Pokémon
base stats across the full roster (1,215 rows, no era concept needed),
saving `data/pokemon_normalized.csv` on the same 0–100 scale as the NBA
output.

```
python pipeline/normalize_pokemon.py
```

`pipeline/match.py` computes Euclidean distance and cosine similarity
between every player's 6D vector and every Pokémon's, saving both nearest
matches side by side to `data/matches.csv`.

```
python pipeline/match.py
```

## Status

- [x] Pokémon data pipeline
- [x] NBA data source selected and raw per-season pull working
- [x] Aggregate NBA per-season stats into career-average rows (minutes-weighted)
- [x] Percentile-normalize NBA stats within era (bucketed by decade)
- [x] Normalize Pokémon stats to the same 6D scale
- [x] Nearest-neighbor matching (Euclidean + cosine, shown side by side)
- [ ] Output format (Python GUI)
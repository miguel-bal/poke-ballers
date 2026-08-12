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
  on the normalized 6D stat vectors, for comparison.
- **NBA normalization:** each stat is converted to a percentile rank
  within the player's own era/peers (not all-time), since raw pace/stats
  differ too much across eras for all-time percentiles to be fair.
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

## Data pipeline

### Pokémon

`fetch_pokemon.py` downloads the static CSV from
[`lgreski/pokemonData`](https://github.com/lgreski/pokemonData), builds a
`DisplayName` column (e.g. `Charizard (Mega Charizard X)`), and saves
`data/pokemon_processed.csv` (1,215 rows / 1,026 unique species).

```
python fetch_pokemon.py
```

### NBA

`fetch_nba.py` pulls per-player, per-season Base and Advanced stats via
`nba_api` for every season from 1996-97 onward, and saves the raw pulls to
`data/nba_base_raw.csv` and `data/nba_advanced_raw.csv`. These are not yet
aggregated to career-level rows.

```
python fetch_nba.py
```

Note: `nba_api`'s Advanced endpoint reports `MIN` as a per-game average
regardless of requested per-mode, while the Base endpoint's `MIN` is a
season total — when weighting seasons by playing time, use Base's `MIN`
(or `GP`), not Advanced's.

`test_nba_api.py` and `test_nba_api_advanced.py` are smoke-test scripts
used to confirm connectivity and inspect available columns; not part of
the pipeline.

## Status

- [x] Pokémon data pipeline
- [x] NBA data source selected and raw per-season pull working
- [ ] Aggregate NBA per-season stats into career-average rows (minutes-weighted)
- [ ] Percentile-normalize NBA stats within era
- [ ] Normalize Pokémon stats to the same 6D scale
- [ ] Nearest-neighbor matching (Euclidean + cosine)
- [ ] Output format (Python GUI)
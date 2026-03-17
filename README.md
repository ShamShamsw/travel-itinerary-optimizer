# Beginner Project 46: Travel Itinerary Optimizer

**Time:** 4-6 hours  
**Difficulty:** Intermediate Beginner  
**Focus:** Constraint-aware route optimization, strategy benchmarking, persistent planning history, and runtime/value visualizations

---

## Why This Project?

Travel-planning apps look simple at first, but real itinerary decisions always involve trade-offs: time caps, budget caps, travel overhead, and stop priorities. This project turns that into a reproducible optimization workflow where you can compare planning strategies, inspect trace bundles, and track planning quality over repeated runs.

This project teaches end-to-end itinerary optimization workflow concepts where you can:

- load or auto-seed a reusable destination library for deterministic demos,
- run itinerary optimization under time and budget constraints,
- compare greedy and brute-force planning strategies side by side,
- score routes using priority value with travel and cost penalties,
- persist itinerary plans and stop-level history for auditability,
- benchmark strategy runtime across growing destination counts,
- visualize runtime behavior as a multi-series chart,
- visualize per-stop value contribution across planned sequence,
- export trace bundles and benchmark bundles to JSON for inspection,
- persist historical run summaries for repeatable analysis,
- and print a readable terminal report with itinerary previews and artifact paths.

---

## More Projects

You can access this project and more in this separate repository:

[student-interview-prep](https://github.com/ShamShamsw/student-interview-prep.git)

---

## What You Will Build

You will build a travel itinerary optimizer workflow that:

1. Loads destination cases from `data/itinerary_sets.json` (or seeds a starter set of 8 destinations).
2. Selects a deterministic demo sequence for planning walkthroughs.
3. Optimizes stop order under configurable time and budget constraints.
4. Runs both greedy and brute-force search to compare strategy quality.
5. Stores itinerary and stop events in `data/itinerary_history.json`.
6. Benchmarks planner runtime across configured destination counts and repeated trials.
7. Aggregates runtime points into strategy-level average performance summaries.
8. Saves a strategy runtime chart under `data/outputs/`.
9. Saves a stop value-trend chart under `data/outputs/`.
10. Persists trace, benchmark, and run-summary artifacts for future sessions.
11. Maintains a run catalog in `data/runs.json` for startup profiling.

---

## Requirements

- Python 3.11+
- `matplotlib`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## Example Session

```text
======================================================================
   TRAVEL ITINERARY OPTIMIZER
======================================================================

Configuration:
   Project type:           travel_itinerary_optimizer
   Strategy selected:      brute_force
   Strategy set:           greedy, brute_force
   Demo sequence:          weekend_city_mix
   Trip time cap:          520 minutes
   Budget cap:             $180.00
   Benchmark stop counts:  4, 5, 6, 7, 8
   Trials per stop count:  4
   Runtime chart:          True
   Value chart:            True
   Max preview rows:       8
   Random seed:            42

Startup:
   Data directory:         data/
   Outputs directory:      data/outputs/
   Destination library:    data/itinerary_sets.json (loaded 0 destinations)
   Run catalog:            data/runs.json (loaded 0 runs)
   Itinerary history:      data/itinerary_history.json (loaded 0 entries)
   Recent runs:            None yet

---

Session complete:
   Session ID:             20260317_230410
   Destinations available: 8
   Demo sequence:          weekend_city_mix
   Strategy selected:      brute_force
   Routes evaluated:       2
   Stops planned:          5
   Runtime points:         40
   Elapsed time:           421.73 ms

Planner metrics: best_strategy=greedy | best_avg_runtime_ms=0.153440 | selected_total_score=334.786500 | history_size=6

Selected plan totals: minutes=497.21 | cost_usd=108.00

Itinerary previews:
   Stop | Destination                    | Travel | Visit | Cost    | Score
   -----+--------------------------------+--------+-------+---------+----------
   1    | Science Center                 | 50.47  | 95    | $22.00  | 57.191
   2    | City Observation Deck          | 13.26  | 60    | $30.00  | 64.682
   3    | Art District                   | 15.38  | 65    | $12.00  | 70.003

Artifacts saved:
   Session record:         data/outputs/run_20260317_230410.json
   Trace bundle:           data/outputs/trace_20260317_230410.json
   Benchmark file:         data/outputs/benchmark_20260317_230410.json
   Runtime chart:          data/outputs/strategy_runtime_20260317_230410.png
   Value chart:            data/outputs/stop_value_trend_20260317_230410.png
```

---

## Run

```bash
python main.py
```

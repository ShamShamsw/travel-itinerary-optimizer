"""Business logic for Project 46: Travel Itinerary Optimizer."""

from __future__ import annotations

import math
import random
import time
from collections import defaultdict
from datetime import datetime
from itertools import permutations
from statistics import mean
from typing import Any, Dict, List, Tuple

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt

from models import (
    create_destination_case,
    create_history_entry,
    create_plan_result,
    create_planner_config,
    create_runtime_point,
    create_session_summary,
    create_stop_result,
)
from storage import (
    OUTPUTS_DIR,
    ensure_data_dirs,
    load_destination_library,
    load_history,
    load_run_catalog,
    save_benchmark_file,
    save_destination_library,
    save_history,
    save_run_record,
    save_trace_file,
)


PLOT_COLORS = {
    'greedy': '#264653',
    'brute_force': '#2a9d8f',
    'selected_plan': '#e76f51',
}


def _session_id() -> str:
    """Build a compact session ID from UTC timestamp."""
    return datetime.utcnow().strftime('%Y%m%d_%H%M%S')


def _default_destination_library() -> List[Dict[str, Any]]:
    """Return deterministic starter destination cases used on first run."""
    return [
        create_destination_case(
            destination_id='dest_001',
            label='weekend_city_mix',
            name='Historic Museum',
            x=1.2,
            y=3.4,
            visit_minutes=85,
            cost_usd=18.0,
            priority=8.4,
            description='Core culture stop with high educational value.',
            tags=['culture', 'indoors'],
        ),
        create_destination_case(
            destination_id='dest_002',
            label='weekend_city_mix',
            name='River Walk',
            x=4.6,
            y=2.3,
            visit_minutes=50,
            cost_usd=0.0,
            priority=7.2,
            description='Scenic walking route with flexible timing.',
            tags=['outdoors', 'photo'],
        ),
        create_destination_case(
            destination_id='dest_003',
            label='weekend_city_mix',
            name='Street Food Market',
            x=2.8,
            y=5.1,
            visit_minutes=70,
            cost_usd=24.0,
            priority=8.8,
            description='High reward food cluster with moderate cost.',
            tags=['food', 'social'],
        ),
        create_destination_case(
            destination_id='dest_004',
            label='weekend_city_mix',
            name='City Observation Deck',
            x=6.4,
            y=4.3,
            visit_minutes=60,
            cost_usd=30.0,
            priority=7.6,
            description='Panoramic skyline experience.',
            tags=['views', 'landmark'],
        ),
        create_destination_case(
            destination_id='dest_005',
            label='weekend_city_mix',
            name='Botanical Garden',
            x=5.2,
            y=7.0,
            visit_minutes=75,
            cost_usd=16.0,
            priority=7.9,
            description='Low-noise nature visit with broad paths.',
            tags=['nature', 'relax'],
        ),
        create_destination_case(
            destination_id='dest_006',
            label='weekend_city_mix',
            name='Science Center',
            x=8.0,
            y=2.6,
            visit_minutes=95,
            cost_usd=22.0,
            priority=9.1,
            description='Hands-on exhibits and interactive galleries.',
            tags=['education', 'indoors'],
        ),
        create_destination_case(
            destination_id='dest_007',
            label='weekend_city_mix',
            name='Art District',
            x=7.1,
            y=6.8,
            visit_minutes=65,
            cost_usd=12.0,
            priority=8.1,
            description='Murals, small galleries, and local shops.',
            tags=['art', 'walking'],
        ),
        create_destination_case(
            destination_id='dest_008',
            label='weekend_city_mix',
            name='Night Jazz Club',
            x=9.2,
            y=5.5,
            visit_minutes=80,
            cost_usd=28.0,
            priority=8.5,
            description='Late-evening music venue with ticketed entry.',
            tags=['music', 'nightlife'],
        ),
    ]


def _distance(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """Return Euclidean distance between two map points."""
    return math.hypot(float(a['x']) - float(b['x']), float(a['y']) - float(b['y']))


def _travel_minutes(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """Translate map distance to transit minutes."""
    return _distance(a, b) * 6.0


def _evaluate_route(
    route: Tuple[Dict[str, Any], ...],
    max_minutes: int,
    max_budget_usd: float,
) -> Dict[str, Any]:
    """Evaluate one candidate route against constraints and score."""
    current = {'x': 0.0, 'y': 0.0}
    total_minutes = 0.0
    total_cost = 0.0
    total_score = 0.0
    stops: List[Dict[str, Any]] = []

    for index, destination in enumerate(route, start=1):
        transit = _travel_minutes(current, destination)
        projected_minutes = total_minutes + transit + float(destination['visit_minutes'])
        projected_cost = total_cost + float(destination['cost_usd'])
        if projected_minutes > float(max_minutes) or projected_cost > float(max_budget_usd):
            break

        # Weight destination priority, then penalize travel overhead.
        score_gain = (float(destination['priority']) * 10.0) - (transit * 0.65) - float(destination['cost_usd']) * 0.25
        total_minutes = projected_minutes
        total_cost = projected_cost
        total_score += score_gain
        stops.append(
            create_stop_result(
                stop_index=index,
                name=str(destination['name']),
                travel_minutes=transit,
                visit_minutes=int(destination['visit_minutes']),
                cost_usd=float(destination['cost_usd']),
                score_gain=score_gain,
                cumulative_minutes=total_minutes,
                cumulative_cost_usd=total_cost,
            )
        )
        current = destination

    feasible = bool(stops)
    return create_plan_result(
        strategy='route_eval',
        total_score=total_score,
        total_minutes=total_minutes,
        total_cost_usd=total_cost,
        stops=stops,
        feasible=feasible,
    )


def optimize_itinerary_greedy(
    destinations: List[Dict[str, Any]],
    max_minutes: int,
    max_budget_usd: float,
) -> Dict[str, Any]:
    """Build itinerary with greedy incremental selection."""
    remaining = list(destinations)
    current = {'x': 0.0, 'y': 0.0}
    route: List[Dict[str, Any]] = []
    minutes_used = 0.0
    budget_used = 0.0

    while remaining:
        best_index = -1
        best_ratio = -1.0
        for index, destination in enumerate(remaining):
            transit = _travel_minutes(current, destination)
            projected_minutes = minutes_used + transit + float(destination['visit_minutes'])
            projected_budget = budget_used + float(destination['cost_usd'])
            if projected_minutes > float(max_minutes) or projected_budget > float(max_budget_usd):
                continue
            utility = (float(destination['priority']) * 10.0) - transit * 0.65 - float(destination['cost_usd']) * 0.25
            denominator = max(1.0, float(destination['visit_minutes']) + transit)
            ratio = utility / denominator
            if ratio > best_ratio:
                best_ratio = ratio
                best_index = index

        if best_index < 0:
            break

        choice = remaining.pop(best_index)
        transit = _travel_minutes(current, choice)
        minutes_used += transit + float(choice['visit_minutes'])
        budget_used += float(choice['cost_usd'])
        route.append(choice)
        current = choice

    evaluated = _evaluate_route(tuple(route), max_minutes, max_budget_usd)
    evaluated['strategy'] = 'greedy'
    return evaluated


def optimize_itinerary_bruteforce(
    destinations: List[Dict[str, Any]],
    max_minutes: int,
    max_budget_usd: float,
) -> Dict[str, Any]:
    """Find itinerary with exhaustive search over destination permutations."""
    capped = destinations[:8]
    best_result = create_plan_result(
        strategy='brute_force',
        total_score=0.0,
        total_minutes=0.0,
        total_cost_usd=0.0,
        stops=[],
        feasible=False,
    )
    for candidate in permutations(capped):
        evaluated = _evaluate_route(candidate, max_minutes, max_budget_usd)
        if evaluated['total_score'] > best_result['total_score']:
            best_result = evaluated
    best_result['strategy'] = 'brute_force'
    return best_result


def _compare_strategies(
    destinations: List[Dict[str, Any]],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Run configured planning strategies for side-by-side comparison."""
    comparison: List[Dict[str, Any]] = []
    for strategy in config['enabled_strategies']:
        if strategy == 'greedy':
            result = optimize_itinerary_greedy(destinations, config['max_trip_minutes'], config['max_budget_usd'])
        elif strategy == 'brute_force':
            result = optimize_itinerary_bruteforce(destinations, config['max_trip_minutes'], config['max_budget_usd'])
        else:
            continue
        comparison.append(result)
    return comparison


def _benchmark_runtime(config: Dict[str, Any], destinations: List[Dict[str, Any]], rng: random.Random) -> List[Dict[str, Any]]:
    """Benchmark strategy runtime across increasing destination counts."""
    points: List[Dict[str, Any]] = []
    for size in config['benchmark_stop_counts']:
        subset = destinations[: min(len(destinations), int(size))]
        for strategy in config['enabled_strategies']:
            for trial in range(1, config['benchmark_trials'] + 1):
                shuffled = subset[:]
                rng.shuffle(shuffled)
                started = time.perf_counter()
                if strategy == 'greedy':
                    optimize_itinerary_greedy(shuffled, config['max_trip_minutes'], config['max_budget_usd'])
                else:
                    optimize_itinerary_bruteforce(shuffled, config['max_trip_minutes'], config['max_budget_usd'])
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                points.append(create_runtime_point(strategy, float(len(shuffled)), trial, elapsed_ms))
    return points


def _aggregate_runtime(points: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, float]]]:
    """Average runtime benchmark points by strategy and stop count."""
    grouped: Dict[str, Dict[float, List[float]]] = defaultdict(lambda: defaultdict(list))
    for point in points:
        grouped[point['series']][point['size']].append(point['elapsed_ms'])

    summary: Dict[str, List[Dict[str, float]]] = {}
    for strategy, buckets in grouped.items():
        rows: List[Dict[str, float]] = []
        for size in sorted(buckets):
            rows.append({'size': size, 'elapsed_ms': round(mean(buckets[size]), 6)})
        summary[strategy] = rows
    return summary


def _save_runtime_chart(runtime_summary: Dict[str, List[Dict[str, float]]], session_id: str) -> str:
    """Persist benchmark runtime chart."""
    figure, axis = plt.subplots(figsize=(9.2, 5.0))
    for series, rows in runtime_summary.items():
        axis.plot(
            [row['size'] for row in rows],
            [row['elapsed_ms'] for row in rows],
            marker='o',
            linewidth=2,
            label=series.replace('_', ' ').title(),
            color=PLOT_COLORS.get(series, '#6c757d'),
        )
    axis.set_title('Average Runtime By Stop Count And Strategy')
    axis.set_xlabel('Destination count')
    axis.set_ylabel('Elapsed time (ms)')
    axis.grid(alpha=0.25)
    axis.legend(ncol=2)
    figure.tight_layout()
    file_path = OUTPUTS_DIR / f'strategy_runtime_{session_id}.png'
    figure.savefig(file_path, dpi=150)
    plt.close(figure)
    return str(file_path)


def _save_value_chart(stops: List[Dict[str, Any]], session_id: str) -> str:
    """Persist itinerary value trend chart across stop order."""
    figure, axis = plt.subplots(figsize=(8.8, 4.8))
    if stops:
        axis.plot(
            list(range(1, len(stops) + 1)),
            [float(row['score_gain']) for row in stops],
            marker='o',
            linewidth=2,
            color=PLOT_COLORS['selected_plan'],
        )
    axis.set_title('Stop Value Trend Across Planned Sequence')
    axis.set_xlabel('Stop index')
    axis.set_ylabel('Score contribution')
    axis.grid(alpha=0.25)
    figure.tight_layout()
    file_path = OUTPUTS_DIR / f'stop_value_trend_{session_id}.png'
    figure.savefig(file_path, dpi=150)
    plt.close(figure)
    return str(file_path)


def load_planner_profile() -> Dict[str, Any]:
    """Return startup profile built from previously saved catalogs."""
    ensure_data_dirs()
    run_catalog = load_run_catalog()
    library = load_destination_library()
    history = load_history()
    recent_runs = [
        f"{item.get('session_id', '')}:{item.get('best_strategy', '')}:{item.get('demo_sequence_label', '')}"
        for item in run_catalog[-5:]
    ]
    return {
        'catalog_file': 'data/runs.json',
        'library_file': 'data/itinerary_sets.json',
        'history_file': 'data/itinerary_history.json',
        'runs_stored': len(run_catalog),
        'destinations_available': len(library),
        'history_entries': len(history),
        'recent_runs': recent_runs,
    }


def run_core_flow() -> Dict[str, Any]:
    """Run one complete itinerary optimization, benchmark, and plotting session."""
    ensure_data_dirs()
    config = create_planner_config()
    session_id = _session_id()
    rng = random.Random(config['random_seed'])
    started = time.perf_counter()

    destination_library = load_destination_library()
    if not destination_library:
        destination_library = _default_destination_library()
        save_destination_library(destination_library)

    demo_destinations = [item for item in destination_library if item['label'] == config['demo_sequence_label']]
    if not demo_destinations:
        demo_destinations = destination_library[:]

    comparison = _compare_strategies(demo_destinations, config)
    selected_plan = next((item for item in comparison if item['strategy'] == config['strategy']), None)
    if selected_plan is None and comparison:
        selected_plan = max(comparison, key=lambda item: float(item['total_score']))
    selected_plan = selected_plan or create_plan_result('none', 0.0, 0.0, 0.0, [], False)

    history = load_history()
    history.append(
        create_history_entry(
            'itinerary_plan',
            {
                'session_id': session_id,
                'strategy': selected_plan['strategy'],
                'stops_planned': len(selected_plan['stops']),
                'total_minutes': selected_plan['total_minutes'],
                'total_cost_usd': selected_plan['total_cost_usd'],
                'total_score': selected_plan['total_score'],
            },
        )
    )
    history.extend(create_history_entry('itinerary_stop', stop) for stop in selected_plan['stops'])
    history = history[-400:]
    history_file = save_history(history)

    runtime_points = _benchmark_runtime(config, demo_destinations, rng)
    runtime_summary = _aggregate_runtime(runtime_points)

    trace_payload = {
        'session_id': session_id,
        'config': config,
        'destinations': demo_destinations,
        'strategy_comparison': comparison,
        'selected_plan': selected_plan,
        'history_file': history_file,
    }
    benchmark_payload = {
        'session_id': session_id,
        'runtime_points': runtime_points,
        'runtime_summary': runtime_summary,
    }

    runtime_chart_file = ''
    value_chart_file = ''
    if config['include_runtime_plot']:
        runtime_chart_file = _save_runtime_chart(runtime_summary, session_id)
    if config['include_value_plot']:
        value_chart_file = _save_value_chart(selected_plan['stops'], session_id)

    trace_file = save_trace_file(trace_payload, session_id)
    benchmark_file = save_benchmark_file(benchmark_payload, session_id)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    average_by_series = {
        series: mean(row['elapsed_ms'] for row in rows)
        for series, rows in runtime_summary.items()
        if rows
    }
    best_strategy = min(average_by_series.items(), key=lambda item: item[1])[0] if average_by_series else ''
    best_total_score = max((float(item['total_score']) for item in comparison), default=0.0)

    metrics = {
        'best_strategy': best_strategy,
        'best_avg_runtime_ms': round(average_by_series.get(best_strategy, 0.0), 6),
        'selected_total_score': round(float(selected_plan['total_score']), 6),
        'best_total_score': round(best_total_score, 6),
        'history_size': len(history),
    }

    artifacts = {
        'trace_file': trace_file,
        'benchmark_file': benchmark_file,
        'runtime_chart_file': runtime_chart_file,
        'value_chart_file': value_chart_file,
        'history_file': history_file,
    }

    summary = create_session_summary(
        session_id=session_id,
        destinations_available=len(destination_library),
        demo_sequence_label=config['demo_sequence_label'],
        strategy_selected=selected_plan['strategy'],
        routes_evaluated=len(comparison),
        stops_planned=len(selected_plan['stops']),
        runtime_points=len(runtime_points),
        elapsed_ms=elapsed_ms,
        artifacts=artifacts,
        itinerary_previews=selected_plan['stops'][: config['max_preview_rows']],
        metrics=metrics,
    )
    summary['history_previews'] = history[-config['max_preview_rows'] :]
    summary['max_preview_rows'] = config['max_preview_rows']
    summary['selected_plan'] = selected_plan

    run_record = dict(summary)
    session_file = save_run_record(run_record)
    summary['artifacts']['session_file'] = session_file
    return summary

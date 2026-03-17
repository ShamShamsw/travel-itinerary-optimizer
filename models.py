"""Data models for Project 46: Travel Itinerary Optimizer."""

from datetime import datetime
from typing import Any, Dict, List


def _utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'


def create_planner_config(
    strategy: str = 'brute_force',
    enabled_strategies: List[str] | None = None,
    demo_sequence_label: str = 'weekend_city_mix',
    max_trip_minutes: int = 520,
    max_budget_usd: float = 180.0,
    benchmark_stop_counts: List[int] | None = None,
    benchmark_trials: int = 4,
    include_runtime_plot: bool = True,
    include_value_plot: bool = True,
    max_preview_rows: int = 8,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Create a validated configuration record for one planner session."""
    strategies = enabled_strategies if enabled_strategies else ['greedy', 'brute_force']
    stop_counts = benchmark_stop_counts if benchmark_stop_counts else [4, 5, 6, 7, 8]
    normalized_strategy = str(strategy).strip().lower()
    selected_strategy = normalized_strategy if normalized_strategy in strategies else 'brute_force'
    return {
        'project_type': 'travel_itinerary_optimizer',
        'strategy': selected_strategy,
        'enabled_strategies': [str(value) for value in strategies],
        'demo_sequence_label': str(demo_sequence_label),
        'max_trip_minutes': max(90, int(max_trip_minutes)),
        'max_budget_usd': max(20.0, float(max_budget_usd)),
        'benchmark_stop_counts': [max(3, int(value)) for value in stop_counts],
        'benchmark_trials': max(1, int(benchmark_trials)),
        'include_runtime_plot': bool(include_runtime_plot),
        'include_value_plot': bool(include_value_plot),
        'max_preview_rows': max(1, int(max_preview_rows)),
        'random_seed': int(random_seed),
        'created_at': _utc_timestamp(),
    }


def create_destination_case(
    destination_id: str,
    label: str,
    name: str,
    x: float,
    y: float,
    visit_minutes: int,
    cost_usd: float,
    priority: float,
    description: str,
    tags: List[str],
) -> Dict[str, Any]:
    """Create one reusable destination record."""
    return {
        'destination_id': str(destination_id),
        'label': str(label),
        'name': str(name),
        'x': float(x),
        'y': float(y),
        'visit_minutes': max(10, int(visit_minutes)),
        'cost_usd': round(max(0.0, float(cost_usd)), 2),
        'priority': round(max(0.1, float(priority)), 2),
        'description': str(description),
        'tags': [str(tag) for tag in tags],
    }


def create_stop_result(
    stop_index: int,
    name: str,
    travel_minutes: float,
    visit_minutes: int,
    cost_usd: float,
    score_gain: float,
    cumulative_minutes: float,
    cumulative_cost_usd: float,
) -> Dict[str, Any]:
    """Create one itinerary stop output record."""
    return {
        'stop_index': int(stop_index),
        'name': str(name),
        'travel_minutes': round(float(travel_minutes), 3),
        'visit_minutes': int(visit_minutes),
        'cost_usd': round(float(cost_usd), 2),
        'score_gain': round(float(score_gain), 5),
        'cumulative_minutes': round(float(cumulative_minutes), 3),
        'cumulative_cost_usd': round(float(cumulative_cost_usd), 2),
    }


def create_plan_result(
    strategy: str,
    total_score: float,
    total_minutes: float,
    total_cost_usd: float,
    stops: List[Dict[str, Any]],
    feasible: bool,
) -> Dict[str, Any]:
    """Create one strategy plan result record."""
    return {
        'strategy': str(strategy),
        'total_score': round(float(total_score), 6),
        'total_minutes': round(float(total_minutes), 3),
        'total_cost_usd': round(float(total_cost_usd), 2),
        'stops': list(stops),
        'feasible': bool(feasible),
    }


def create_history_entry(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create one persistent history entry."""
    return {
        'event_type': str(event_type),
        'payload': dict(payload),
        'created_at': _utc_timestamp(),
    }


def create_runtime_point(series: str, size: float, trial: int, elapsed_ms: float) -> Dict[str, Any]:
    """Create one benchmark runtime point."""
    return {
        'series': str(series),
        'size': float(size),
        'trial': int(trial),
        'elapsed_ms': round(float(elapsed_ms), 6),
    }


def create_session_summary(
    session_id: str,
    destinations_available: int,
    demo_sequence_label: str,
    strategy_selected: str,
    routes_evaluated: int,
    stops_planned: int,
    runtime_points: int,
    elapsed_ms: float,
    artifacts: Dict[str, Any],
    itinerary_previews: List[Dict[str, Any]],
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Create final session summary for reporting and persistence."""
    return {
        'session_id': str(session_id),
        'destinations_available': int(destinations_available),
        'demo_sequence_label': str(demo_sequence_label),
        'strategy_selected': str(strategy_selected),
        'routes_evaluated': int(routes_evaluated),
        'stops_planned': int(stops_planned),
        'runtime_points': int(runtime_points),
        'elapsed_ms': round(float(elapsed_ms), 5),
        'artifacts': dict(artifacts),
        'itinerary_previews': list(itinerary_previews),
        'metrics': dict(metrics),
        'finished_at': _utc_timestamp(),
    }


def create_record(**kwargs):
    """Backwards-compatible generic record factory."""
    return dict(kwargs)

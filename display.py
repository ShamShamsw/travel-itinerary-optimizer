"""Presentation helpers for Project 46: Travel Itinerary Optimizer."""

from typing import Any, Dict, List


def format_header() -> str:
    """Format session header banner."""
    return '=' * 70 + '\n' + '   TRAVEL ITINERARY OPTIMIZER\n' + '=' * 70


def format_startup_guide(config: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """Format startup configuration and historical profile."""
    recent = ', '.join(profile.get('recent_runs', [])) or 'None yet'
    lines = [
        '',
        'Configuration:',
        f"   Project type:           {config['project_type']}",
        f"   Strategy selected:      {config['strategy']}",
        f"   Strategy set:           {', '.join(config['enabled_strategies'])}",
        f"   Demo sequence:          {config['demo_sequence_label']}",
        f"   Trip time cap:          {config['max_trip_minutes']} minutes",
        f"   Budget cap:             ${config['max_budget_usd']:.2f}",
        f"   Benchmark stop counts:  {', '.join(str(value) for value in config['benchmark_stop_counts'])}",
        f"   Trials per stop count:  {config['benchmark_trials']}",
        f"   Runtime chart:          {config['include_runtime_plot']}",
        f"   Value chart:            {config['include_value_plot']}",
        f"   Max preview rows:       {config['max_preview_rows']}",
        f"   Random seed:            {config['random_seed']}",
        '',
        'Startup:',
        '   Data directory:         data/',
        '   Outputs directory:      data/outputs/',
        (
            f"   Destination library:    {profile['library_file']} "
            f"(loaded {profile['destinations_available']} destinations)"
        ),
        (
            f"   Run catalog:            {profile['catalog_file']} "
            f"(loaded {profile['runs_stored']} runs)"
        ),
        (
            f"   Itinerary history:      {profile['history_file']} "
            f"(loaded {profile['history_entries']} entries)"
        ),
        f"   Recent runs:            {recent}",
        '',
        '---',
    ]
    return '\n'.join(lines)


def _clip_preview(value: str, width: int = 36) -> str:
    """Return a compact preview string for table output."""
    compact = value.replace('\n', ' ').strip()
    if len(compact) <= width:
        return compact
    return compact[: width - 3] + '...'


def format_itinerary_table(stops: List[Dict[str, Any]]) -> str:
    """Format itinerary stop preview table."""
    if not stops:
        return 'No itinerary previews generated.'
    lines = [
        'Itinerary previews:',
        '   Stop | Destination                    | Travel | Visit | Cost    | Score',
        '   -----+--------------------------------+--------+-------+---------+----------',
    ]
    for row in stops:
        lines.append(
            '   '
            f"{int(row.get('stop_index', 0)):<4} | "
            f"{_clip_preview(str(row.get('name', '')), 30):<30} | "
            f"{float(row.get('travel_minutes', 0.0)):<6.2f} | "
            f"{int(row.get('visit_minutes', 0)):<5} | "
            f"${float(row.get('cost_usd', 0.0)):<6.2f} | "
            f"{float(row.get('score_gain', 0.0)):<8.3f}"
        )
    return '\n'.join(lines)


def format_history_table(history: List[Dict[str, Any]], max_rows: int) -> str:
    """Format history preview table."""
    if not history:
        return 'No history entries available.'
    lines = [
        'Recent history:',
        '   Event type      | Preview                              | Created at',
        '   ----------------+--------------------------------------+----------------------',
    ]
    for row in history[-max_rows:]:
        payload = row.get('payload', {})
        if row.get('event_type') == 'itinerary_plan':
            preview = (
                f"{payload.get('strategy', '')} | "
                f"stops={payload.get('stops_planned', 0)} | "
                f"score={payload.get('total_score', 0)}"
            )
        elif row.get('event_type') == 'itinerary_stop':
            preview = f"{payload.get('stop_index', 0)}. {payload.get('name', '')}"
        else:
            preview = str(payload)
        lines.append(
            '   '
            f"{_clip_preview(str(row.get('event_type', '')), 14):<14} | "
            f"{_clip_preview(preview, 36):<36} | "
            f"{_clip_preview(str(row.get('created_at', '')), 20):<20}"
        )
    return '\n'.join(lines)


def format_run_report(summary: Dict[str, Any]) -> str:
    """Format final session report."""
    artifacts = summary.get('artifacts', {})
    metrics = summary.get('metrics', {})
    selected_plan = summary.get('selected_plan', {})
    lines = [
        '',
        'Session complete:',
        f"   Session ID:             {summary['session_id']}",
        f"   Destinations available: {summary['destinations_available']}",
        f"   Demo sequence:          {summary['demo_sequence_label']}",
        f"   Strategy selected:      {summary['strategy_selected']}",
        f"   Routes evaluated:       {summary['routes_evaluated']}",
        f"   Stops planned:          {summary['stops_planned']}",
        f"   Runtime points:         {summary['runtime_points']}",
        f"   Elapsed time:           {summary['elapsed_ms']:.2f} ms",
        '',
        (
            'Planner metrics: '
            f"best_strategy={metrics.get('best_strategy', 'N/A')} | "
            f"best_avg_runtime_ms={metrics.get('best_avg_runtime_ms', 0.0):.6f} | "
            f"selected_total_score={metrics.get('selected_total_score', 0.0):.5f} | "
            f"history_size={metrics.get('history_size', 0)}"
        ),
        '',
        (
            'Selected plan totals: '
            f"minutes={float(selected_plan.get('total_minutes', 0.0)):.2f} | "
            f"cost_usd={float(selected_plan.get('total_cost_usd', 0.0)):.2f}"
        ),
        '',
        format_itinerary_table(summary.get('itinerary_previews', [])),
        '',
        format_history_table(summary.get('history_previews', []), max_rows=summary.get('max_preview_rows', 8)),
        '',
        'Artifacts saved:',
        f"   Session record:         {artifacts.get('session_file', 'N/A')}",
        f"   Trace bundle:           {artifacts.get('trace_file', 'N/A')}",
        f"   Benchmark file:         {artifacts.get('benchmark_file', 'N/A')}",
        f"   Runtime chart:          {artifacts.get('runtime_chart_file', 'N/A')}",
        f"   Value chart:            {artifacts.get('value_chart_file', 'N/A')}",
    ]
    return '\n'.join(lines)


def format_message(message: str) -> str:
    """Format a user-facing message string."""
    return f'[Project 46] {message}'

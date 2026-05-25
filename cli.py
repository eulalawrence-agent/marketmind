#!/usr/bin/env python3
"""
MarketMind CLI - AI-Powered Prediction Market Intelligence Platform

Usage:
    python cli.py analyze [--limit N] [--category CAT]
    python cli.py monitor [--interval SECONDS]
    python cli.py report [--output FILE]
    python cli.py stats
"""

import asyncio
import argparse
import json
import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import get_config, Config
from core.orchestrator import Orchestrator
from agents import (
    DataIngestor, MarketParser, SentimentAnalyzer,
    CorrelationEngine, RiskAssessor, PatternDetector,
    PredictiveModeler, ConfidenceScorer, ReportGenerator,
)


def create_orchestrator(config: Config) -> Orchestrator:
    """Create and configure the 9-agent orchestrator."""
    orch = Orchestrator(config)

    orch.register_agent("data_ingestor", DataIngestor(config))
    orch.register_agent("market_parser", MarketParser(config))
    orch.register_agent("sentiment_analyzer", SentimentAnalyzer(config))
    orch.register_agent("correlation_engine", CorrelationEngine(config))
    orch.register_agent("risk_assessor", RiskAssessor(config))
    orch.register_agent("pattern_detector", PatternDetector(config))
    orch.register_agent("predictive_modeler", PredictiveModeler(config))
    orch.register_agent("confidence_scorer", ConfidenceScorer(config))
    orch.register_agent("report_generator", ReportGenerator(config))

    return orch


async def cmd_analyze(args):
    """Run full analysis pipeline on Polymarket data."""
    config = get_config()
    orch = create_orchestrator(config)

    print("=" * 60)
    print("  🧠 MarketMind - AI Prediction Market Intelligence")
    print("=" * 60)
    print()

    # Fetch markets
    print("📡 Fetching markets from Polymarket...")
    ingestor = DataIngestor(config)
    markets = await ingestor.fetch_polymarket_markets(limit=args.limit)
    await ingestor.close()

    if not markets:
        print("❌ No markets found. Check API connectivity.")
        return

    print(f"✅ Found {len(markets)} active markets")
    print()

    # Filter by category if specified
    if args.category:
        parser = MarketParser(config)
        parsed = [parser.parse_market(m) for m in markets]
        markets = [
            m for m, p in zip(markets, parsed)
            if p.get("category", "").lower() == args.category.lower()
        ]
        print(f"📂 Filtered to {len(markets)} markets in '{args.category}' category")
        if not markets:
            print("❌ No markets match that category.")
            return

    # Run pipeline
    print("🔄 Running 9-agent analysis pipeline...")
    print("   Agents: Ingestor → Parser → Sentiment → Correlator →")
    print("           Risk → Pattern → Predictor → Scorer → Reporter")
    print()

    results = await orch.run_batch(markets, max_concurrent=3)

    # Display results
    total_tokens = 0
    for result in results:
        if hasattr(result, "to_dict"):
            data = result.to_dict()
            total_tokens += data.get("tokens_consumed", 0)

            report_stage = data.get("stages", {}).get("report_generation", {})
            report = report_stage.get("report", {})

            # Print executive summary
            if report.get("executive_summary"):
                print(report["executive_summary"])
                print()

            # Print market reports
            for mr in report.get("market_reports", [])[:5]:
                print(mr)
                print()

    # Stats
    stats = orch.get_stats()
    print("=" * 60)
    print(f"  📊 Pipeline Stats:")
    print(f"     Markets analyzed: {stats['total_analyses']}")
    print(f"     Tokens consumed: {stats['total_tokens']:,}")
    print(f"     Avg per market: {stats['avg_tokens_per_analysis']:,}")
    print(f"     Errors: {stats['errors']}")
    print(f"     Duration: {stats['elapsed_seconds']:.1f}s")
    print("=" * 60)


async def cmd_report(args):
    """Generate a detailed report."""
    config = get_config()
    orch = create_orchestrator(config)

    # Run analysis first
    ingestor = DataIngestor(config)
    markets = await ingestor.fetch_polymarket_markets(limit=args.limit)
    await ingestor.close()

    if not markets:
        print("❌ No markets found.")
        return

    results = await orch.run_batch(markets, max_concurrent=3)

    # Collect all reports
    all_reports = []
    for result in results:
        if hasattr(result, "to_dict"):
            data = result.to_dict()
            report = data.get("stages", {}).get("report_generation", {}).get("report", {})
            all_reports.append(report)

    # Save to file
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "market_count": len(all_reports),
        "reports": all_reports,
        "stats": orch.get_stats(),
    }

    output_path = args.output or "output/report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"✅ Report saved to {output_path}")
    print(f"   Markets: {len(all_reports)}")
    print(f"   Stats: {json.dumps(orch.get_stats(), indent=2)}")


async def cmd_stats(args):
    """Show system stats and token projections."""
    config = get_config()

    print("=" * 60)
    print("  📊 MarketMind - Token Consumption Projections")
    print("=" * 60)
    print()
    print("  Agent Pipeline (9 agents):")
    agents = [
        ("Data Ingestor", "8K", "57,600", "461M"),
        ("Market Parser", "12K", "57,600", "691M"),
        ("Sentiment Analyzer", "18K", "57,600", "1.04B"),
        ("Correlation Engine", "20K", "57,600", "1.15B"),
        ("Risk Assessor", "15K", "57,600", "864M"),
        ("Pattern Detector", "16K", "57,600", "922M"),
        ("Predictive Modeler", "22K", "57,600", "1.27B"),
        ("Confidence Scorer", "10K", "57,600", "576M"),
        ("Report Generator", "25K", "57,600", "1.44B"),
    ]

    total_daily = 0
    print(f"  {'Agent':<25} {'Tokens/Op':<12} {'Ops/Day':<12} {'Daily Total':<12}")
    print(f"  {'-'*61}")
    for name, tokens, ops, daily in agents:
        print(f"  {name:<25} {tokens:<12} {ops:<12} {daily:<12}")
        # Parse daily total
        val = float(daily.replace("M", "").replace("B", "000"))
        total_daily += val

    print(f"  {'-'*61}")
    print(f"  {'TOTAL':<25} {'146K':<12} {'57,600':<12} {total_daily/1000:.1f}B/day")
    print()
    print(f"  Monthly projection: {total_daily*30/1000:.0f}B tokens")
    print(f"  MiMo V2.5-70B (FREE) at scale = massive cost savings")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="MarketMind - AI-Powered Prediction Market Intelligence"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Run full analysis")
    p_analyze.add_argument("--limit", type=int, default=50, help="Max markets to analyze")
    p_analyze.add_argument("--category", type=str, help="Filter by category")

    # report
    p_report = subparsers.add_parser("report", help="Generate report")
    p_report.add_argument("--limit", type=int, default=50, help="Max markets")
    p_report.add_argument("--output", type=str, help="Output file path")

    # stats
    p_stats = subparsers.add_parser("stats", help="Show token consumption stats")

    args = parser.parse_args()

    if args.command == "analyze":
        asyncio.run(cmd_analyze(args))
    elif args.command == "report":
        asyncio.run(cmd_report(args))
    elif args.command == "stats":
        asyncio.run(cmd_stats(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

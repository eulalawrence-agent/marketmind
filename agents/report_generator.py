"""Agent 9: Report Generator - Generates final analysis reports."""

from datetime import datetime, timezone
from typing import Dict, Any


class ReportGenerator:
    """
    Generates comprehensive analysis reports from all agent outputs.

    Token consumption: ~25K tokens per report (full synthesis)
    """

    def __init__(self, config):
        self.config = config

    def _format_market_report(self, market_id: str, question: str, prediction: str,
                               confidence: float, tier: str, recommendation: str,
                               risk_level: str, sentiment: str) -> str:
        emoji = {"S": "🏆", "A": "✅", "B": "📊", "C": "⚠️", "D": "❌"}.get(tier, "❓")
        return (
            f"{emoji} [{tier}] {question}\n"
            f"   Direction: {prediction.upper()} | Confidence: {confidence:.1%} | "
            f"Risk: {risk_level} | Sentiment: {sentiment}\n"
            f"   Recommendation: {recommendation}"
        )

    def _generate_executive_summary(self, all_context: Dict) -> str:
        scored = all_context.get("confidence_scoring", {})
        aggregate = scored.get("aggregate", {})

        lines = [
            "═══════════════════════════════════════════════════════",
            "  MARKETMIND ANALYSIS REPORT - EXECUTIVE SUMMARY",
            "═══════════════════════════════════════════════════════",
            "",
            f"  Markets Analyzed: {scored.get('scored_count', 0)}",
            f"  Avg Confidence: {aggregate.get('avg_confidence', 0):.1%}",
            f"  Actionable Markets: {aggregate.get('actionable_count', 0)}",
            "",
            "  Tier Distribution:",
        ]

        tier_dist = aggregate.get("tier_distribution", {})
        for tier, count in tier_dist.items():
            lines.append(f"    {tier}: {count} markets")

        return "\n".join(lines)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final report from all pipeline stages."""
        # Collect all data
        ingestion = context.get("data_ingestion", {})
        parsing = context.get("market_parsing", {})
        sentiment = context.get("sentiment_analysis", {})
        correlation = context.get("cross_market_correlation", {})
        risk = context.get("risk_assessment", {})
        patterns = context.get("pattern_detection", {})
        prediction = context.get("predictive_modeling", {})
        scoring = context.get("confidence_scoring", {})

        # Executive summary
        exec_summary = self._generate_executive_summary(context)

        # Market-level reports
        market_reports = []
        scores = scoring.get("scores", [])
        risks = risk.get("assessments", [])
        sentiments = sentiment.get("market_sentiments", [])

        for i, score in enumerate(scores):
            risk_data = risks[i] if i < len(risks) else {}
            sent_data = sentiments[i] if i < len(sentiments) else {}

            report = self._format_market_report(
                market_id=score.get("market_id", ""),
                question=score.get("question", ""),
                prediction=score.get("prediction_direction", "neutral"),
                confidence=score.get("confidence", {}).get("final_confidence", 0),
                tier=score.get("confidence", {}).get("tier", "C"),
                recommendation=score.get("confidence", {}).get("recommendation", "HOLD"),
                risk_level=risk_data.get("composite", {}).get("level", "unknown"),
                sentiment=sent_data.get("sentiment", {}).get("sentiment_label", "neutral"),
            )
            market_reports.append(report)

        # Pattern summary
        pattern_summary = patterns.get("summary", {})
        corr_summary = {
            "correlations_found": correlation.get("pairwise_count", 0),
            "clusters": correlation.get("cluster_count", 0),
        }

        # Full report
        full_report = {
            "executive_summary": exec_summary,
            "market_reports": market_reports,
            "data_sources": {
                "polymarket_markets": ingestion.get("polymarket_markets", 0),
                "defi_protocols": ingestion.get("defi_protocols", 0),
                "chain_tvl": ingestion.get("chain_tvl_count", 0),
            },
            "pattern_analysis": pattern_summary,
            "correlation_analysis": corr_summary,
            "sentiment_overview": sentiment.get("aggregate", {}),
            "risk_overview": risk.get("aggregate", {}),
            "prediction_overview": prediction.get("aggregate", {}),
            "scoring_overview": scoring.get("aggregate", {}),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        return {
            "report": full_report,
            "tokens_used": 25_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

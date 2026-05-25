"""Agent 5: Risk Assessor - Evaluates risk factors for each market."""

import math
from datetime import datetime, timezone
from typing import Dict, Any


class RiskAssessor:
    """
    Evaluates risk factors including liquidity risk, manipulation risk, and resolution risk.

    Token consumption: ~15K tokens per market
    """

    def __init__(self, config):
        self.config = config

    def _assess_liquidity_risk(self, liquidity: float, volume: float) -> Dict:
        if liquidity < 1000:
            level, score = "critical", 0.9
        elif liquidity < 10000:
            level, score = "high", 0.7
        elif liquidity < 100000:
            level, score = "medium", 0.4
        else:
            level, score = "low", 0.1

        return {
            "level": level,
            "score": score,
            "liquidity_usd": liquidity,
            "volume_usd": volume,
            "warning": "Low liquidity increases manipulation risk" if score > 0.5 else None,
        }

    def _assess_manipulation_risk(self, market: Dict) -> Dict:
        volume = market.get("volume", 0)
        liquidity = market.get("liquidity", 0)
        ratio = volume / max(liquidity, 1)

        # High volume/low liquidity = manipulation risk
        if ratio > 50:
            level, score = "critical", 0.85
        elif ratio > 20:
            level, score = "high", 0.6
        elif ratio > 5:
            level, score = "medium", 0.3
        else:
            level, score = "low", 0.1

        return {
            "level": level,
            "score": score,
            "volume_liquidity_ratio": round(ratio, 2),
        }

    def _assess_resolution_risk(self, market: Dict) -> Dict:
        """Assess risk of market resolution issues."""
        question = market.get("question", "").lower()
        risk_factors = []

        if "by" in question and ("end" in question or "before" in question):
            risk_factors.append("time_bound")
        if "exact" in question or "precisely" in question:
            risk_factors.append("precise_criteria")
        if "or" in question:
            risk_factors.append("multi_outcome")
        if not market.get("end_date"):
            risk_factors.append("no_end_date")

        score = min(len(risk_factors) * 0.2, 0.9)
        return {
            "score": round(score, 3),
            "factors": risk_factors,
            "level": "high" if score > 0.6 else "medium" if score > 0.3 else "low",
        }

    def _compute_composite_risk(self, liquidity_risk, manipulation_risk, resolution_risk) -> Dict:
        weights = {"liquidity": 0.35, "manipulation": 0.35, "resolution": 0.30}
        composite = (
            liquidity_risk["score"] * weights["liquidity"] +
            manipulation_risk["score"] * weights["manipulation"] +
            resolution_risk["score"] * weights["resolution"]
        )
        return {
            "composite_score": round(composite, 3),
            "level": "critical" if composite > 0.7 else "high" if composite > 0.5 else "medium" if composite > 0.3 else "low",
            "components": {
                "liquidity": round(liquidity_risk["score"], 3),
                "manipulation": round(manipulation_risk["score"], 3),
                "resolution": round(resolution_risk["score"], 3),
            },
        }

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        parsed = context.get("market_parsing", {})
        markets = parsed.get("parsed_markets", [])

        assessments = []
        for market in markets:
            liq = self._assess_liquidity_risk(market.get("liquidity", 0), market.get("volume", 0))
            manip = self._assess_manipulation_risk(market)
            res = self._assess_resolution_risk(market)
            composite = self._compute_composite_risk(liq, manip, res)

            assessments.append({
                "market_id": market.get("id", ""),
                "question": market.get("question", ""),
                "liquidity_risk": liq,
                "manipulation_risk": manip,
                "resolution_risk": res,
                "composite": composite,
            })

        # Aggregate
        if assessments:
            avg_risk = sum(a["composite"]["composite_score"] for a in assessments) / len(assessments)
            high_risk = sum(1 for a in assessments if a["composite"]["level"] in ("high", "critical"))
        else:
            avg_risk = 0
            high_risk = 0

        return {
            "assessed_count": len(assessments),
            "assessments": assessments,
            "aggregate": {
                "avg_risk_score": round(avg_risk, 3),
                "high_risk_count": high_risk,
                "risk_distribution": {
                    "critical": sum(1 for a in assessments if a["composite"]["level"] == "critical"),
                    "high": sum(1 for a in assessments if a["composite"]["level"] == "high"),
                    "medium": sum(1 for a in assessments if a["composite"]["level"] == "medium"),
                    "low": sum(1 for a in assessments if a["composite"]["level"] == "low"),
                },
            },
            "tokens_used": 15_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

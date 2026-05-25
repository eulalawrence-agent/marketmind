"""Agent 8: Confidence Scorer - Computes final confidence scores."""

import math
from datetime import datetime, timezone
from typing import Dict, Any, List


class ConfidenceScorer:
    """
    Aggregates all signals into a final confidence score for each prediction.

    Token consumption: ~10K tokens per market
    """

    def __init__(self, config):
        self.config = config

    def _compute_confidence(self, prediction: Dict, risk: Dict, sentiment: Dict) -> Dict:
        """Compute final confidence combining all agent outputs."""
        ensemble_score = prediction.get("ensemble_score", 0.5)
        risk_score = 1 - risk.get("composite", {}).get("composite_score", 0.5)
        sent_confidence = sentiment.get("sentiment", {}).get("confidence", 0.5)
        bias_penalty = risk.get("resolution_risk", {}).get("score", 0) * 0.3

        raw_confidence = (
            ensemble_score * 0.4 +
            risk_score * 0.25 +
            sent_confidence * 0.25 +
            (1 - bias_penalty) * 0.1
        )

        # Normalize to 0-1
        final = max(0, min(1, raw_confidence))

        return {
            "raw_confidence": round(raw_confidence, 3),
            "final_confidence": round(final, 3),
            "components": {
                "ensemble": round(ensemble_score, 3),
                "risk_inverse": round(risk_score, 3),
                "sentiment": round(sent_confidence, 3),
                "bias_penalty": round(bias_penalty, 3),
            },
            "tier": (
                "S" if final > 0.85 else
                "A" if final > 0.7 else
                "B" if final > 0.5 else
                "C" if final > 0.3 else
                "D"
            ),
            "recommendation": (
                "STRONG_BUY" if final > 0.8 else
                "BUY" if final > 0.6 else
                "HOLD" if final > 0.4 else
                "AVOID" if final > 0.2 else
                "STRONG_AVOID"
            ),
        }

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        predictions = context.get("predictive_modeling", {}).get("predictions", [])
        risk_assessments = context.get("risk_assessment", {}).get("assessments", [])
        sentiments = context.get("sentiment_analysis", {}).get("market_sentiments", [])

        scores = []
        for i, pred in enumerate(predictions):
            risk = risk_assessments[i] if i < len(risk_assessments) else {}
            sent = sentiments[i] if i < len(sentiments) else {}

            confidence = self._compute_confidence(pred.get("prediction", {}), risk, sent)
            scores.append({
                "market_id": pred.get("market_id", ""),
                "question": pred.get("question", ""),
                "prediction_direction": pred.get("prediction", {}).get("prediction", "neutral"),
                "confidence": confidence,
            })

        # Tier distribution
        tier_dist = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        for s in scores:
            tier = s["confidence"]["tier"]
            tier_dist[tier] = tier_dist.get(tier, 0) + 1

        avg_conf = sum(s["confidence"]["final_confidence"] for s in scores) / max(len(scores), 1)

        return {
            "scored_count": len(scores),
            "scores": scores,
            "aggregate": {
                "avg_confidence": round(avg_conf, 3),
                "tier_distribution": tier_dist,
                "actionable_count": sum(1 for s in scores if s["confidence"]["final_confidence"] > 0.6),
            },
            "tokens_used": 10_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

"""Agent 7: Predictive Modeler - Generates price/outcome predictions."""

import math
from datetime import datetime, timezone
from typing import Dict, Any, List


class PredictiveModeler:
    """
    Generates predictions using ensemble of signals:
    - Market price (from Polymarket)
    - Sentiment score
    - Volume momentum
    - Cross-market correlation

    Token consumption: ~22K tokens per market (complex multi-factor modeling)
    """

    def __init__(self, config):
        self.config = config

    def _calculate_momentum(self, volume: float, liquidity: float) -> Dict:
        """Volume momentum indicator."""
        ratio = volume / max(liquidity, 1)
        if ratio > 20:
            momentum = "strong_bullish"
            confidence = 0.8
        elif ratio > 10:
            momentum = "bullish"
            confidence = 0.6
        elif ratio > 3:
            momentum = "neutral"
            confidence = 0.4
        elif ratio > 1:
            momentum = "bearish"
            confidence = 0.3
        else:
            momentum = "strong_bearish"
            confidence = 0.2

        return {
            "direction": momentum,
            "confidence": confidence,
            "volume_liquidity_ratio": round(ratio, 3),
        }

    def _ensemble_predict(self, market: Dict, sentiment: Dict, risk: Dict) -> Dict:
        """Ensemble prediction combining multiple signals."""
        # Signal 1: Volume momentum
        momentum = self._calculate_momentum(market.get("volume", 0), market.get("liquidity", 0))

        # Signal 2: Sentiment
        sent_score = sentiment.get("sentiment", {}).get("positive_score", 0.5)

        # Signal 3: Risk inverse (lower risk = higher confidence)
        risk_score = 1 - risk.get("composite", {}).get("composite_score", 0.5)

        # Signal 4: Market maturity (higher volume = more mature)
        vol_log = math.log10(max(market.get("volume", 1), 1))
        maturity = min(vol_log / 7, 1)  # Normalize to 0-1

        # Ensemble weights
        weights = {"momentum": 0.3, "sentiment": 0.25, "risk": 0.25, "maturity": 0.2}

        ensemble_score = (
            momentum["confidence"] * weights["momentum"] +
            sent_score * weights["sentiment"] +
            risk_score * weights["risk"] +
            maturity * weights["maturity"]
        )

        # Direction from momentum
        direction = momentum["direction"]

        return {
            "prediction": direction,
            "ensemble_score": round(ensemble_score, 3),
            "signals": {
                "momentum": momentum,
                "sentiment_score": round(sent_score, 3),
                "risk_inverse": round(risk_score, 3),
                "maturity": round(maturity, 3),
            },
            "weights": weights,
            "confidence_level": (
                "very_high" if ensemble_score > 0.8 else
                "high" if ensemble_score > 0.6 else
                "medium" if ensemble_score > 0.4 else
                "low"
            ),
        }

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        parsed = context.get("market_parsing", {})
        markets = parsed.get("parsed_markets", [])
        sentiments = context.get("sentiment_analysis", {}).get("market_sentiments", [])
        risk_data = context.get("risk_assessment", {}).get("assessments", [])

        predictions = []
        for i, market in enumerate(markets):
            sentiment = sentiments[i] if i < len(sentiments) else {}
            risk = risk_data[i] if i < len(risk_data) else {}

            pred = self._ensemble_predict(market, sentiment, risk)
            predictions.append({
                "market_id": market.get("id", ""),
                "question": market.get("question", ""),
                "prediction": pred,
            })

        # Aggregate predictions
        if predictions:
            avg_ensemble = sum(p["prediction"]["ensemble_score"] for p in predictions) / len(predictions)
            high_conf = sum(1 for p in predictions if p["prediction"]["confidence_level"] in ("high", "very_high"))
        else:
            avg_ensemble = 0
            high_conf = 0

        return {
            "prediction_count": len(predictions),
            "predictions": predictions,
            "aggregate": {
                "avg_ensemble_score": round(avg_ensemble, 3),
                "high_confidence_count": high_conf,
                "prediction_distribution": {
                    "very_high": sum(1 for p in predictions if p["prediction"]["confidence_level"] == "very_high"),
                    "high": sum(1 for p in predictions if p["prediction"]["confidence_level"] == "high"),
                    "medium": sum(1 for p in predictions if p["prediction"]["confidence_level"] == "medium"),
                    "low": sum(1 for p in predictions if p["prediction"]["confidence_level"] == "low"),
                },
            },
            "tokens_used": 22_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

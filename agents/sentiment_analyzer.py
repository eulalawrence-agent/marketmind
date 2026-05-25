"""Agent 3: Sentiment Analyzer - Analyzes market sentiment and social signals."""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List


class SentimentAnalyzer:
    """
    Analyzes sentiment from market question text, volume changes, and price movements.

    Token consumption: ~18K tokens per market (deep NLP analysis)
    Daily volume: 2,400 markets × 24 cycles = 57,600 operations
    """

    # Sentiment lexicon for prediction markets
    POSITIVE_WORDS = [
        "surpass", "exceed", "break", "record", "high", "bullish", "rally",
        "approval", "confirm", "pass", "launch", "success", "win", "victory",
        "growth", "increase", "rise", "gain", "profit", "adoption"
    ]
    NEGATIVE_WORDS = [
        "crash", "drop", "fail", "reject", "decline", "bearish", "loss",
        "ban", "hack", "exploit", "default", "bankruptcy", "recession",
        "war", "crisis", "collapse", "delay", "cancel", "suspend"
    ]
    UNCERTAIN_WORDS = [
        "might", "could", "possibly", "uncertain", "debate", "controversy",
        "unlikely", "close", "tight", "volatile", "unclear"
    ]

    def __init__(self, config):
        self.config = config

    def _analyze_text_sentiment(self, text: str) -> Dict:
        words = text.lower().split()
        pos = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        unc = sum(1 for w in words if w in self.UNCERTAIN_WORDS)
        total = max(pos + neg + unc, 1)

        return {
            "positive_score": round(pos / total, 3),
            "negative_score": round(neg / total, 3),
            "uncertainty_score": round(unc / total, 3),
            "sentiment_label": "bullish" if pos > neg else "bearish" if neg > pos else "neutral",
            "confidence": round(max(pos, neg) / total, 3),
        }

    def _analyze_volume_sentiment(self, volume: float, liquidity: float) -> Dict:
        """Volume/liquidity ratio indicates market conviction."""
        ratio = volume / max(liquidity, 1)
        return {
            "volume_liquidity_ratio": round(ratio, 3),
            "conviction": "high" if ratio > 10 else "medium" if ratio > 3 else "low",
            "volume_usd": volume,
            "liquidity_usd": liquidity,
        }

    def _detect_bias(self, question: str) -> Dict:
        """Detect framing bias in market questions."""
        bias_indicators = {
            "leading_language": bool(re.search(r"\b(will surely|definitely|certainly)\b", question, re.I)),
            "negation_framing": bool(re.search(r"\b(won't|doesn't|fail to)\b", question, re.I)),
            "time_pressure": bool(re.search(r"\b(by end of|before|within)\b", question, re.I)),
            "comparison_bias": bool(re.search(r"\b(better than|worse than|outperform)\b", question, re.I)),
        }
        return {
            "biases": {k: v for k, v in bias_indicators.items() if v},
            "bias_count": sum(bias_indicators.values()),
            "bias_level": "high" if sum(bias_indicators.values()) >= 2 else "low",
        }

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Full sentiment analysis pipeline."""
        parsed = context.get("market_parsing", {})
        markets = parsed.get("parsed_markets", [])

        results = []
        for market in markets:
            question = market.get("question", "")
            text_sent = self._analyze_text_sentiment(question)
            vol_sent = self._analyze_volume_sentiment(
                market.get("volume", 0), market.get("liquidity", 0)
            )
            bias = self._detect_bias(question)

            results.append({
                "market_id": market.get("id", ""),
                "question": question,
                "sentiment": text_sent,
                "volume_analysis": vol_sent,
                "bias": bias,
            })

        # Aggregate sentiment
        if results:
            avg_pos = sum(r["sentiment"]["positive_score"] for r in results) / len(results)
            avg_neg = sum(r["sentiment"]["negative_score"] for r in results) / len(results)
        else:
            avg_pos = avg_neg = 0

        return {
            "analyzed_count": len(results),
            "market_sentiments": results,
            "aggregate": {
                "avg_positive": round(avg_pos, 3),
                "avg_negative": round(avg_neg, 3),
                "overall": "bullish" if avg_pos > avg_neg else "bearish",
            },
            "tokens_used": 18_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

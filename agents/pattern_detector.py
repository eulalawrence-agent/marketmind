"""Agent 6: Pattern Detector - Identifies patterns in market behavior."""

import math
from datetime import datetime, timezone
from typing import Dict, Any, List
from collections import Counter


class PatternDetector:
    """
    Detects recurring patterns in prediction markets.

    Token consumption: ~16K tokens per analysis
    """

    def __init__(self, config):
        self.config = config

    def _detect_volume_patterns(self, markets: List[Dict]) -> List[Dict]:
        """Detect volume anomalies and patterns."""
        patterns = []
        volumes = [m.get("volume", 0) for m in markets]
        if not volumes:
            return patterns

        avg_vol = sum(volumes) / len(volumes)
        std_vol = math.sqrt(sum((v - avg_vol) ** 2 for v in volumes) / max(len(volumes), 1))

        for i, m in enumerate(markets):
            vol = m.get("volume", 0)
            z_score = (vol - avg_vol) / max(std_vol, 1)

            if abs(z_score) > 2:
                patterns.append({
                    "type": "volume_anomaly",
                    "market_id": m.get("id", ""),
                    "question": m.get("question", ""),
                    "z_score": round(z_score, 2),
                    "volume": vol,
                    "direction": "spike" if z_score > 0 else "drop",
                })

        return patterns

    def _detect_category_trends(self, markets: List[Dict]) -> Dict:
        """Detect trending categories."""
        cat_volumes = {}
        cat_counts = Counter()

        for m in markets:
            cat = m.get("category", "general")
            cat_volumes[cat] = cat_volumes.get(cat, 0) + m.get("volume", 0)
            cat_counts[cat] += 1

        # Sort by total volume
        sorted_cats = sorted(cat_volumes.items(), key=lambda x: x[1], reverse=True)

        return {
            "trending_categories": [
                {
                    "category": cat,
                    "total_volume": vol,
                    "market_count": cat_counts[cat],
                    "avg_volume": round(vol / max(cat_counts[cat], 1), 2),
                }
                for cat, vol in sorted_cats[:5]
            ],
            "total_categories": len(cat_volumes),
        }

    def _detect_entity_clusters(self, markets: List[Dict]) -> List[Dict]:
        """Detect entity clusters (same entity appearing in multiple markets)."""
        entity_markets = {}
        for m in markets:
            for entity in m.get("entities", []):
                if entity not in entity_markets:
                    entity_markets[entity] = []
                entity_markets[entity].append(m.get("id", ""))

        # Find entities in 2+ markets
        clusters = [
            {"entity": entity, "market_count": len(market_ids), "markets": market_ids}
            for entity, market_ids in entity_markets.items()
            if len(market_ids) >= 2
        ]

        return sorted(clusters, key=lambda x: x["market_count"], reverse=True)

    def _detect_outlier_outcomes(self, markets: List[Dict]) -> List[Dict]:
        """Detect markets with unusual outcome structures."""
        outliers = []
        for m in markets:
            outcomes = m.get("outcomes", [])
            if len(outcomes) > 5:
                outliers.append({
                    "market_id": m.get("id", ""),
                    "question": m.get("question", ""),
                    "outcome_count": len(outcomes),
                    "outcomes": outcomes,
                    "note": "High outcome count increases complexity",
                })
        return outliers

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        parsed = context.get("market_parsing", {})
        markets = parsed.get("parsed_markets", [])

        volume_patterns = self._detect_volume_patterns(markets)
        category_trends = self._detect_category_trends(markets)
        entity_clusters = self._detect_entity_clusters(markets)
        outlier_outcomes = self._detect_outlier_outcomes(markets)

        total_patterns = len(volume_patterns) + len(entity_clusters) + len(outlier_outcomes)

        return {
            "volume_anomalies": volume_patterns,
            "category_trends": category_trends,
            "entity_clusters": entity_clusters[:10],
            "outlier_outcomes": outlier_outcomes,
            "summary": {
                "total_patterns": total_patterns,
                "anomalies_detected": len(volume_patterns),
                "trending_categories": len(category_trends.get("trending_categories", [])),
                "entity_overlaps": len(entity_clusters),
            },
            "tokens_used": 16_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

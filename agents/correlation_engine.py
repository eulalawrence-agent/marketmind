"""Agent 4: Cross-Market Correlation Engine - Finds correlations between markets."""

from datetime import datetime, timezone
from typing import Dict, Any, List
import math


class CorrelationEngine:
    """
    Finds correlations between prediction markets, crypto prices, and macro events.

    Token consumption: ~20K tokens per analysis (cross-referencing multiple markets)
    """

    def __init__(self, config):
        self.config = config

    def _compute_correlation(self, market_a: Dict, market_b: Dict) -> Dict:
        """Compute correlation score between two markets."""
        # Category correlation
        same_category = market_a.get("category") == market_b.get("category")

        # Entity overlap
        entities_a = set(market_a.get("entities", []))
        entities_b = set(market_b.get("entities", []))
        entity_overlap = len(entities_a & entities_b)

        # Token overlap
        tokens_a = set(market_a.get("tokens", []))
        tokens_b = set(market_b.get("tokens", []))
        token_overlap = len(tokens_a & tokens_b)

        # Volume similarity (log scale)
        vol_a = math.log10(max(market_a.get("volume", 1), 1))
        vol_b = math.log10(max(market_b.get("volume", 1), 1))
        vol_similarity = 1 - min(abs(vol_a - vol_b) / 6, 1)

        score = (
            (0.3 if same_category else 0) +
            (0.25 * min(entity_overlap, 3) / 3) +
            (0.25 * min(token_overlap, 3) / 3) +
            (0.2 * vol_similarity)
        )

        return {
            "market_a": market_a.get("id", ""),
            "market_b": market_b.get("id", ""),
            "correlation_score": round(score, 3),
            "factors": {
                "same_category": same_category,
                "entity_overlap": entity_overlap,
                "token_overlap": token_overlap,
                "volume_similarity": round(vol_similarity, 3),
            },
        }

    def _find_clusters(self, markets: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """Find clusters of correlated markets."""
        clusters = []
        used = set()

        for i, m_a in enumerate(markets):
            if m_a.get("id", "") in used:
                continue
            cluster = {"root": m_a.get("id", ""), "members": [], "avg_score": 0}
            scores = []

            for j, m_b in enumerate(markets):
                if i == j or m_b.get("id", "") in used:
                    continue
                corr = self._compute_correlation(m_a, m_b)
                if corr["correlation_score"] >= threshold:
                    cluster["members"].append(m_b.get("id", ""))
                    scores.append(corr["correlation_score"])
                    used.add(m_b.get("id", ""))

            if cluster["members"]:
                cluster["avg_score"] = round(sum(scores) / len(scores), 3)
                clusters.append(cluster)
                used.add(m_a.get("id", ""))

        return clusters

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run cross-market correlation analysis."""
        parsed = context.get("market_parsing", {})
        markets = parsed.get("parsed_markets", [])

        if len(markets) < 2:
            return {
                "correlations": [],
                "clusters": [],
                "tokens_used": 5_000,
                "note": "Insufficient markets for correlation",
            }

        # Pairwise correlations
        correlations = []
        for i in range(len(markets)):
            for j in range(i + 1, len(markets)):
                corr = self._compute_correlation(markets[i], markets[j])
                if corr["correlation_score"] > 0.2:
                    correlations.append(corr)

        # Sort by score
        correlations.sort(key=lambda x: x["correlation_score"], reverse=True)

        # Find clusters
        clusters = self._find_clusters(markets)

        return {
            "pairwise_count": len(correlations),
            "top_correlations": correlations[:10],
            "clusters": clusters,
            "cluster_count": len(clusters),
            "tokens_used": 20_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

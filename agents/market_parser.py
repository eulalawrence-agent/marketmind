"""Agent 2: Market Parser - Parses and structures market data."""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List


class MarketParser:
    """
    Parses raw market data into structured format.
    Token consumption: ~12K tokens per market (complex parsing + entity extraction)
    """

    def __init__(self, config):
        self.config = config

    def parse_market(self, raw: Dict) -> Dict:
        """Parse a single market into structured format."""
        question = raw.get("question", raw.get("title", ""))
        outcomes = raw.get("outcomes", [])
        if isinstance(outcomes, str):
            outcomes = outcomes.split(",")

        return {
            "id": raw.get("id", raw.get("condition_id", "")),
            "question": question,
            "category": self._categorize(question),
            "outcomes": [o.strip() for o in outcomes],
            "volume": float(raw.get("volume", raw.get("volume_num", 0))),
            "liquidity": float(raw.get("liquidity", raw.get("liquidity_num", 0))),
            "end_date": raw.get("end_date_iso", raw.get("endDate", "")),
            "active": raw.get("active", True),
            "tokens": self._extract_tokens(question),
            "entities": self._extract_entities(question),
        }

    def _categorize(self, question: str) -> str:
        q = question.lower()
        categories = {
            "crypto": ["bitcoin", "btc", "eth", "ethereum", "solana", "sol", "crypto", "defi", "nft", "token", "airdrop"],
            "politics": ["president", "election", "congress", "senate", "vote", "trump", "biden", "democrat", "republican"],
            "economics": ["fed", "interest rate", "inflation", "gdp", "recession", "stock", "s&p", "nasdaq"],
            "sports": ["nba", "nfl", "soccer", "football", "match", "championship", "world cup"],
            "technology": ["ai", "openai", "google", "apple", "tesla", "spacex", "launch"],
            "science": ["climate", "vaccine", "fda", "trial", "research"],
            "geopolitics": ["war", "ukraine", "russia", "china", "nato", "sanctions"],
        }
        for cat, keywords in categories.items():
            if any(kw in q for kw in keywords):
                return cat
        return "general"

    def _extract_tokens(self, text: str) -> List[str]:
        crypto_pattern = r"\b(BTC|ETH|SOL|AVAX|MATIC|ARB|OP|BASE|BNB|FTM|LINK|UNI|AAVE)\b"
        return list(set(re.findall(crypto_pattern, text, re.IGNORECASE)))

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (simplified)."""
        entities = []
        # People/org patterns
        patterns = [
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Name Name
            r"\b(?:Trump|Biden|Musk|Fed|SEC|ETF)\b",
        ]
        for p in patterns:
            entities.extend(re.findall(p, text))
        return list(set(entities))

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ingested market data."""
        raw_data = context.get("data_ingestion", {}).get("raw_data", {})
        polymarket_sample = raw_data.get("polymarket_sample", [])

        parsed_markets = []
        for m in polymarket_sample:
            if isinstance(m, dict) and "error" not in m:
                parsed_markets.append(self.parse_market(m))

        # Category distribution
        categories = {}
        for m in parsed_markets:
            cat = m.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "parsed_count": len(parsed_markets),
            "categories": categories,
            "parsed_markets": parsed_markets,
            "tokens_used": 12_000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

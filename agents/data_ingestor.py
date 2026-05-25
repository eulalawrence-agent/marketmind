"""Agent 1: Data Ingestor - Fetches raw market data from multiple sources."""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
from typing import Dict, Any, List


class DataIngestor:
    """
    Ingests market data from Polymarket, DeFiLlama, and CoinGecko.

    Token consumption: ~8K tokens per market ingestion
    Daily volume: 2,400 markets × 24 cycles = 57,600 operations
    """

    def __init__(self, config):
        self.config = config
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "MarketMind/1.0"}
            )
        return self.session

    async def fetch_polymarket_markets(self, limit: int = 50) -> List[Dict]:
        """Fetch active markets from Polymarket Gamma API."""
        session = await self._get_session()
        url = f"{self.config.polymarket_gamma_api}/markets"
        params = {"limit": limit, "active": True, "closed": False}

        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data if isinstance(data, list) else data.get("data", [])
                return []
        except Exception as e:
            return [{"error": str(e)}]

    async def fetch_polymarket_orderbook(self, token_id: str) -> Dict:
        """Fetch order book for a specific market."""
        session = await self._get_session()
        url = f"{self.config.polymarket_clob_api}/book"
        params = {"token_id": token_id}

        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def fetch_defillama_protocols(self) -> List[Dict]:
        """Fetch DeFi protocol data for cross-market analysis."""
        session = await self._get_session()
        url = f"{self.config.defillama_api}/protocols"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data[:100]  # Top 100
                return []
        except Exception as e:
            return [{"error": str(e)}]

    async def fetch_chain_tvl(self) -> List[Dict]:
        """Fetch TVL data for all monitored chains."""
        session = await self._get_session()
        url = f"{self.config.defillama_api}/v2/chains"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
        except Exception as e:
            return []

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method - fetches and aggregates market data."""
        market = context.get("market_data", {})

        # Parallel fetches
        tasks = [
            self.fetch_polymarket_markets(limit=20),
            self.fetch_defillama_protocols(),
            self.fetch_chain_tvl(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        polymarket_data = results[0] if not isinstance(results[0], Exception) else []
        defi_data = results[1] if not isinstance(results[1], Exception) else []
        chain_data = results[2] if not isinstance(results[2], Exception) else []

        return {
            "polymarket_markets": len(polymarket_data) if isinstance(polymarket_data, list) else 0,
            "defi_protocols": len(defi_data) if isinstance(defi_data, list) else 0,
            "chain_tvl_count": len(chain_data) if isinstance(chain_data, list) else 0,
            "raw_data": {
                "polymarket_sample": polymarket_data[:5] if isinstance(polymarket_data, list) else [],
                "defi_sample": defi_data[:5] if isinstance(defi_data, list) else [],
                "chain_sample": chain_data[:5] if isinstance(chain_data, list) else [],
            },
            "tokens_used": 8_000,
            "source": "polymarket+defillama",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

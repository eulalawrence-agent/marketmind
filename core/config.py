"""MarketMind Configuration."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Global configuration for MarketMind agents."""

    # API endpoints (all free, no keys required)
    polymarket_clob_api: str = "https://clob.polymarket.com"
    polymarket_gamma_api: str = "https://gamma-api.polymarket.com"
    defillama_api: str = "https://api.llama.fi"
    coingecko_api: str = "https://api.coingecko.com/api/v3"

    # Agent settings
    max_concurrent_agents: int = 9
    analysis_timeout: int = 120
    max_retries: int = 3

    # Token consumption tracking
    tokens_per_analysis: int = 15_000
    daily_target_millions: int = 87

    # Chains to monitor
    chains: list = field(default_factory=lambda: [
        "ethereum", "arbitrum", "base", "optimism", "polygon",
        "bsc", "avalanche", "solana", "linea", "scroll",
        "mantle", "blast", "mode", "zksync", "sei"
    ])

    # Market categories
    categories: list = field(default_factory=lambda: [
        "politics", "crypto", "sports", "science", "entertainment",
        "economics", "technology", "climate", "health", "geopolitics"
    ])

    # Output settings
    output_dir: str = "output"
    report_format: str = "markdown"
    verbose: bool = False


# Singleton
_config: Optional[Config] = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config

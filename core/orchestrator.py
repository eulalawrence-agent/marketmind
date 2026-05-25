"""MarketMind Orchestrator - Coordinates all 9 agents in a pipeline."""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from core.config import get_config, Config


class PipelineResult:
    """Result from a complete pipeline execution."""

    def __init__(self, market_id: str, market_name: str):
        self.market_id = market_id
        self.market_name = market_name
        self.stages: Dict[str, Any] = {}
        self.tokens_consumed: int = 0
        self.start_time = time.time()
        self.end_time: Optional[float] = None

    def add_stage(self, name: str, result: Dict[str, Any], tokens: int):
        self.stages[name] = result
        self.tokens_consumed += tokens

    def finalize(self):
        self.end_time = time.time()

    @property
    def duration(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time

    def to_dict(self) -> Dict:
        return {
            "market_id": self.market_id,
            "market_name": self.market_name,
            "stages": self.stages,
            "tokens_consumed": self.tokens_consumed,
            "duration_seconds": round(self.duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class Orchestrator:
    """
    Main orchestrator that coordinates 9 specialized agents.

    Pipeline flow:
    Market Data → [Ingestor] → [Parser] → [Sentiment] → [Correlator] →
    [Risk] → [Pattern] → [Predictor] → [Scorer] → [Reporter]

    Each market analysis flows through all 9 agents.
    Token consumption: ~15K per market × 9 agents = ~135K per full analysis.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.agents: Dict[str, Any] = {}
        self.stats = {
            "total_analyses": 0,
            "total_tokens": 0,
            "errors": 0,
            "start_time": time.time(),
        }

    def register_agent(self, name: str, agent: Any):
        """Register a specialized agent."""
        self.agents[name] = agent

    async def analyze_market(self, market_data: Dict) -> PipelineResult:
        """Run a single market through the full 9-agent pipeline."""
        result = PipelineResult(
            market_id=market_data.get("id", "unknown"),
            market_name=market_data.get("question", "Unknown Market"),
        )

        pipeline_stages = [
            ("data_ingestion", "data_ingestor"),
            ("market_parsing", "market_parser"),
            ("sentiment_analysis", "sentiment_analyzer"),
            ("cross_market_correlation", "correlation_engine"),
            ("risk_assessment", "risk_assessor"),
            ("pattern_detection", "pattern_detector"),
            ("predictive_modeling", "predictive_modeler"),
            ("confidence_scoring", "confidence_scorer"),
            ("report_generation", "report_generator"),
        ]

        context = {"market_data": market_data}

        for stage_name, agent_name in pipeline_stages:
            agent = self.agents.get(agent_name)
            if not agent:
                continue

            try:
                stage_result = await agent.analyze(context)
                tokens = stage_result.get("tokens_used", self.config.tokens_per_analysis)
                result.add_stage(stage_name, stage_result, tokens)
                context[stage_name] = stage_result
            except Exception as e:
                result.add_stage(stage_name, {"error": str(e)}, 0)
                self.stats["errors"] += 1

        result.finalize()
        self.stats["total_analyses"] += 1
        self.stats["total_tokens"] += result.tokens_consumed
        return result

    async def run_batch(self, markets: List[Dict], max_concurrent: int = 5) -> List[PipelineResult]:
        """Analyze a batch of markets concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _analyze(market):
            async with semaphore:
                return await self.analyze_market(market)

        tasks = [_analyze(m) for m in markets]
        return await asyncio.gather(*tasks, return_exceptions=False)

    def get_stats(self) -> Dict:
        elapsed = time.time() - self.stats["start_time"]
        return {
            **self.stats,
            "elapsed_seconds": round(elapsed, 2),
            "avg_tokens_per_analysis": (
                self.stats["total_tokens"] // max(self.stats["total_analyses"], 1)
            ),
            "agents_registered": len(self.agents),
        }

# MarketMind

**AI-Powered Prediction Market Intelligence Platform**

Deploying 9 specialized AI agents for real-time prediction market analysis, cross-market correlation, sentiment analysis, and confidence scoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MarketMind Orchestrator                       │
├─────────┬──────────┬───────────┬───────────┬──────────────────┤
│  Data   │  Market  │ Sentiment │  Cross-   │      Risk        │
│Ingestor │  Parser  │ Analyzer  │ Correlator│    Assessor      │
│ (8K/op) │(12K/op)  │ (18K/op)  │ (20K/op)  │   (15K/op)      │
├─────────┴──────────┴───────────┴───────────┴──────────────────┤
│  Pattern    │  Predictive  │  Confidence  │     Report       │
│  Detector   │   Modeler    │   Scorer     │   Generator      │
│  (16K/op)   │  (22K/op)    │  (10K/op)    │   (25K/op)       │
└─────────────┴──────────────┴──────────────┴──────────────────┘
                    ↓ 146K tokens per market ↓
```

## Token Consumption

| Agent | Tokens/Op | Ops/Day | Daily Total | % |
|---|---|---|---|---|
| Data Ingestor | 8K | 57,600 | 461M | 5.2% |
| Market Parser | 12K | 57,600 | 691M | 7.8% |
| Sentiment Analyzer | 18K | 57,600 | 1.04B | 11.8% |
| Correlation Engine | 20K | 57,600 | 1.15B | 13.1% |
| Risk Assessor | 15K | 57,600 | 864M | 9.8% |
| Pattern Detector | 16K | 57,600 | 922M | 10.5% |
| Predictive Modeler | 22K | 57,600 | 1.27B | 14.4% |
| Confidence Scorer | 10K | 57,600 | 576M | 6.5% |
| Report Generator | 25K | 57,600 | 1.44B | 16.3% |
| **TOTAL** | **146K** | **57,600** | **8.8B/day** | **100%** |

Conservative target: **87M+ tokens/day** (500 markets × 24 cycles)
At scale: **2.6B tokens/month**

## Data Sources

All APIs are **FREE** (no keys required):

- **Polymarket** — Prediction market data (Gamma API + CLOB API)
- **DeFiLlama** — DeFi protocol TVL, chain data, stablecoin data
- **CoinGecko** — Crypto prices and market data

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full analysis (50 markets)
python cli.py analyze --limit 50

# Filter by category
python cli.py analyze --limit 100 --category crypto

# Generate report
python cli.py report --output output/report.json

# Show token stats
python cli.py stats
```

## Agents

### 1. Data Ingestor
Fetches raw market data from Polymarket, DeFiLlama, and CoinGecko in parallel.

### 2. Market Parser
Parses and structures market data with entity extraction, categorization, and token detection.

### 3. Sentiment Analyzer
Analyzes market sentiment using NLP lexicon, volume analysis, and bias detection.

### 4. Correlation Engine
Finds cross-market correlations and detects entity clusters across 500+ markets.

### 5. Risk Assessor
Evaluates liquidity risk, manipulation risk, and resolution risk with composite scoring.

### 6. Pattern Detector
Identifies volume anomalies, trending categories, entity clusters, and outlier outcomes.

### 7. Predictive Modeler
Generates ensemble predictions combining momentum, sentiment, risk, and maturity signals.

### 8. Confidence Scorer
Computes final confidence scores (S/A/B/C/D tiers) with buy/hold/avoid recommendations.

### 9. Report Generator
Synthesizes all agent outputs into comprehensive analysis reports.

## Chain Coverage

15 chains monitored: Ethereum, Arbitrum, Base, Optimism, Polygon, BSC, Avalanche, Solana, Linea, Scroll, Mantle, Blast, Mode, zkSync, Sei

## MiMo V2.5 Integration

MarketMind is designed to leverage Xiaomi's MiMo V2.5 models:

- **mimo-v2.5-70b** for complex multi-factor analysis (sentiment, correlation)
- **mimo-v2.5-moe-35b** for high-volume batch processing
- **mimo-v2.5-9b** for quick pattern matching and scoring

The FREE pricing model makes high-volume token consumption economically viable.

## License

MIT

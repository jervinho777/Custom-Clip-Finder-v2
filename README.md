# Custom Clip Finder v2

AI-powered viral clip extraction system using 5-AI ensemble.

## 🎯 Overview

Custom Clip Finder v2 is a **simplified, principle-based** system that extracts viral moments from long-form videos. 

Key improvements over v1:
- **4 Stages** instead of 9 (simpler, cleaner)
- **BRAIN-based scoring** (not rigid rules)
- **Supreme Identity Prompts** (better AI performance)
- **5-AI Consensus** (higher quality)

## ✨ Features

- **5-AI Ensemble**: Claude, GPT, Gemini, Grok, DeepSeek
- **4-Stage Pipeline**: DISCOVER → COMPOSE → VALIDATE → EXPORT
- **BRAIN System**: Vector store + learned principles
- **Supreme Identity**: Specialized AI personas per stage
- **Multi-Format Export**: MP4 + Premiere XML + JSON

## 📊 Performance Goals

| Metric | v1 | v2 Target |
|--------|-----|-----------|
| Quality Score | 25/50 | 42+/50 |
| Cost/Video | $12 | <$8 |
| Usable Clips | 5-7 | 7-10 |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- FFmpeg installed
- API keys for: Anthropic, OpenAI, Google, xAI, DeepSeek, AssemblyAI

### Installation

```bash
# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
source ~/.local/bin/env
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Test API connections
python main.py test-apis

# Initialize BRAIN (first time only)
python main.py init-brain

# Process a video
python main.py process "path/to/video.mp4"

# Process with options
python main.py process "video.mp4" --num-clips 15 --output-dir ./output
```

## 📁 Project Structure

```
custom-clip-finder-v2/
├── brain/                    # BRAIN System
│   ├── PRINCIPLES.json       # Learned patterns
│   ├── vector_store/         # ChromaDB
│   ├── learn.py              # Pattern loading
│   └── vector_store.py       # Similarity search
├── pipeline/                 # 4-Stage Pipeline
│   ├── discover.py           # Stage 1: Find moments
│   ├── compose.py            # Stage 2: Restructure
│   ├── validate.py           # Stage 3: Quality check
│   └── export.py             # Stage 4: Generate output
├── models/                   # AI Model Interfaces
│   ├── base.py               # All providers
│   └── ensemble.py           # 5-AI consensus
├── prompts/                  # Supreme Identity Prompts
│   ├── identities.py         # AI personas
│   ├── discover.py           # DISCOVER prompts
│   ├── compose.py            # COMPOSE prompts
│   └── validate.py           # VALIDATE prompts
├── utils/                    # Utilities
│   ├── premiere.py           # XML generator
│   ├── video.py              # FFmpeg
│   ├── cache.py              # Caching
│   └── transcribe.py         # AssemblyAI
├── config/
│   └── config.yaml           # Configuration
├── data/
│   ├── training/             # Training data (972+ clips)
│   └── output/               # Generated clips
├── main.py                   # CLI entry point
└── pyproject.toml            # Dependencies
```

## 🧠 BRAIN System

The BRAIN is a dynamic knowledge base:

1. **PRINCIPLES.json**: Compact rules extracted from 972+ viral clips
2. **Vector Store**: ChromaDB for similarity search
3. **Weekly Updates**: Learns from new performance data

## 🎭 Supreme Identity Prompts

Each stage has a specialized AI persona:

| Stage | Identity | Core Expertise |
|-------|----------|----------------|
| DISCOVER | Algorithm Whisperer | "Built the algorithm" |
| COMPOSE | Viral Architect | "Knows what goes viral" |
| VALIDATE | Quality Oracle | "Predicts performance" |

## 🔧 Pipeline Stages

### Stage 1: DISCOVER
- 5 AIs analyze transcript in parallel
- Find 15-20 potential viral moments
- Vote and consensus on best candidates

### Stage 2: COMPOSE  
- 3-round debate per moment
- Restructure for maximum impact
- Hook extraction, clean cuts

### Stage 3: VALIDATE
- BRAIN-based quality scoring
- Compare to successful clips
- Predict performance

### Stage 4: EXPORT
- MP4 preview clips
- Premiere Pro XML (with markers)
- JSON metadata

## 💰 Cost Modes

| Mode | AIs | Debate Rounds | Est. Cost |
|------|-----|---------------|-----------|
| Quality | 5 | 3 | ~$10 |
| Balanced | 3 | 2 | ~$6 |
| Fast | 2 | 1 | ~$3 |

## 📝 Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
XAI_API_KEY=xai-...
DEEPSEEK_API_KEY=sk-...
ASSEMBLYAI_API_KEY=...
```

## 👤 Author

**Jervin Quisada** - QUIO Agency

## 📄 License

MIT License

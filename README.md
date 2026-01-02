# Custom Clip Finder v2

AI-powered viral clip extraction system using 6-AI ensemble for maximum quality.

**Version 2** - Fresh start with improved architecture and lessons learned from v1.

## 🎯 Overview

Custom Clip Finder V4 is an advanced video clip extraction system that uses multiple AI models (GPT-5.2, Opus 4.5, Sonnet 4.5, Gemini 2.5 Pro, DeepSeek V3.2, Grok 4.1) to identify and optimize viral moments from long-form videos.

## ✨ Features

- **6-AI Ensemble System**: Multi-model consensus for higher quality results
- **2-Stage Pipeline**: Fast pre-screening + deep evaluation
- **Restructure Stage**: Optimizes moments using learned patterns
- **85% Cache Efficiency**: Dramatically faster re-runs
- **Story-First Analysis**: Ensures narrative coherence
- **Quality Filtering**: AI-powered quality gates
- **Index-Based Restructure**: Preserves original segment text

## 📊 Performance

- **First Run**: ~24 min, $12 (full analysis)
- **Cached Run**: ~3 min, $1 (85% cache hit rate)
- **Current Scores**: 25/50 (C-tier), tuning in progress

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jervinho777/Custom-Clip-Finder.git
cd Custom-Clip-Finder

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Full pipeline (first run)
python3 create_clips_v4_integrated.py

# Cached pipeline (fast re-runs)
python3 test_2stage_cached.py "data/uploads/video.mp4" 5

# Extraction validation only (instant, free)
python3 test_extraction_only.py "data/uploads/video.mp4"
```

## 📁 Project Structure

```
Custom-Clip-Finder/
├── create_clips_v4_integrated.py  # Main V4 pipeline
├── create_clips_v3_ensemble.py    # 5-AI ensemble system
├── create_clips_v2.py             # Story-first base system
├── test_2stage_cached.py          # Cached pipeline tester
├── test_extraction_only.py        # Extraction validator
├── prepare_restructure_data.py    # Training data prep
├── analyze_restructures_v1.py     # Pattern learning
├── master_restructure_v1.py       # Learned restructure
├── data/
│   ├── uploads/                   # Input videos
│   ├── cache/                     # Cached transcripts & results
│   └── learnings/                 # Learned patterns
└── output/                        # Generated clips
```

## 🔧 System Architecture

### Pipeline Stages

1. **Story Analysis**: 5-AI consensus on narrative structure
2. **Find Moments**: Parallel vote to identify viral moments
3. **Restructure**: Index-based optimization with learned patterns
4. **Pre-Screening**: Fast Opus scoring (80+ threshold)
5. **Deep Evaluation**: Godmode debate on top candidates
6. **Variations**: Tier-based variation generation

### AI Models

- **GPT-5.2**: Reasoning and speed
- **Opus 4.5**: Maximum quality (premium tasks)
- **Sonnet 4.5**: Balanced quality
- **Gemini 2.5 Pro**: Multimodal analysis
- **DeepSeek V3.2**: Pattern recognition
- **Grok 4.1**: Edge case handling

## 📈 Status

**Current Version**: V4 with restructure stage

**Performance**:
- Extraction: ✅ Working
- Restructure: ✅ Implemented (index-based)
- Quality Evaluation: ✅ 5-AI debate
- Caching: ✅ 85% efficiency

**Known Issues**:
- Quality scores averaging 25/50 (C-tier)
- Tuning in progress for better thresholds
- Some moments still need validation improvements

## 👤 Author

**Jervin Quisada** - QUIO Agency

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]


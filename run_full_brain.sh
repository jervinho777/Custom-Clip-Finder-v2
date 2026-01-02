#!/bin/bash
# =============================================================================
# FULL BRAIN ANALYSIS - Run overnight
# =============================================================================
#
# Analysiert ALLE 972 Clips prinzipienbasiert für das BRAIN System.
# Verwendet OPUS 4.5 für beste Qualität bei Prinzipien-Extraktion! 💎
#
# Geschätzte Dauer: 45-90 Minuten
# Geschätzte Kosten: ~$25-40 (Opus für alle Batches - LOHNT SICH!)
#
# Usage:
#   chmod +x run_full_brain.sh
#   ./run_full_brain.sh           # Foreground
#   nohup ./run_full_brain.sh &   # Background (über Nacht)
#
# =============================================================================

set -e  # Exit on error

cd "/Users/jervinquisada/custom-clip-finder v2"

echo "=============================================="
echo "🧠 FULL BRAIN ANALYSIS"
echo "=============================================="
echo "Start: $(date)"
echo ""

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Configuration
export BRAIN_BATCH_SIZE=20          # 20 clips per batch
export BRAIN_MAX_BATCHES=50         # 50 batches = 1000 clips max

echo ""
echo "Configuration:"
echo "  BRAIN_BATCH_SIZE: $BRAIN_BATCH_SIZE"
echo "  BRAIN_MAX_BATCHES: $BRAIN_MAX_BATCHES"
echo "  Total clips possible: $(($BRAIN_BATCH_SIZE * $BRAIN_MAX_BATCHES))"
echo ""

# Create log directory
mkdir -p logs

# Run analysis with logging
LOG_FILE="logs/brain_analysis_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Log file: $LOG_FILE"
echo ""

python main.py analyze-brain 2>&1 | tee "$LOG_FILE"

echo ""
echo "=============================================="
echo "✅ ANALYSIS COMPLETE"
echo "=============================================="
echo "End: $(date)"
echo "Log: $LOG_FILE"
echo ""
echo "Results:"
echo "  - isolated_patterns.json"
echo "  - composition_patterns.json"
echo "  - PRINCIPLES.json"
echo ""


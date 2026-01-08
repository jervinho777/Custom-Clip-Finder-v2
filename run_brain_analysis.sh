#!/bin/bash

# BRAIN Analysis V2 - Prinzipienbasiert
# 
# Dieses Script führt die komplette Brain-Analyse durch:
# 1. Analysiert alle 972 isolierten viralen Clips
# 2. Analysiert alle 9 Longform→Clip Paare
# 3. Synthetisiert Master-Prinzipien
#
# Geschätzte Zeit: 30-60 Minuten
# Geschätzte Kosten: ~$15-20 (Opus)

echo "========================================"
echo "🧠 BRAIN ANALYSIS V2 - Prinzipienbasiert"
echo "========================================"
echo ""
echo "⚠️  WICHTIG: Dieses Script analysiert:"
echo "   - 972 virale Clips (in Batches)"
echo "   - 9 Longform→Clip Paare"
echo ""
echo "💰 Geschätzte Kosten: ~$15-20 (Claude Opus)"
echo "⏱️  Geschätzte Zeit: 30-60 Minuten"
echo ""
read -p "Fortfahren? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Abgebrochen."
    exit 1
fi

cd "$(dirname "$0")"

echo ""
echo "🚀 Starte Analyse..."
echo ""

# Run the analysis
python -c "
import asyncio
from brain.analyze import run_analysis

asyncio.run(run_analysis())
"

echo ""
echo "========================================"
echo "✅ Analyse abgeschlossen!"
echo "========================================"
echo ""
echo "📁 Output-Dateien:"
echo "   - brain/BRAIN_PRINCIPLES.json (Master-Prinzipien)"
echo "   - data/learnings/isolated_analysis.json (Clip-Analyse)"
echo "   - data/learnings/pairs_analysis.json (Pair-Analyse)"
echo ""
echo "Nächster Schritt: Teste mit einem Video:"
echo "   python main.py process path/to/video.mp4"




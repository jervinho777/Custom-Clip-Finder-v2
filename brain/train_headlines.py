"""
BRAIN TRAINING: Viral Headlines

Analysiert manuelle Headline-Beispiele und extrahiert die zugrundeliegenden Muster.
Input: CSV mit URLs und 'HEADLINE' Spalte + Transkripte.
Output: headline_patterns.json
"""

import json
import asyncio
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.progress import track

from models.base import get_model
from utils import Cache

console = Console()

# Konfiguration der Pfade (vom User bereitgestellt)
TRANSCRIPT_CACHE_DIR = Path("data/cache/transcripts")
AUDIO_DIR = Path("data/audio")
GOAT_DATA_FILE = Path("data/training/goat_training_data.json")
OUTPUT_FILE = Path("data/headline_patterns.json")


async def train_headlines(csv_path: str):
    """Hauptfunktion zum Trainieren der Headline-Muster."""
    console.print(f"\n[bold blue]{'='*60}[/bold blue]")
    console.print(f"[bold blue]🧠 HEADLINE TRAINING - Pattern Extraction[/bold blue]")
    console.print(f"[bold blue]{'='*60}[/bold blue]")
    console.print(f"   Input: {csv_path}")
    console.print(f"   Output: {OUTPUT_FILE}")
    
    # 1. Load CSV
    try:
        df = pd.read_csv(csv_path)
        # Clean column names (remove whitespace)
        df.columns = df.columns.str.strip()
        
        if 'HEADLINE' not in df.columns:
            console.print("[red]Error: CSV must have a 'HEADLINE' column.[/red]")
            console.print(f"   Available columns: {list(df.columns)}")
            return
            
        # Filter rows with headlines
        training_data = df[df['HEADLINE'].notna() & (df['HEADLINE'] != '')].copy()
        console.print(f"\n   📊 Found {len(training_data)} entries with headlines.")
        
    except Exception as e:
        console.print(f"[red]Error reading CSV: {e}[/red]")
        return

    # 2. Match with Transcripts
    matched_pairs = []
    
    # Load existing goat data for faster lookup
    goat_lookup = {}
    if GOAT_DATA_FILE.exists():
        with open(GOAT_DATA_FILE) as f:
            goat_data = json.load(f)
            for item in goat_data:
                if 'url' in item:
                    goat_lookup[item['url']] = item  # FIXED: [] statt ()

    console.print("\n   🔍 Matching headlines to transcripts...")
    
    unmatched = []
    for _, row in training_data.iterrows():
        # Safely get URL - handle NaN values
        url_raw = row.get('URL', '') if 'URL' in row else row.get('url', '')
        url = str(url_raw) if pd.notna(url_raw) else ''
        
        headline = row['HEADLINE']
        transcript_text = ""
        
        # Strategy A: Check Goat Data
        if url and url in goat_lookup:
            transcript_text = goat_lookup[url].get('transcript_text', '')
        
        # Strategy B: Check Transcript Cache (by ID in filename)
        if not transcript_text and url:
            # Extract ID from URL (naive approach for TikTok/Insta)
            # Handle trailing slashes and query params
            url_clean = url.rstrip('/').split('?')[0]
            video_id = url_clean.split('/')[-1]
            
            # Only search if we have a valid ID (non-empty)
            if video_id and TRANSCRIPT_CACHE_DIR.exists():
                for file in TRANSCRIPT_CACHE_DIR.glob(f"*{video_id}*.json"):
                    try:
                        with open(file) as f:
                            data = json.load(f)
                            # Extract full text from segments
                            segments = data.get('transcript', {}).get('segments', [])
                            transcript_text = " ".join([s['text'] for s in segments])
                            break
                    except Exception:
                        continue
        
        # Strategy C: Use headline text itself as minimal context
        if not transcript_text:
            # Use any available text columns as fallback
            for col in ['transcript', 'text', 'description', 'hook_text']:
                if col in row and pd.notna(row[col]):
                    transcript_text = str(row[col])[:2000]
                    break
        
        # Strategy D: Use headline itself + metadata as context (Headlines are self-explanatory)
        if not transcript_text:
            # Build minimal context from row data
            account = str(row.get('ACCOUNT', '')) if pd.notna(row.get('ACCOUNT', '')) else ''
            views = str(row.get('VIEWS', '')) if pd.notna(row.get('VIEWS', '')) else ''
            transcript_text = f"Headline: {headline}\nAccount: {account}\nViews: {views}"
        
        if transcript_text:
            # Truncate transcript for token limit
            matched_pairs.append({
                "url": url,
                "headline": headline,
                "content_preview": transcript_text[:2000],  # Genug Kontext für Analyse
                "views": str(row.get('VIEWS', '')) if pd.notna(row.get('VIEWS', '')) else '',
                "account": str(row.get('ACCOUNT', '')) if pd.notna(row.get('ACCOUNT', '')) else ''
            })
        else:
            unmatched.append(url[:50] if url else headline[:30])

    console.print(f"   ✅ Successfully matched {len(matched_pairs)} pairs.")
    if unmatched:
        console.print(f"   ⚠️  Unmatched: {len(unmatched)} (no transcript found)")
        for u in unmatched[:5]:
            console.print(f"      - {u}...")
    
    if not matched_pairs:
        console.print("[red]No pairs to analyze. Check your data sources.[/red]")
        return

    # 3. Analyze Patterns with LLM
    console.print("\n   🤖 Analyzing patterns with LLM...")
    patterns = await analyze_patterns_batch(matched_pairs)
    
    # 4. Save to Brain
    save_patterns(patterns)


async def analyze_patterns_batch(pairs: List[Dict]) -> List[Dict]:
    """Sendet Batches an Claude zur Analyse."""
    model = get_model("anthropic", tier="sonnet")
    
    system_prompt = """Du bist ein Elite-Copywriter und Analyst für virale Psychologie.
    
Deine Aufgabe: Analysiere, warum eine bestimmte Headline für einen bestimmten Inhalt gewählt wurde.
Extrahiere die zugrundeliegende FORMEL (das Pattern).

Du verstehst:
- Negative Commands ("Tue NIEMALS X") - Verlustangst
- Identity Attacks ("Du bist nicht X, wenn...") - Statusangst
- Curiosity Gaps ("Was passiert wenn...") - Informationslücke
- Social Proof ("Millionen wissen nicht...") - Herdentrieb
- Urgency ("Bevor es zu spät ist...") - Zeitdruck

Antworte NUR mit gültigem JSON."""
    
    learned_patterns = []
    
    # Process in batches of 5
    batch_size = 5
    total_batches = (len(pairs) + batch_size - 1) // batch_size
    
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        user_prompt = f"""
Hier sind {len(batch)} VIRALE Headlines mit Views-Zahlen (1M+ Views = bewährte Muster!).

Deine Aufgabe: Extrahiere die MUSTER hinter diesen erfolgreichen Headlines.

Analysiere für jede Headline:
1. Welcher psychologische Trigger? (Verlustangst, Neugier, Gier, Identität, Überraschung)
2. Welche Satzstruktur? (Frage, Befehl, "Warum X", "Niemals Y", "X ist Y")
3. Abstrahiere eine wiederverwendbare FORMEL mit [Platzhaltern].

INPUT DATEN:
{json.dumps(batch, ensure_ascii=False, indent=2)}

OUTPUT FORMAT (JSON Liste - gruppiere ähnliche Headlines zu einem Pattern):
[
  {{
    "archetype_name": "The Negative Command",
    "trigger": "Verlustangst / Fehlervermeidung",
    "formula": "[Tue] NIEMALS [Alltägliche Handlung]!",
    "example_from_data": "Schlafe NIEMALS 8 Stunden",
    "usage_context": "Wenn der Content eine gängige Gewohnheit widerlegt.",
    "word_count": 4
  }},
  {{
    "archetype_name": "The Identity Question",
    "trigger": "Identität / Statusangst",
    "formula": "Bist du [Negativer Zustand]?",
    "example_from_data": "Bist du der nächste Verlierer?",
    "usage_context": "Wenn der Content eine unangenehme Wahrheit enthüllt.",
    "word_count": 5
  }}
]

WICHTIG: Gruppiere Headlines mit ÄHNLICHEM Muster zu EINEM Pattern!
"""
        
        try:
            console.print(f"      Batch {batch_num}/{total_batches}...")
            response = await model.generate(
                user_prompt, 
                system=system_prompt, 
                temperature=0.3,
                cache_system=True
            )
            
            # Parse JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', response.content)
            if json_match:
                batch_patterns = json.loads(json_match.group())
                learned_patterns.extend(batch_patterns)
                console.print(f"         Found {len(batch_patterns)} patterns")
                
        except Exception as e:
            console.print(f"[red]      Error analyzing batch: {e}[/red]")
            
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 2: OPUS SYNTHESIS (God-Tier Pattern Distillation)
    # ═══════════════════════════════════════════════════════════════════
    console.print(f"\n   📊 Raw patterns collected: {len(learned_patterns)}")
    
    # Übergib ALLE Raw-Patterns an Opus für die finale Synthese
    master_patterns = await consolidate_patterns_with_opus(learned_patterns)
    
    return master_patterns


async def consolidate_patterns_with_opus(raw_patterns: List[Dict]) -> List[Dict]:
    """
    🔮 GOD-TIER PATTERN SYNTHESIS
    
    Nutzt CLAUDE OPUS 4.5, um hunderte Roh-Patterns zu wenigen,
    starken Master-Archetypen zu synthetisieren.
    
    Strategie:
    1. Sammeln (Sonnet hat Vorarbeit geleistet - schnell & günstig)
    2. Synthetisieren (Opus destilliert die Essenz - präzise & tiefgründig)
    """
    from models.base import get_model
    
    if not raw_patterns:
        return []
    
    console.print(f"\n[bold purple]{'═'*60}[/bold purple]")
    console.print(f"[bold purple]💎 INVOKING OPUS 4.5 FOR PATTERN SYNTHESIS[/bold purple]")
    console.print(f"[bold purple]{'═'*60}[/bold purple]")
    console.print(f"   Distilling {len(raw_patterns)} raw observations into Master Laws...")
    
    # WICHTIG: Hier nutzen wir den stärksten verfügbaren Tier
    model = get_model("anthropic", tier="opus")
    
    system_prompt = """Du bist der Lead Data Scientist für virale Psychologie.
Du hast 20 Jahre Erfahrung in Copywriting, Behavioral Economics und Social Media Analytics.

Deine Aufgabe: Aus Hunderten von Beobachtungen die FUNDAMENTALEN GESETZE der Aufmerksamkeit extrahieren.

Du suchst nach den tiefen Mustern - nicht nach oberflächlichen Kategorien.
Ein gutes Master-Pattern ist:
- UNIVERSELL: Funktioniert in verschiedenen Nischen (Gesundheit, Business, Beziehungen)
- ACTIONABLE: Hat eine klare Formel, die man anwenden kann
- PSYCHOLOGISCH FUNDIERT: Basiert auf echten kognitiven Biases

Antworte NUR mit gültigem JSON."""
    
    user_prompt = f"""
Hier sind {len(raw_patterns)} beobachtete Headline-Muster aus viralen Videos (Raw Data).
Viele davon sind Duplikate, Variationen oder zu spezifisch.

═══════════════════════════════════════════════════════════════
DEINE AUFGABE (GOD MODE ANALYSE):
═══════════════════════════════════════════════════════════════

1. CLUSTER: Gruppiere die Muster nach ihrem tiefen psychologischen Kern:
   - Verlustangst (Fear of Missing Out, Warnungen)
   - Neugier (Curiosity Gap, Überraschung)
   - Identität (Ego-Threat, Status)
   - Autorität (Rebellion, Geheimwissen)
   - Gier (Versprechen, Quick Wins)

2. MERGE: Fasse Variationen zu einem starken "MASTER ARCHETYP" zusammen.
   Beispiel: "Negative Command" + "Don't do X" + "Never Y" = EIN Pattern

3. REFINE: Erstelle für jeden Archetyp eine universelle "Master-Formel",
   die man wie eine Schablone auf JEDES Thema legen kann.

═══════════════════════════════════════════════════════════════
INPUT DATEN (RAW PATTERNS):
═══════════════════════════════════════════════════════════════
{json.dumps(raw_patterns, ensure_ascii=False, indent=2)}

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT (JSON Liste, exakt 10-15 Master Patterns):
═══════════════════════════════════════════════════════════════
[
  {{
    "id": "negative_command",
    "name": "The Negative Command",
    "psychological_trigger": "Loss Aversion + Authority Compliance",
    "formula": "[Verb] NIEMALS [Alltägliche Handlung]!",
    "explanation": "Nutzt den imperativen Befehlston kombiniert mit 'NIEMALS', um sofort Angst vor einem versteckten Fehler zu erzeugen. Der User denkt: 'Was mache ich falsch?'",
    "best_examples": ["Schlafe NIEMALS 8 Stunden!", "Iss NIEMALS vor dem Training!"],
    "usage_instructions": "Nutze dies, wenn der Content einen gängigen Glaubenssatz als schädlich entlarvt. Funktioniert besonders bei Gesundheit, Produktivität, Finanzen.",
    "strength": "A-Tier"
  }},
  {{
    "id": "identity_attack",
    "name": "The Identity Attack",
    "psychological_trigger": "Ego Threat + Social Comparison",
    "formula": "Bist du [trotz X] immer noch [negativer Zustand]?",
    "explanation": "Greift direkt das Selbstbild des Viewers an. Erzeugt kognitive Dissonanz ('Ich mache doch alles richtig, warum bin ich trotzdem...?'). Zwingt zum Klicken.",
    "best_examples": ["Bist du trotz Schlaf IMMER müde?", "Bist du der nächste Verlierer?"],
    "usage_instructions": "Nutze dies bei Content, der ein heimlich befürchtetes Problem adressiert. Der Viewer muss sich ertappt fühlen.",
    "strength": "S-Tier"
  }}
]
"""
    
    try:
        response = await model.generate(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.2,  # Niedrig für Präzision
            max_tokens=8000,  # Genug Platz für 15 detaillierte Patterns
            cache_system=True
        )
        
        import re
        json_match = re.search(r'\[[\s\S]*\]', response.content)
        if json_match:
            master_patterns = json.loads(json_match.group())
            
            console.print(f"\n[bold green]   ✅ Opus identified {len(master_patterns)} Master Archetypes![/bold green]")
            
            # Zeige die gefundenen Patterns
            for i, p in enumerate(master_patterns[:5], 1):
                strength = p.get('strength', 'Unknown')
                name = p.get('name', 'Unknown')
                console.print(f"      {i}. [{strength}] {name}")
            
            if len(master_patterns) > 5:
                console.print(f"      ... und {len(master_patterns) - 5} weitere")
            
            return master_patterns
        else:
            console.print("[red]   ❌ Opus response could not be parsed. Falling back to basic consolidation.[/red]")
            return _basic_consolidation(raw_patterns)
            
    except Exception as e:
        console.print(f"[red]   ❌ Error in Opus synthesis: {e}[/red]")
        console.print("   Falling back to basic consolidation...")
        return _basic_consolidation(raw_patterns)


def _basic_consolidation(raw_patterns: List[Dict]) -> List[Dict]:
    """Fallback: Simple Python-basierte Deduplizierung."""
    unique = {}
    
    for p in raw_patterns:
        name = p.get('archetype_name', p.get('name', 'Unknown'))
        trigger = p.get('trigger', p.get('psychological_trigger', ''))
        
        # Composite key
        key = f"{name}::{trigger}"
        
        if key not in unique:
            unique[key] = p
            unique[key]['occurrence_count'] = 1
        else:
            unique[key]['occurrence_count'] = unique[key].get('occurrence_count', 1) + 1
    
    sorted_patterns = sorted(unique.values(), key=lambda x: x.get('occurrence_count', 0), reverse=True)
    
    console.print(f"   📊 Basic consolidation: {len(raw_patterns)} → {len(sorted_patterns)} patterns")
    
    return sorted_patterns[:20]  # Max 20 im Fallback


def save_patterns(patterns: List[Dict]):
    """Speichert die Muster in JSON."""
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "metadata": {
            "source": "headline_training_opus_synthesis",
            "count": len(patterns),
            "version": "2.0",
            "model": "claude-opus-4.5"
        },
        "patterns": patterns
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    console.print(f"\n[bold green]{'='*60}[/bold green]")
    console.print(f"[bold green]✅ Saved {len(patterns)} MASTER PATTERNS to {OUTPUT_FILE}[/bold green]")
    console.print(f"[bold green]{'='*60}[/bold green]")
    
    console.print("\n[bold]🏆 Top 5 Master Patterns:[/bold]")
    for i, p in enumerate(patterns[:5], 1):
        # Support both old and new field names
        name = p.get('name', p.get('archetype_name', 'Unknown'))
        trigger = p.get('psychological_trigger', p.get('trigger', 'N/A'))
        formula = p.get('formula', 'N/A')
        strength = p.get('strength', 'Unknown')
        
        # Get examples (support both formats)
        examples = p.get('best_examples', [])
        if not examples:
            example = p.get('example_from_data', 'N/A')
            examples = [example] if example != 'N/A' else []
        
        console.print(f"\n   {i}. [{strength}] [cyan]{name}[/cyan]")
        console.print(f"      Trigger: {trigger}")
        console.print(f"      Formula: {formula}")
        if examples:
            console.print(f"      Examples: {', '.join(examples[:2])}")


def load_patterns() -> List[Dict]:
    """Lädt die gespeicherten Headline-Patterns."""
    if not OUTPUT_FILE.exists():
        return []
    
    with open(OUTPUT_FILE) as f:
        data = json.load(f)
    
    return data.get('patterns', [])


if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "data/training/goat_clips.csv"
    asyncio.run(train_headlines(csv_file))


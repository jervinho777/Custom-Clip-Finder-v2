#!/usr/bin/env python3
# MUST be first - suppress huggingface tokenizers warning before any imports
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

"""
Custom Clip Finder v2

AI-powered viral clip extraction system.
4-Stage Pipeline: DISCOVER → COMPOSE → VALIDATE → EXPORT

Usage:
    python main.py process <video_path>
    python main.py init-brain
    python main.py test-apis
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(
    name="clip-finder",
    help="AI-powered viral clip extraction system"
)
console = Console()


@app.command()
def process(
    video_path: str = typer.Argument(..., help="Path to video file or URL (YouTube, TikTok, etc.)"),
    output_dir: str = typer.Option("data/output", help="Output directory"),
    num_clips: int = typer.Option(10, help="Number of clips to generate"),
    skip_cache: bool = typer.Option(False, help="Skip cached results"),
    formats: str = typer.Option("mp4,xml,json", help="Export formats (comma-separated)"),
    godmode: bool = typer.Option(False, help="Enable Godmode final evaluation (off by default - quality now in Opus)"),
    min_score: int = typer.Option(35, help="Minimum Godmode score (0-50)"),
    council: bool = typer.Option(False, help="🏛️ Enable Viral Council (Multi-AI Remixing) for premium quality")
):
    """
    Process a video and extract viral clips.
    
    Supports both local paths and URLs (YouTube, Instagram, TikTok, etc.)
    
    Full pipeline: DISCOVER → COMPOSE/COUNCIL → VALIDATE → (GODMODE) → EXPORT
    
    Use --council for Multi-AI Remixing (5 AIs compete, Opus judges).
    """
    asyncio.run(_process_video(
        video_path=video_path,
        output_dir=output_dir,
        num_clips=num_clips,
        use_cache=not skip_cache,
        formats=formats.split(","),
        godmode=godmode,
        min_score=min_score,
        use_council=council
    ))


async def _process_video(
    video_path: str,
    output_dir: str,
    num_clips: int,
    use_cache: bool,
    formats: list,
    godmode: bool = True,
    min_score: int = 35,
    use_council: bool = False
):
    """Run the full pipeline."""
    from utils import Cache
    from utils.transcribe import transcribe_video
    from utils.download import is_url, get_video_path
    
    console.print(f"\n[bold blue]Custom Clip Finder v2[/bold blue]")
    
    # Handle URL or local path
    if is_url(video_path):
        console.print(f"Detected URL: {video_path[:50]}...")
        console.print("[yellow]Downloading video...[/yellow]")
        video_path, was_downloaded = get_video_path(video_path)
        console.print(f"[green]Downloaded: {video_path.name}[/green]\n")
    else:
        video_path = Path(video_path)
        was_downloaded = False
        
        if not video_path.exists():
            console.print(f"[red]Error: Video not found: {video_path}[/red]")
            raise typer.Exit(1)
    
    console.print(f"Processing: {video_path.name}\n")
    
    cache = Cache()
    
    # Step 1: Transcribe
    # ALWAYS use transcript cache if available (transcription is expensive and deterministic)
    console.print("[bold]STEP 1: Transcription[/bold]")
    
    cached_transcript = cache.get_transcript(video_path)
    if cached_transcript:
        console.print("  Using cached transcript")
        transcript = cached_transcript.get("transcript", {})
    else:
        console.print("  Transcribing video (this may take a few minutes)...")
        transcript = await transcribe_video(str(video_path))
        cache.set_transcript(video_path, transcript)
        console.print("  ✅ Transcription complete")
    
    segments = transcript.get("segments", [])
    console.print(f"  Segments: {len(segments)}")
    console.print(f"  Duration: {transcript.get('duration', 0):.1f}s\n")
    
    # Step 2: Discover
    # NOTE: use_cache only affects DISCOVER/COMPOSE/VALIDATE, not transcript
    # Transcript is always cached if available (it's expensive and deterministic)
    console.print("[bold]STEP 2: DISCOVER[/bold]")
    
    from pipeline.discover import discover_moments
    
    moments = await discover_moments(
        transcript_segments=segments,
        video_path=str(video_path),
        use_cache=use_cache  # Skip DISCOVER cache if --skip-cache
    )
    
    console.print(f"  Found: {len(moments)} potential moments\n")
    
    # Step 3: Compose or Council
    moment_dicts = [
        {
            "start": m.start,
            "end": m.end,
            "archetype": m.archetype.value,
            "hook_strength": m.hook_strength,
            "viral_potential": m.viral_potential,
            "reasoning": m.reasoning,
            "hook_text": m.hook_text if hasattr(m, 'hook_text') else "",
            "viral_headline": getattr(m, 'viral_headline', ""),
            "segments": [s.model_dump() for s in m.segments] if m.segments else [],
            "editing_instruction": m.editing_instruction if hasattr(m, 'editing_instruction') else "",
            "full_text": m.full_text if hasattr(m, 'full_text') else ""
        }
        for m in moments
    ]
    
    if use_council:
        # ═══════════════════════════════════════════════════════════════
        # 🏛️ THE VIRAL COUNCIL - Multi-AI Remixing
        # ═══════════════════════════════════════════════════════════════
        console.print("[bold]STEP 3: 🏛️ VIRAL COUNCIL (Multi-AI Remixing)[/bold]")
        
        from pipeline.council import ViralCouncil, CouncilDecision
        from pipeline.discover import find_structural_blueprint
        from pipeline.compose import ComposedClip
        
        console.print(f"  🎯 Processing TOP {min(5, len(moment_dicts))} moments with Council")
        console.print("  👥 Council: Opus, GPT-5.2, Gemini 3, Grok 4.1, DeepSeek Reasoner")
        
        composed = []
        
        # Process top moments with Council (limit to 5 for cost)
        top_moments = sorted(moment_dicts, key=lambda m: m.get('viral_potential', 0), reverse=True)[:5]
        
        for i, moment in enumerate(top_moments, 1):
            console.print(f"\n  [{i}/{len(top_moments)}] Convening Council for moment @ {moment['start']:.0f}s...")
            
            # Get transcript text for this moment
            moment_text = moment.get('full_text', '')
            if not moment_text:
                # Extract from segments
                start_time = moment.get('start', 0)
                end_time = moment.get('end', 0)
                moment_text = ' '.join([
                    s.get('text', '') for s in segments
                    if s.get('start', 0) >= start_time and s.get('end', 0) <= end_time
                ])
            
            # 🧠 Active Brain Lookup (returns dict with pattern info)
            blueprint = await find_structural_blueprint(
                moment_text,
                moment.get('archetype', 'unknown')
            )
            brain_context = blueprint.get('context_for_prompt', '')
            pattern_name = blueprint.get('pattern_name', 'Standard')
            risk_level = blueprint.get('risk_level', 'low')
            
            console.print(f"    📋 Pattern: {pattern_name} (Risk: {risk_level})")
            
            # Get original segments for this moment (for robust remapping)
            start_time = moment.get('start', 0)
            end_time = moment.get('end', 0)
            moment_segments = [
                s for s in segments
                if s.get('start', 0) >= start_time and s.get('end', 0) <= end_time
            ]
            
            # 🏛️ Convene the Council
            council = ViralCouncil()
            await council.convene_council(
                moment_text, 
                brain_context,
                original_segments=moment_segments  # For robust timestamp remapping
            )
            
            # ⚖️ Executive Decision
            decision = await council.executive_decision()
            
            # Convert to ComposedClip
            original_archetype = moment.get('archetype', 'unknown')
            composed_clip = ComposedClip(
                structure_type="council_remix",
                archetype=original_archetype,  # Pass original archetype for validation
                segments=decision.final_segments,
                total_duration=sum(
                    s.get('end', 0) - s.get('start', 0) 
                    for s in decision.final_segments
                ),
                hook_text=moment.get('hook_text', ''),
                reasoning=decision.judge_reasoning,
                viral_headline=moment.get('viral_headline', ''),
                pacing_mode="density" if original_archetype in ['insight', 'tutorial'] else "immersion"
            )
            
            composed.append(composed_clip)
        
        console.print(f"\n  🏛️ Council completed: {len(composed)} clips\n")
        
    else:
        # ═══════════════════════════════════════════════════════════════
        # Standard Compose (VIRAL FACTORY MODE)
        # ═══════════════════════════════════════════════════════════════
        console.print("[bold]STEP 3: COMPOSE (VIRAL FACTORY MODE)[/bold]")
        
        from pipeline.compose import compose_batch
        
        console.print(f"  🏭 Processing ALL {len(moments)} moments (no artificial limits)")
        
        composed = await compose_batch(moment_dicts, segments)
        
    console.print(f"  Composed: {len(composed)} clips\n")
    
    # Step 4: Validate
    console.print("[bold]STEP 4: VALIDATE[/bold]")
    
    from pipeline.validate import validate_batch, rank_clips
    
    # Pass clip data directly (not wrapped in "clip" key)
    # Include archetype for archetype-aware validation
    clip_dicts = [
        {
            "structure_type": c.structure_type,
            "archetype": getattr(c, 'archetype', c.structure_type),  # Fallback to structure_type
            "segments": c.segments,
            "total_duration": c.total_duration,
            "hook_text": c.hook_text,
            "reasoning": c.reasoning,
            "pacing_mode": getattr(c, 'pacing_mode', 'density'),
            "viral_headline": getattr(c, 'viral_headline', ''),
        }
        for c in composed
    ]
    
    validated = await validate_batch(clip_dicts)
    
    # Debug: Show verdicts
    verdicts = [v.validation.verdict for v in validated]
    console.print(f"  Verdicts: {verdicts}")
    
    approved = [v for v in validated if v.validation.verdict in ["approve", "refine"]]
    console.print(f"  Approved: {len(approved)}/{len(validated)}\n")
    
    # Optional: Godmode Evaluation
    if godmode and approved:
        console.print("[bold]STEP 4.5: GODMODE EVALUATION[/bold]")
        
        from pipeline.godmode import godmode_evaluate, filter_by_godmode
        
        # Prepare clips for godmode
        godmode_clips = [
            {
                "clip_id": f"clip_{i+1}",
                "hook_text": v.clip.get("hook_text", ""),
                "total_duration": v.clip.get("total_duration", 0),
                "structure_type": v.clip.get("structure_type", ""),
                "reasoning": v.clip.get("reasoning", "")
            }
            for i, v in enumerate(approved)
        ]
        
        godmode_results = await godmode_evaluate(godmode_clips)
        
        # Filter by min_score
        passing_ids = {r.clip_id for r in godmode_results if r.score >= min_score}
        approved = [v for i, v in enumerate(approved) if f"clip_{i+1}" in passing_ids]
        
        console.print(f"  Passed Godmode: {len(approved)}/{len(godmode_clips)}\n")
    
    # VIRAL FACTORY: Rank but export ALL approved clips (num_clips is minimum)
    clips_to_rank = approved if godmode else validated
    actual_count = max(num_clips, len(clips_to_rank))  # At least num_clips, but all if more
    console.print(f"  🏭 Viral Factory: Exporting {len(clips_to_rank)} clips (min requested: {num_clips})")
    ranked = await rank_clips(clips_to_rank, target_count=actual_count)
    
    # Step 5: Export
    console.print("[bold]STEP 5: EXPORT[/bold]")
    
    from pipeline.export import export_batch, generate_export_report
    
    export_data = [
        {
            "clip": v.clip,
            "validation": {
                "verdict": v.validation.verdict,
                "assessment": v.validation.assessment,
                "predicted_performance": v.validation.predicted_performance
            },
            "rank": v.rank
        }
        for v in ranked
    ]
    
    results = await export_batch(
        validated_clips=export_data,
        source_video_path=str(video_path),
        output_dir=output_dir,
        formats=formats
    )
    
    report_path = generate_export_report(results, output_dir)
    
    # Summary
    console.print("\n[bold green]COMPLETE![/bold green]\n")
    
    table = Table(title="Exported Clips")
    table.add_column("Rank", style="cyan")
    table.add_column("Clip ID", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Status", style="magenta")
    
    for i, result in enumerate(results, 1):
        table.add_row(
            str(i),
            result.clip_id,
            f"{export_data[i-1]['clip'].get('total_duration', 0):.1f}s",
            "✓" if result.success else "✗"
        )
    
    console.print(table)
    console.print(f"\nReport: {report_path}")


@app.command()
def init_brain():
    """
    Initialize the BRAIN vector store from training data.
    """
    asyncio.run(_init_brain())


async def _init_brain():
    """Initialize BRAIN."""
    from brain.vector_store import initialize_brain
    
    console.print("[bold]Initializing BRAIN Vector Store...[/bold]\n")
    
    try:
        count = await initialize_brain()
        console.print(f"[green]BRAIN initialized with {count} clips[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def analyze_brain():
    """
    Run BRAIN analysis phase.
    
    Phase 1 des Systems:
    - Code 1: Analysiert isolierte virale Clips
    - Code 2: Analysiert Longform→Clip Paare
    - Code 3: Synthetisiert zu PRINCIPLES.json
    """
    asyncio.run(_analyze_brain())


async def _analyze_brain():
    """Run BRAIN analysis."""
    from brain.analyze import run_analysis
    
    console.print("[bold]Running BRAIN Analysis Phase...[/bold]\n")
    console.print("Phase 1: Analyse")
    console.print("  Code 1: Isolierte Clips → Patterns")
    console.print("  Code 2: Paare → Composition Patterns")
    console.print("  Code 3: Synthese → PRINCIPLES.json\n")
    
    try:
        result = await run_analysis()
        
        console.print("\n[green]Analysis complete![/green]")
        console.print(f"  Isolated patterns: {result['isolated_patterns'].get('clips_analyzed', 0)} clips")
        console.print(f"  Composition patterns: {result['composition_patterns'].get('pairs_analyzed', 0)} pairs")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def test_apis():
    """
    Test all API connections.
    """
    asyncio.run(_test_apis())


async def _test_apis():
    """Test API connections."""
    from models.base import get_model
    
    console.print("[bold]Testing API connections...[/bold]\n")
    
    # Use dynamic model detection
    apis = [
        ("anthropic", "sonnet"),
        ("openai", "mini"),  # Use mini for testing to save costs
        ("google", "flash"),
        ("xai", "standard"),
        ("deepseek", "chat"),
    ]
    
    table = Table(title="API Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Status", style="yellow")
    
    for provider, tier in apis:
        try:
            ai = get_model(provider, tier=tier)
            response = await ai.generate("Say 'OK' in one word.", max_tokens=10)
            status = f"✓ ({response.latency_ms}ms)"
            model_name = ai.model
        except ValueError as e:
            status = f"✗ Missing API key"
            model_name = f"{provider}/{tier}"
        except Exception as e:
            status = f"✗ {str(e)[:30]}"
            model_name = f"{provider}/{tier}"
        
        table.add_row(provider, model_name, status)
    
    console.print(table)


@app.command()
def cache_stats():
    """
    Show cache statistics.
    """
    from utils import Cache
    
    cache = Cache()
    stats = cache.stats()
    
    table = Table(title="Cache Statistics")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Size", style="yellow")
    
    for cat, data in stats.items():
        table.add_row(cat, str(data["count"]), f"{data['size_mb']:.2f} MB")
    
    console.print(table)


@app.command()
def train_headlines(
    csv_path: str = typer.Argument(
        "data/training/headline_training.csv",
        help="Path to CSV with headlines"
    )
):
    """
    Train the BRAIN to generate viral headlines.
    
    Analyzes a CSV with manual headline examples and extracts patterns.
    The CSV must have a 'HEADLINE' column.
    
    Example:
        python main.py train-headlines data/training/goat_clips.csv
    """
    from brain.train_headlines import train_headlines as run_training
    asyncio.run(run_training(csv_path))


@app.command()
def generate_headline(
    text: str = typer.Argument(..., help="Transcript excerpt or clip text"),
    archetype: str = typer.Option("unknown", help="Clip archetype (paradox_story, contrarian_rant, etc.)")
):
    """
    Generate a viral headline for a clip.
    
    Uses learned patterns from headline training.
    
    Example:
        python main.py generate-headline "Arbeite niemals für Geld..." --archetype paradox_story
    """
    from brain.headlines import generate_viral_headline
    
    async def _run():
        result = await generate_viral_headline(text, archetype=archetype)
        console.print("\n[bold green]🎯 Generated Headlines:[/bold green]")
        console.print(f"   Best: [bold cyan]{result.get('viral_headline', 'N/A')}[/bold cyan]")
        console.print(f"   Type: {result.get('headline_type', 'N/A')}")
        console.print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
        
        variants = result.get('headline_variants', [])
        if variants:
            console.print("\n   All Variants:")
            for v in variants:
                console.print(f"      - {v.get('text', '')} ({v.get('type', '')}, score: {v.get('score', 0)})")
    
    asyncio.run(_run())


@app.command()
def version():
    """
    Show version information.
    """
    console.print("[bold]Custom Clip Finder v2.0.0[/bold]")
    console.print("AI-powered viral clip extraction system")
    console.print("\nPipeline: DISCOVER → COMPOSE → VALIDATE → EXPORT")
    console.print("AI Ensemble: Claude, GPT, Gemini, Grok, DeepSeek")


if __name__ == "__main__":
    app()


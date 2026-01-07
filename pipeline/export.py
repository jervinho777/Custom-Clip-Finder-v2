"""
STAGE 4: EXPORT

Generate final outputs:
- MP4 Preview clips
- Premiere Pro XML
- JSON Metadata
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from utils import generate_premiere_xml, extract_clip


def _concat_clips(clip_paths: List[Path], output_path: Path) -> bool:
    """
    Concatenate multiple video clips into one using ffmpeg.
    
    Args:
        clip_paths: List of paths to clips to concatenate
        output_path: Path for output file
        
    Returns:
        True if successful, False otherwise
    """
    if not clip_paths:
        return False
        
    # Create concat list file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for clip in clip_paths:
            # Use absolute paths because the concat list file lives in a temp directory.
            # Relative paths would be resolved relative to that temp dir and break.
            f.write(f"file '{clip.resolve()}'\n")
        concat_list = f.name
    
    try:
        # Re-encode during concat for robustness:
        # - avoids stream-copy concat pitfalls (timestamp drift, differing stream params)
        # - ensures output duration matches sum of segments
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return output_path.exists()
    except subprocess.CalledProcessError as e:
        print(f"Concat error: {e.stderr}")
        return False
    finally:
        # Cleanup concat list file
        Path(concat_list).unlink(missing_ok=True)


@dataclass
class ExportResult:
    """Result of export operation."""
    clip_id: str
    mp4_path: Optional[Path]
    xml_path: Optional[Path]
    json_path: Optional[Path]
    success: bool
    error: Optional[str] = None


async def export_clip(
    validated_clip: Dict,
    source_video_path: str,
    output_dir: str = "data/output",
    clip_id: Optional[str] = None,
    formats: List[str] = ["mp4", "xml", "json"]
) -> ExportResult:
    """
    Export a validated clip to multiple formats.
    
    Args:
        validated_clip: Validated clip data
        source_video_path: Path to source video
        output_dir: Output directory
        clip_id: Optional clip ID (auto-generated if not provided)
        formats: List of formats to export
        
    Returns:
        ExportResult with paths to generated files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate clip ID
    if not clip_id:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clip_id = f"clip_{timestamp}"
    
    clip_data = validated_clip.get("clip", validated_clip)
    segments = clip_data.get("segments", [])
    
    if not segments:
        return ExportResult(
            clip_id=clip_id,
            mp4_path=None,
            xml_path=None,
            json_path=None,
            success=False,
            error="No segments in clip"
        )
    
    result = ExportResult(
        clip_id=clip_id,
        mp4_path=None,
        xml_path=None,
        json_path=None,
        success=True
    )
    
    try:
        # Export MP4
        if "mp4" in formats:
            mp4_path = output_path / f"{clip_id}.mp4"

            if len(segments) == 1:
                # Single segment - direct extraction
                seg = segments[0]
                extracted = extract_clip(
                    source_video_path,
                    mp4_path,
                    seg.get("start", 0),
                    seg.get("end", 0),
                    codec="libx264",
                    audio_codec="aac",
                )
                if extracted:
                    result.mp4_path = mp4_path
            else:
                # Multi-segment clip (chronological OR reordered):
                # Always extract each segment individually and concatenate.
                # This is REQUIRED to actually perform cuts.
                temp_clips: List[Path] = []
                temp_path = output_path / f"_temp_{clip_id}"
                temp_path.mkdir(parents=True, exist_ok=True)

                for idx, seg in enumerate(segments):
                    temp_clip = temp_path / f"seg_{idx:03d}.mp4"
                    extracted = extract_clip(
                        source_video_path,
                        temp_clip,
                        seg.get("start", 0),
                        seg.get("end", 0),
                        codec="libx264",
                        audio_codec="aac",
                    )
                    if extracted:
                        temp_clips.append(temp_clip)
                    else:
                        raise Exception(f"Failed to extract segment {idx} for {clip_id}")

                concat_success = _concat_clips(temp_clips, mp4_path)
                if concat_success:
                    result.mp4_path = mp4_path
                else:
                    raise Exception(f"Failed to concatenate segments for {clip_id}")

                # Cleanup temp files
                import shutil

                shutil.rmtree(temp_path, ignore_errors=True)
        
        # Export XML
        if "xml" in formats:
            xml_path = output_path / f"{clip_id}.xml"
            generate_premiere_xml(
                segments=segments,
                source_video_path=source_video_path,
                output_path=xml_path,
                sequence_name=clip_id
            )
            result.xml_path = xml_path
        
        # Export JSON metadata
        if "json" in formats:
            json_path = output_path / f"{clip_id}.json"

            # Compute accurate duration from segments (do not trust model output)
            computed_total_duration = 0.0
            for seg in segments:
                try:
                    computed_total_duration += float(seg.get("end", 0)) - float(
                        seg.get("start", 0)
                    )
                except Exception:
                    continue
            
            metadata = {
                "clip_id": clip_id,
                "created_at": datetime.now().isoformat(),
                "source_video": str(source_video_path),
                "structure_type": clip_data.get("structure_type", "unknown"),
                "segments": segments,
                "total_duration": round(computed_total_duration, 2),
                "hook_text": clip_data.get("hook_text", ""),
                "reasoning": clip_data.get("reasoning", ""),
                "validation": validated_clip.get("validation", {}),
                "predicted_performance": validated_clip.get("validation", {}).get(
                    "predicted_performance", {}
                ),
                "rank": validated_clip.get("rank")
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            result.json_path = json_path
        
        print(f"Exported: {clip_id}")
        if result.mp4_path:
            print(f"  MP4: {result.mp4_path}")
        if result.xml_path:
            print(f"  XML: {result.xml_path}")
        if result.json_path:
            print(f"  JSON: {result.json_path}")
        
    except Exception as e:
        result.success = False
        result.error = str(e)
        print(f"Export failed: {e}")
    
    return result


async def export_batch(
    validated_clips: List[Dict],
    source_video_path: str,
    output_dir: str = "data/output",
    formats: List[str] = ["mp4", "xml", "json"]
) -> List[ExportResult]:
    """
    Export multiple clips.
    
    Args:
        validated_clips: List of validated clips
        source_video_path: Path to source video
        output_dir: Output directory
        formats: Formats to export
        
    Returns:
        List of ExportResult objects
    """
    results = []
    
    for i, clip in enumerate(validated_clips, 1):
        rank = clip.get("rank", i)
        clip_id = f"clip_{rank:02d}"
        
        result = await export_clip(
            validated_clip=clip,
            source_video_path=source_video_path,
            output_dir=output_dir,
            clip_id=clip_id,
            formats=formats
        )
        results.append(result)
    
    # Summary
    successful = sum(1 for r in results if r.success)
    print(f"\nExport complete: {successful}/{len(results)} clips exported")
    
    return results


def generate_export_report(
    results: List[ExportResult],
    output_dir: str = "data/output"
) -> Path:
    """
    Generate summary report for exported clips.
    
    Args:
        results: List of export results
        output_dir: Output directory
        
    Returns:
        Path to report file
    """
    output_path = Path(output_dir)
    report_path = output_path / "export_report.json"
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_clips": len(results),
        "successful": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "clips": [
            {
                "clip_id": r.clip_id,
                "success": r.success,
                "mp4": str(r.mp4_path) if r.mp4_path else None,
                "xml": str(r.xml_path) if r.xml_path else None,
                "json": str(r.json_path) if r.json_path else None,
                "error": r.error
            }
            for r in results
        ]
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_path



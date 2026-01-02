"""
STAGE 4: EXPORT

Generate final outputs:
- MP4 Preview clips
- Premiere Pro XML
- JSON Metadata
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from utils import generate_premiere_xml, extract_clip


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
            
            # For simple clips, extract directly
            if len(segments) == 1:
                seg = segments[0]
                extracted = extract_clip(
                    source_video_path,
                    mp4_path,
                    seg.get("start", 0),
                    seg.get("end", 0)
                )
                if extracted:
                    result.mp4_path = mp4_path
            else:
                # For complex clips, we'd need to concat
                # For now, export first segment as preview
                seg = segments[0]
                extracted = extract_clip(
                    source_video_path,
                    mp4_path,
                    seg.get("start", 0),
                    segments[-1].get("end", 0)
                )
                if extracted:
                    result.mp4_path = mp4_path
        
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
            
            metadata = {
                "clip_id": clip_id,
                "created_at": datetime.now().isoformat(),
                "source_video": str(source_video_path),
                "structure_type": clip_data.get("structure_type", "unknown"),
                "segments": segments,
                "total_duration": clip_data.get("total_duration", 0),
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


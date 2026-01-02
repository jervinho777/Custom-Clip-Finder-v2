#!/usr/bin/env python3
"""
Production: Process video with Full AI
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def process_video(video_path: str, metadata: dict = None):
    """
    Full AI processing pipeline
    """
    
    from backend.processors.video_processor import VideoProcessor
    from backend.processors.transcriber import Transcriber
    from backend.processors.feature_extractor import FeatureExtractor
    from backend.ml.models.virality_predictor import ViralityPredictor
    from backend.ai.content_restructurer import ContentRestructurer
    from backend.utils.transcript_cache import TranscriptCache
    
    # Initialize
    video_proc = VideoProcessor(video_path)
    cache = TranscriptCache()
    feature_extractor = FeatureExtractor()
    predictor = ViralityPredictor()
    restructurer = ContentRestructurer(predictor, feature_extractor)
    
    # Get transcript
    audio_path = video_path.replace('.mp4', '_audio.wav')
    video_proc.extract_audio(audio_path)
    
    transcript = cache.get(video_path)
    if not transcript:
        transcriber = Transcriber(model_size="medium")
        transcript = transcriber.transcribe(audio_path, language="de")
        cache.save(video_path, transcript)
    
    # ML + AI Analysis
    sentences = restructurer.analyze_sentences(transcript, audio_path)
    variants = restructurer.build_clip_variants(sentences, (45, 60))
    
    # Save results
    output = {
        'video': video_path,
        'processed_at': datetime.now().isoformat(),
        'total_sentences': len(sentences),
        'top_sentences': [
            {
                'text': s['text'],
                'score': s['ml_score'],
                'type': s['type']
            } for s in sentences[:20]
        ],
        'ai_variants': [
            {
                'name': v['name'],
                'strategy': v.get('strategy'),
                'predicted_retention': v.get('predicted_retention'),
                'duration': v['total_duration'],
                'structure': [s['text'] for s in v['structure']]
            } for v in variants
        ],
        'metadata': metadata
    }
    
    # Save
    output_file = Path(f"data/outputs/{Path(video_path).stem}_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_video_full_ai.py <video>")
        sys.exit(1)
    
    result = process_video(sys.argv[1])
    print(f"\n✅ Processed: {result['video']}")
    print(f"   Variants: {len(result['ai_variants'])}")
    print(f"   Best retention: {max(v['predicted_retention'] for v in result['ai_variants'])}%")

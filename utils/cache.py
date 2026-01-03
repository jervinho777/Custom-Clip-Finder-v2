"""
Simple Caching System

File-based caching for transcripts, AI responses, and pipeline results.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


class Cache:
    """
    Simple file-based cache for expensive operations.
    
    Caches:
    - Transcripts (keyed by video file hash)
    - AI responses (keyed by prompt hash)
    - Pipeline results (keyed by video + config hash)
    """
    
    def __init__(self, cache_dir: str | Path = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-directories
        (self.cache_dir / "transcripts").mkdir(exist_ok=True)
        (self.cache_dir / "ai_responses").mkdir(exist_ok=True)
        (self.cache_dir / "pipeline").mkdir(exist_ok=True)
    
    def _hash_key(self, key: str) -> str:
        """Create short hash from key."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _file_hash(self, file_path: Path) -> str:
        """Create hash from file content (first 1MB + size)."""
        file_path = Path(file_path)
        if not file_path.exists():
            return self._hash_key(str(file_path))
        
        size = file_path.stat().st_size
        with open(file_path, 'rb') as f:
            content = f.read(1024 * 1024)  # First 1MB
        
        return hashlib.sha256(content + str(size).encode()).hexdigest()[:16]
    
    def get_transcript(self, video_path: str | Path) -> Optional[dict]:
        """
        Get cached transcript for video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Transcript dict or None if not cached
        """
        video_path = Path(video_path)
        
        # Strategy 1: Check hash-based cache (new format)
        key = self._file_hash(video_path)
        cache_file = self.cache_dir / "transcripts" / f"{key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        # Strategy 2: Check name-based cache (old format from V1)
        # e.g. "Dieter Lange.mp4" → "Dieter Lange_transcript.json"
        name_based = self.cache_dir / "transcripts" / f"{video_path.stem}_transcript.json"
        if name_based.exists():
            with open(name_based) as f:
                data = json.load(f)
                # Convert old format to new format
                if "transcript" not in data:
                    # Old format: transcript is the root object
                    return {"transcript": data, "video_path": str(video_path)}
                return data
        
        return None
    
    def set_transcript(self, video_path: str | Path, transcript: dict) -> Path:
        """
        Cache transcript for video.
        
        Args:
            video_path: Path to video file
            transcript: Transcript data to cache
            
        Returns:
            Path to cache file
        """
        key = self._file_hash(Path(video_path))
        cache_file = self.cache_dir / "transcripts" / f"{key}.json"
        
        data = {
            "video_path": str(video_path),
            "cached_at": datetime.now().isoformat(),
            "transcript": transcript
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return cache_file
    
    def get_ai_response(self, prompt_key: str) -> Optional[dict]:
        """
        Get cached AI response.
        
        Args:
            prompt_key: Unique key for the prompt (hash of prompt + model)
            
        Returns:
            Response dict or None if not cached
        """
        key = self._hash_key(prompt_key)
        cache_file = self.cache_dir / "ai_responses" / f"{key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None
    
    def set_ai_response(self, prompt_key: str, response: dict) -> Path:
        """
        Cache AI response.
        
        Args:
            prompt_key: Unique key for the prompt
            response: Response data to cache
            
        Returns:
            Path to cache file
        """
        key = self._hash_key(prompt_key)
        cache_file = self.cache_dir / "ai_responses" / f"{key}.json"
        
        data = {
            "prompt_key": prompt_key,
            "cached_at": datetime.now().isoformat(),
            "response": response
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return cache_file
    
    def get_pipeline_result(self, video_path: str | Path, stage: str) -> Optional[dict]:
        """
        Get cached pipeline result.
        
        Args:
            video_path: Path to video
            stage: Pipeline stage name
            
        Returns:
            Result dict or None if not cached
        """
        video_key = self._file_hash(Path(video_path))
        cache_file = self.cache_dir / "pipeline" / f"{video_key}_{stage}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None
    
    def set_pipeline_result(self, video_path: str | Path, stage: str, result: dict) -> Path:
        """
        Cache pipeline result.
        
        Args:
            video_path: Path to video
            stage: Pipeline stage name
            result: Result data to cache
            
        Returns:
            Path to cache file
        """
        video_key = self._file_hash(Path(video_path))
        cache_file = self.cache_dir / "pipeline" / f"{video_key}_{stage}.json"
        
        data = {
            "video_path": str(video_path),
            "stage": stage,
            "cached_at": datetime.now().isoformat(),
            "result": result
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return cache_file
    
    def clear(self, category: Optional[str] = None):
        """
        Clear cache.
        
        Args:
            category: Optional category to clear (transcripts, ai_responses, pipeline)
                     If None, clears all.
        """
        if category:
            target = self.cache_dir / category
            if target.exists():
                for f in target.glob("*.json"):
                    f.unlink()
        else:
            for cat in ["transcripts", "ai_responses", "pipeline"]:
                self.clear(cat)
    
    def stats(self) -> dict:
        """Get cache statistics."""
        stats = {}
        for cat in ["transcripts", "ai_responses", "pipeline"]:
            cat_dir = self.cache_dir / cat
            if cat_dir.exists():
                files = list(cat_dir.glob("*.json"))
                total_size = sum(f.stat().st_size for f in files)
                stats[cat] = {
                    "count": len(files),
                    "size_mb": round(total_size / (1024 * 1024), 2)
                }
        return stats


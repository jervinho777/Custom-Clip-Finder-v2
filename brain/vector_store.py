"""
Vector Store for Clip Similarity Search

Uses ChromaDB for efficient semantic search over 972+ clips.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


BRAIN_DIR = Path(__file__).parent
VECTOR_STORE_DIR = BRAIN_DIR / "vector_store"
TRAINING_DATA_PATH = Path(__file__).parent.parent / "data" / "training" / "goat_training_data.json"


class VectorStore:
    """
    ChromaDB-based vector store for clip similarity.
    
    Stores clip embeddings for fast similarity search.
    """
    
    def __init__(self, collection_name: str = "viral_clips"):
        self.collection_name = collection_name
        self._client = None
        self._collection = None
    
    def _get_client(self):
        """Lazy load ChromaDB client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings
            
            VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.PersistentClient(
                path=str(VECTOR_STORE_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
        return self._client
    
    def _get_collection(self):
        """Get or create collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection
    
    def is_initialized(self) -> bool:
        """Check if vector store has data."""
        try:
            collection = self._get_collection()
            return collection.count() > 0
        except Exception:
            return False
    
    def count(self) -> int:
        """Get number of clips in store."""
        try:
            return self._get_collection().count()
        except Exception:
            return 0
    
    async def initialize_from_training_data(
        self,
        min_views: int = 10000,
        batch_size: int = 100
    ) -> int:
        """
        Initialize vector store from goat_training_data.json.
        
        Args:
            min_views: Minimum views to include clip
            batch_size: Batch size for adding
            
        Returns:
            Number of clips added
        """
        if not TRAINING_DATA_PATH.exists():
            raise FileNotFoundError(f"Training data not found: {TRAINING_DATA_PATH}")
        
        with open(TRAINING_DATA_PATH) as f:
            clips = json.load(f)
        
        print(f"Loading {len(clips)} clips from training data...")
        
        # Filter by views
        filtered_clips = []
        for clip in clips:
            views = clip.get("performance", {}).get("views", 0)
            if views >= min_views:
                filtered_clips.append(clip)
        
        print(f"Filtered to {len(filtered_clips)} clips with {min_views}+ views")
        
        collection = self._get_collection()
        added = 0
        
        for i in range(0, len(filtered_clips), batch_size):
            batch = filtered_clips[i:i+batch_size]
            
            ids = []
            documents = []
            metadatas = []
            
            for clip in batch:
                # Create unique ID
                clip_id = clip.get("video_id", hashlib.md5(
                    json.dumps(clip, sort_keys=True).encode()
                ).hexdigest()[:16])
                
                # Get text for embedding
                transcript = clip.get("transcript", {})
                text = transcript.get("text", "")
                if not text:
                    continue
                
                # Truncate for embedding
                text = text[:2000]
                
                # Build metadata
                perf = clip.get("performance", {})
                metadata = {
                    "video_id": clip_id,
                    "views": perf.get("views", 0),
                    "completion_rate": perf.get("completion_rate", 0),
                    "account": clip.get("account", ""),
                    "framework": clip.get("framework", ""),
                    "hook": text[:200]  # First 200 chars as hook
                }
                
                ids.append(clip_id)
                documents.append(text)
                metadatas.append(metadata)
            
            if ids:
                collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                added += len(ids)
                print(f"Added batch: {added}/{len(filtered_clips)}")
        
        print(f"Vector store initialized with {added} clips")
        return added
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar clips.
        
        Args:
            query: Text to search for
            n_results: Number of results
            where: Optional filter conditions
            
        Returns:
            List of similar clips with metadata and distance
        """
        collection = self._get_collection()
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted = []
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"][0]):
                formatted.append({
                    "id": doc_id,
                    "text": results["documents"][0][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else 0
                })
        
        return formatted
    
    async def add_clip(
        self,
        clip_id: str,
        text: str,
        metadata: Dict
    ):
        """
        Add a single clip to the store.
        
        Args:
            clip_id: Unique clip ID
            text: Clip transcript text
            metadata: Clip metadata (views, etc.)
        """
        collection = self._get_collection()
        
        collection.upsert(
            ids=[clip_id],
            documents=[text[:2000]],
            metadatas=[metadata]
        )
    
    def clear(self):
        """Clear all data from vector store."""
        client = self._get_client()
        try:
            client.delete_collection(self.collection_name)
            self._collection = None
            print(f"Cleared collection: {self.collection_name}")
        except Exception:
            pass


async def initialize_brain():
    """
    Initialize the BRAIN system.
    
    Creates vector store from training data.
    """
    store = VectorStore()
    
    if store.is_initialized():
        print(f"Vector store already initialized with {store.count()} clips")
        return store.count()
    
    return await store.initialize_from_training_data()


"""
Vector Store V3 - Specialized Collections

Shift from one generic collection to specialized, searchable stores:

1. hooks_collection: Only viral hooks (first 2 sentences)
   - Use Case: Compare new sentences against known viral hooks
   - "Sentence at 10:42 is 85% similar to Alex Hormozi viral hook"

2. patterns_collection: Content summaries + structure
   - Use Case: Find similar content patterns

3. blueprints_collection: Transformation blueprints
   - Use Case: Find similar editing patterns

Each collection is weighted by views/performance.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


BRAIN_DIR = Path(__file__).parent
VECTOR_STORE_DIR = BRAIN_DIR / "vector_store"
TRAINING_DATA_PATH = Path(__file__).parent.parent / "data" / "training" / "goat_training_data.json"
HOOKS_BLUEPRINT_PATH = BRAIN_DIR.parent / "data" / "learnings" / "hook_blueprints.json"
ACCOUNTS_METADATA_PATH = BRAIN_DIR.parent / "data" / "accounts_metadata.json"

# Default Baseline für unbekannte Accounts
DEFAULT_BASELINE = 1000


@dataclass
class HookMatch:
    """Result of a hook similarity search."""
    hook_text: str
    similarity: float  # 0-1, higher is more similar
    views: int
    source_clip_id: str
    hook_type: str
    account: str


@dataclass
class SentenceScanResult:
    """Result of scanning a sentence against the hook database."""
    sentence: str
    timestamp: float
    best_match: Optional[HookMatch]
    is_potential_viral_hook: bool  # True if similarity > threshold


@dataclass
class GlobalHookCandidate:
    """
    A candidate hook found in the ENTIRE transcript.
    
    No time limits - the perfect hook can be 20 minutes after the body.
    """
    sentence: str
    timestamp: float
    end_timestamp: float
    
    # Semantic match to the body topic
    semantic_score: float  # 0-1, how well it matches the body topic
    
    # Hook quality indicators
    punch_score: float  # 0-1, how "punchy" the sentence is
    contains_conclusion_marker: bool
    contains_number: bool
    is_question: bool
    is_contrarian: bool
    word_count: int
    
    # Match to known viral hooks
    viral_hook_similarity: float  # 0-1, similarity to known viral hooks
    matched_viral_hook: Optional[str] = None


class VectorStore:
    """
    ChromaDB-based vector store V3 with specialized collections.
    
    Collections:
    - viral_hooks: High-performance hooks only (>100k views)
    - content_patterns: Full content embeddings
    - blueprints: Transformation patterns
    """
    
    # Collection names
    HOOKS_COLLECTION = "viral_hooks"
    PATTERNS_COLLECTION = "content_patterns"
    BLUEPRINTS_COLLECTION = "transformation_blueprints"
    
    # Default collection for backwards compatibility
    DEFAULT_COLLECTION = "viral_clips"
    
    def __init__(self, collection_name: str = None):
        """
        Initialize vector store.
        
        Args:
            collection_name: Optional specific collection (for backwards compat)
        """
        self.collection_name = collection_name or self.DEFAULT_COLLECTION
        self._client = None
        self._collections: Dict = {}
    
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
    
    def _get_collection(self, name: str = None):
        """Get or create a specific collection."""
        collection_name = name or self.collection_name
        
        if collection_name not in self._collections:
            client = self._get_client()
            self._collections[collection_name] = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collections[collection_name]
    
    # =========================================================================
    # Collection Status
    # =========================================================================
    
    def is_initialized(self, collection: str = None) -> bool:
        """Check if a collection has data."""
        try:
            coll = self._get_collection(collection)
            return coll.count() > 0
        except Exception:
            return False
    
    def count(self, collection: str = None) -> int:
        """Get number of items in a collection."""
        try:
            return self._get_collection(collection).count()
        except Exception:
            return 0
    
    def get_all_counts(self) -> Dict[str, int]:
        """Get counts for all collections."""
        return {
            "hooks": self.count(self.HOOKS_COLLECTION),
            "patterns": self.count(self.PATTERNS_COLLECTION),
            "blueprints": self.count(self.BLUEPRINTS_COLLECTION),
            "legacy": self.count(self.DEFAULT_COLLECTION)
        }
    
    # =========================================================================
    # HOOKS COLLECTION - First 2 sentences of viral clips
    # =========================================================================
    
    async def initialize_hooks_collection(
        self,
        min_views: int = 100000,
        batch_size: int = 100
    ) -> int:
        """
        Initialize the hooks collection from training data.
        
        WICHTIG: Speichert NVI (Normalized Viral Index) für jedes Hook!
        
        Matthias Langwasser (NVI 7000) wird dadurch viel stärker
        gewichtet als Greator (NVI 40).
        
        Args:
            min_views: Minimum views threshold
            batch_size: Batch size for adding
            
        Returns:
            Number of hooks added
        """
        if not TRAINING_DATA_PATH.exists():
            raise FileNotFoundError(f"Training data not found: {TRAINING_DATA_PATH}")
        
        with open(TRAINING_DATA_PATH) as f:
            clips = json.load(f)
        
        # Lade Account Baselines
        accounts_data = {}
        if ACCOUNTS_METADATA_PATH.exists():
            with open(ACCOUNTS_METADATA_PATH) as f:
                accounts_data = json.load(f)
        
        print(f"Loading hooks from {len(clips)} clips (min views: {min_views:,})...")
        print(f"   Loaded {len(accounts_data)} account baselines for NVI calculation")
        
        collection = self._get_collection(self.HOOKS_COLLECTION)
        added = 0
        seen_ids = set()
        
        # Filter and sort by views
        filtered = [
            c for c in clips
            if c.get("performance", {}).get("views", 0) >= min_views
            and c.get("transcript", {}).get("text")
        ]
        
        # Berechne NVI für jeden Clip
        for clip in filtered:
            account = clip.get("account", "unknown")
            views = clip.get("performance", {}).get("views", 0)
            
            # Hole Baseline (mit Fallback)
            if account in accounts_data:
                baseline = accounts_data[account].get("baseline", DEFAULT_BASELINE)
            else:
                baseline = DEFAULT_BASELINE
            
            # Berechne NVI
            nvi = views / max(baseline, 1.0)
            clip["_nvi"] = nvi
            clip["_baseline"] = baseline
        
        # Sortiere nach NVI statt nach Views!
        # Matthias Langwasser (NVI 7000) kommt vor Greator (NVI 40)
        filtered.sort(key=lambda c: c.get("_nvi", 0), reverse=True)
        
        print(f"Found {len(filtered)} clips with {min_views:,}+ views")
        print(f"   Top NVI: {filtered[0].get('account', 'unknown')} = {filtered[0].get('_nvi', 0):.0f}" if filtered else "")
        
        for i in range(0, len(filtered), batch_size):
            batch = filtered[i:i+batch_size]
            
            ids = []
            documents = []
            metadatas = []
            
            for clip in batch:
                transcript = clip.get("transcript", {})
                text = transcript.get("text", "")
                
                # Extract first 2 sentences (the hook)
                sentences = text.replace("!", ".").replace("?", ".").split(".")
                hook_text = ". ".join(s.strip() for s in sentences[:2] if s.strip())
                
                if not hook_text or len(hook_text) < 10:
                    continue
                
                # Create unique ID
                clip_hash = hashlib.md5(hook_text.encode()).hexdigest()[:12]
                clip_id = f"hook_{clip_hash}"
                
                if clip_id in seen_ids:
                    continue
                seen_ids.add(clip_id)
                
                perf = clip.get("performance", {})
                nvi = clip.get("_nvi", 1.0)
                
                # Engagement-Daten
                likes = perf.get("likes", 0)
                shares = perf.get("shares", 0)
                saves = perf.get("saves", 0)
                engagement_rate = (shares + saves) / max(perf.get("views", 1), 1)
                
                metadata = {
                    "views": perf.get("views", 0),
                    "nvi": round(nvi, 2),  # NEU: NVI für Ranking
                    "baseline": clip.get("_baseline", DEFAULT_BASELINE),
                    "completion_rate": perf.get("completion_rate", 0),
                    "engagement_rate": round(engagement_rate, 4),  # NEU
                    "likes": likes,
                    "shares": shares,
                    "saves": saves,
                    "account": clip.get("account", ""),
                    "hook_type": self._classify_hook_type(hook_text),
                    "word_count": len(hook_text.split()),
                    "source_clip_id": clip.get("video_id", "unknown")
                }
                
                ids.append(clip_id)
                documents.append(hook_text)
                metadatas.append(metadata)
            
            if ids:
                collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
                added += len(ids)
                print(f"  Added hooks batch: {added}/{len(filtered)}")
        
        print(f"✅ Hooks collection initialized with {added} high-performance hooks (NVI-weighted)")
        return added
    
    def _classify_hook_type(self, text: str) -> str:
        """Classify hook type."""
        text_lower = text.lower()
        
        if "?" in text:
            return "question"
        elif any(w in text_lower for w in ["nicht", "niemals", "nie", "falsch"]):
            return "contrarian"
        elif any(c.isdigit() for c in text[:50]):
            return "statistic"
        elif any(w in text_lower for w in ["als ich", "gestern", "vor"]):
            return "story"
        else:
            return "statement"
    
    # =========================================================================
    # PATTERNS COLLECTION - Full content embeddings
    # =========================================================================
    
    async def initialize_patterns_collection(
        self,
        min_views: int = 10000,
        batch_size: int = 100
    ) -> int:
        """
        Initialize patterns collection with full content.
        
        Args:
            min_views: Minimum views threshold
            batch_size: Batch size
            
        Returns:
            Number of patterns added
        """
        if not TRAINING_DATA_PATH.exists():
            raise FileNotFoundError(f"Training data not found: {TRAINING_DATA_PATH}")
        
        with open(TRAINING_DATA_PATH) as f:
            clips = json.load(f)
        
        print(f"Loading patterns from {len(clips)} clips...")
        
        collection = self._get_collection(self.PATTERNS_COLLECTION)
        added = 0
        seen_ids = set()
        
        filtered = [
            c for c in clips
            if c.get("performance", {}).get("views", 0) >= min_views
            and c.get("transcript", {}).get("text")
        ]
        
        for i in range(0, len(filtered), batch_size):
            batch = filtered[i:i+batch_size]
            
            ids = []
            documents = []
            metadatas = []
            
            for clip in batch:
                text = clip.get("transcript", {}).get("text", "")
                
                if not text:
                    continue
                
                # Truncate for embedding
                text = text[:2000]
                
                clip_hash = hashlib.md5(text.encode()).hexdigest()[:12]
                clip_id = f"pattern_{clip_hash}"
                
                if clip_id in seen_ids:
                    continue
                seen_ids.add(clip_id)
                
                perf = clip.get("performance", {})
                
                metadata = {
                    "views": perf.get("views", 0),
                    "completion_rate": perf.get("completion_rate", 0),
                    "account": clip.get("account", ""),
                    "framework": clip.get("framework", ""),
                    "hook": text[:200],
                    "word_count": len(text.split())
                }
                
                ids.append(clip_id)
                documents.append(text)
                metadatas.append(metadata)
            
            if ids:
                collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
                added += len(ids)
        
        print(f"✅ Patterns collection initialized with {added} patterns")
        return added
    
    # =========================================================================
    # SEARCH FUNCTIONS (NVI-WEIGHTED!)
    # =========================================================================
    
    async def search_hooks(
        self,
        query: str,
        n_results: int = 5,
        min_views: int = 0,
        min_nvi: float = 0,
        use_nvi_ranking: bool = True
    ) -> List[HookMatch]:
        """
        Search for similar hooks with NVI-weighted ranking.
        
        WICHTIG: Wenn use_nvi_ranking=True, werden Ergebnisse nach
        kombiniertem Score (similarity * NVI-weight) gerankt.
        
        Matthias Langwasser (NVI 7000) wird dadurch viel höher gerankt
        als Greator (NVI 40), selbst wenn die Similarity ähnlich ist.
        
        Args:
            query: Text to compare
            n_results: Number of results
            min_views: Minimum views filter
            min_nvi: Minimum NVI filter (z.B. 10 für nur virale Clips)
            use_nvi_ranking: Ob NVI ins Ranking einfließen soll
            
        Returns:
            List of HookMatch objects with similarity scores
        """
        collection = self._get_collection(self.HOOKS_COLLECTION)
        
        if collection.count() == 0:
            return []
        
        # Filters
        where_filter = None
        if min_views > 0 or min_nvi > 0:
            conditions = []
            if min_views > 0:
                conditions.append({"views": {"$gte": min_views}})
            if min_nvi > 0:
                conditions.append({"nvi": {"$gte": min_nvi}})
            
            if len(conditions) == 1:
                where_filter = conditions[0]
            else:
                where_filter = {"$and": conditions}
        
        # Get more results if we're re-ranking
        fetch_n = n_results * 3 if use_nvi_ranking else n_results
        
        results = collection.query(
            query_texts=[query],
            n_results=fetch_n,
            where=where_filter
        )
        
        matches = []
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 1
                
                # Convert distance to similarity (cosine distance: 0 = identical)
                similarity = 1 - (distance / 2)  # Normalize to 0-1
                
                # Hole NVI (default 1.0 für alte Daten ohne NVI)
                nvi = metadata.get("nvi", 1.0)
                
                # Berechne NVI-Gewicht (log-skaliert)
                # NVI 1 → weight 1.0, NVI 10 → weight 2.0, NVI 100 → weight 3.0
                import math
                if nvi <= 1:
                    nvi_weight = 1.0
                else:
                    nvi_weight = 1.0 + math.log10(nvi)
                
                # Kombinierter Score für Ranking
                combined_score = similarity * nvi_weight if use_nvi_ranking else similarity
                
                matches.append({
                    "hook_text": results["documents"][0][i] if results.get("documents") else "",
                    "similarity": round(similarity, 3),
                    "nvi": round(nvi, 2),
                    "nvi_weight": round(nvi_weight, 2),
                    "combined_score": round(combined_score, 3),
                    "views": metadata.get("views", 0),
                    "source_clip_id": metadata.get("source_clip_id", ""),
                    "hook_type": metadata.get("hook_type", ""),
                    "account": metadata.get("account", ""),
                    "engagement_rate": metadata.get("engagement_rate", 0)
                })
        
        # Re-rank by combined score if NVI ranking is enabled
        if use_nvi_ranking:
            matches.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Convert to HookMatch objects and limit
        result = []
        for m in matches[:n_results]:
            result.append(HookMatch(
                hook_text=m["hook_text"],
                similarity=m["similarity"],
                views=m["views"],
                source_clip_id=m["source_clip_id"],
                hook_type=m["hook_type"],
                account=m["account"]
            ))
        
        return result
    
    async def search_patterns(
        self,
        query: str,
        n_results: int = 5,
        min_views: int = 0
    ) -> List[Dict]:
        """
        Search for similar content patterns.
        
        Args:
            query: Text to search
            n_results: Number of results
            min_views: Minimum views filter
            
        Returns:
            List of pattern dicts
        """
        collection = self._get_collection(self.PATTERNS_COLLECTION)
        
        if collection.count() == 0:
            return []
        
        where_filter = {"views": {"$gte": min_views}} if min_views > 0 else None
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        formatted = []
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 1
                
                formatted.append({
                    "id": doc_id,
                    "text": results["documents"][0][i] if results.get("documents") else "",
                    "metadata": metadata,
                    "similarity": round(1 - (distance / 2), 3),
                    "views": metadata.get("views", 0)
                })
        
        return formatted
    
    # =========================================================================
    # SCAN FOR HOOKS (Main use case)
    # =========================================================================
    
    async def scan_transcript_for_hooks(
        self,
        transcript_segments: List[Dict],
        similarity_threshold: float = 0.75,
        min_views: int = 100000,
        window_size: int = 2
    ) -> List[SentenceScanResult]:
        """
        Scan a transcript sentence-by-sentence against the hooks database.
        
        This is the main discovery use case:
        "Find sentences that are similar to known viral hooks"
        
        Args:
            transcript_segments: List of transcript segments with text and timestamps
            similarity_threshold: Minimum similarity to flag as potential hook
            min_views: Minimum views for comparison hooks
            window_size: Number of sentences to combine for comparison
            
        Returns:
            List of SentenceScanResult for sentences above threshold
        """
        if not self.is_initialized(self.HOOKS_COLLECTION):
            print("⚠️ Hooks collection not initialized")
            return []
        
        results = []
        
        # Extract sentences with timestamps
        sentences = []
        for seg in transcript_segments:
            text = seg.get("text", "")
            start = seg.get("start", 0)
            
            # Split into sentences
            for sentence in text.replace("!", ".").replace("?", ".").split("."):
                sentence = sentence.strip()
                if len(sentence) > 15:  # Minimum sentence length
                    sentences.append((sentence, start))
        
        print(f"Scanning {len(sentences)} sentences against {self.count(self.HOOKS_COLLECTION)} hooks...")
        
        # Scan with sliding window
        for i in range(len(sentences)):
            # Combine window_size sentences
            window_sentences = sentences[i:i + window_size]
            combined_text = ". ".join(s[0] for s in window_sentences)
            timestamp = window_sentences[0][1]
            
            # Search for similar hooks
            matches = await self.search_hooks(
                combined_text, 
                n_results=1,
                min_views=min_views
            )
            
            if matches:
                best_match = matches[0]
                is_potential = best_match.similarity >= similarity_threshold
                
                if is_potential:
                    results.append(SentenceScanResult(
                        sentence=combined_text[:200],
                        timestamp=timestamp,
                        best_match=best_match,
                        is_potential_viral_hook=True
                    ))
        
        # Sort by similarity
        results.sort(key=lambda x: x.best_match.similarity if x.best_match else 0, reverse=True)
        
        print(f"Found {len(results)} potential viral hooks above {similarity_threshold:.0%} threshold")
        
        return results
    
    # =========================================================================
    # GLOBAL HOOK HUNTING (NO TIME LIMITS!)
    # =========================================================================
    
    async def find_global_hook_candidates(
        self,
        body_topic: str,
        transcript_segments: List[Dict],
        top_k: int = 10,
        min_sentence_length: int = 15,
        min_views_for_viral_match: int = 100000
    ) -> List[GlobalHookCandidate]:
        """
        Find the BEST hook candidates from the ENTIRE transcript.
        
        KEY DIFFERENCE: NO TIME LIMITS!
        The perfect hook can be 30 minutes after the body content.
        Like Dieter Lange: Story at 09:00, conclusion at 12:00.
        
        Process:
        1. Extract ALL sentences from transcript with timestamps
        2. Score each sentence for "punchiness" (hook potential)
        3. Score semantic match to the body topic
        4. Compare against known viral hooks (vector store)
        5. Return top-K candidates ranked by combined score
        
        Args:
            body_topic: Summary/topic of the content body (for semantic matching)
            transcript_segments: The FULL transcript (no truncation!)
            top_k: Number of candidates to return
            min_sentence_length: Minimum characters for a valid sentence
            min_views_for_viral_match: Min views for viral hook comparison
            
        Returns:
            List of GlobalHookCandidate, sorted by combined score (best first)
        """
        # Step 1: Extract ALL sentences with timestamps
        all_sentences = self._extract_sentences_with_timestamps(
            transcript_segments, 
            min_length=min_sentence_length
        )
        
        if not all_sentences:
            return []
        
        print(f"   🌍 Global Hook Hunt: Scanning {len(all_sentences)} sentences...")
        
        candidates = []
        
        # Step 2 & 3: Score each sentence
        for sent_text, start_ts, end_ts in all_sentences:
            # Calculate punch score (local, no API call)
            punch_score = self._calculate_punch_score(sent_text)
            
            # Check markers
            contains_conclusion = self._has_conclusion_marker(sent_text)
            contains_number = any(c.isdigit() for c in sent_text[:50])
            is_question = "?" in sent_text
            is_contrarian = self._is_contrarian(sent_text)
            
            # Early filter: Skip low-punch sentences
            if punch_score < 0.3 and not contains_conclusion:
                continue
            
            candidates.append({
                "text": sent_text,
                "start": start_ts,
                "end": end_ts,
                "punch_score": punch_score,
                "contains_conclusion": contains_conclusion,
                "contains_number": contains_number,
                "is_question": is_question,
                "is_contrarian": is_contrarian,
                "word_count": len(sent_text.split())
            })
        
        print(f"   📊 After punch filter: {len(candidates)} candidates remain")
        
        if not candidates:
            return []
        
        # Step 4: Batch semantic scoring with body topic
        # Use ChromaDB's embedding for semantic match
        try:
            scored_candidates = await self._score_semantic_match_batch(
                candidates, 
                body_topic
            )
        except Exception as e:
            print(f"   ⚠️ Semantic scoring failed: {e}")
            scored_candidates = [(c, 0.5) for c in candidates]  # Default score
        
        # Step 5: Compare top candidates against viral hooks
        top_punch_candidates = sorted(
            scored_candidates, 
            key=lambda x: x[0]["punch_score"] * 0.4 + x[1] * 0.6,
            reverse=True
        )[:top_k * 2]  # Get 2x for viral matching
        
        final_candidates = []
        
        for cand, semantic_score in top_punch_candidates:
            # Check viral hook similarity
            viral_sim = 0.0
            matched_hook = None
            
            if self.is_initialized(self.HOOKS_COLLECTION):
                try:
                    matches = await self.search_hooks(
                        cand["text"], 
                        n_results=1,
                        min_views=min_views_for_viral_match
                    )
                    if matches:
                        viral_sim = matches[0].similarity
                        matched_hook = matches[0].hook_text
                except Exception:
                    pass
            
            # Create candidate object
            final_candidates.append(GlobalHookCandidate(
                sentence=cand["text"],
                timestamp=cand["start"],
                end_timestamp=cand["end"],
                semantic_score=semantic_score,
                punch_score=cand["punch_score"],
                contains_conclusion_marker=cand["contains_conclusion"],
                contains_number=cand["contains_number"],
                is_question=cand["is_question"],
                is_contrarian=cand["is_contrarian"],
                word_count=cand["word_count"],
                viral_hook_similarity=viral_sim,
                matched_viral_hook=matched_hook
            ))
        
        # Final ranking: Combined score
        # Punch * 0.3 + Semantic * 0.4 + Viral * 0.2 + Conclusion bonus * 0.1
        def combined_score(c: GlobalHookCandidate) -> float:
            base = c.punch_score * 0.3 + c.semantic_score * 0.4 + c.viral_hook_similarity * 0.2
            if c.contains_conclusion_marker:
                base += 0.1
            if c.is_contrarian:
                base += 0.05
            return base
        
        final_candidates.sort(key=combined_score, reverse=True)
        
        print(f"   ✅ Top hook candidate: \"{final_candidates[0].sentence[:50]}...\" @ {final_candidates[0].timestamp:.0f}s")
        
        return final_candidates[:top_k]
    
    def _extract_sentences_with_timestamps(
        self,
        segments: List[Dict],
        min_length: int = 15
    ) -> List[Tuple[str, float, float]]:
        """Extract all sentences with their timestamps."""
        results = []
        
        for seg in segments:
            text = seg.get("text", "")
            start = seg.get("start", 0)
            end = seg.get("end", start + 1)
            
            # Split into sentences
            sentences = []
            current = ""
            for char in text:
                current += char
                if char in ".!?":
                    if len(current.strip()) >= min_length:
                        sentences.append(current.strip())
                    current = ""
            if len(current.strip()) >= min_length:
                sentences.append(current.strip())
            
            # Distribute timestamps across sentences
            if sentences:
                duration = end - start
                per_sentence = duration / len(sentences)
                for i, sent in enumerate(sentences):
                    sent_start = start + i * per_sentence
                    sent_end = sent_start + per_sentence
                    results.append((sent, sent_start, sent_end))
        
        return results
    
    def _calculate_punch_score(self, text: str) -> float:
        """
        Calculate "punchiness" of a sentence.
        High punch = good hook potential.
        """
        score = 0.5  # Base score
        text_lower = text.lower()
        
        # Short sentences are punchier
        word_count = len(text.split())
        if word_count <= 8:
            score += 0.2
        elif word_count <= 15:
            score += 0.1
        elif word_count > 30:
            score -= 0.2
        
        # Contrarian words boost punch
        contrarian_words = ["nicht", "niemals", "nie", "falsch", "lüge", "irrtum", "fehler", "vergiss"]
        if any(w in text_lower for w in contrarian_words):
            score += 0.15
        
        # Numbers catch attention
        if any(c.isdigit() for c in text[:30]):
            score += 0.1
        
        # Imperatives are punchy
        imperative_starts = ["vergiss", "hör", "schau", "denk", "arbeite", "lerne", "stopp"]
        if any(text_lower.startswith(w) for w in imperative_starts):
            score += 0.15
        
        # Questions create curiosity
        if "?" in text:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _has_conclusion_marker(self, text: str) -> bool:
        """Check if sentence contains conclusion/moral markers."""
        markers = [
            "das bedeutet", "deswegen", "deshalb", "darum",
            "das heißt", "das ist der grund", "fazit",
            "die moral", "die lektion", "lerne daraus",
            "niemals", "immer", "der wichtigste", "das wichtigste"
        ]
        text_lower = text.lower()
        return any(m in text_lower for m in markers)
    
    def _is_contrarian(self, text: str) -> bool:
        """Check if sentence is contrarian/provocative."""
        markers = [
            "nicht", "niemals", "falsch", "bullshit", "müll",
            "lüge", "betrug", "vergiss", "hör auf", "stopp"
        ]
        text_lower = text.lower()
        return any(m in text_lower for m in markers)
    
    async def _score_semantic_match_batch(
        self,
        candidates: List[Dict],
        body_topic: str
    ) -> List[Tuple[Dict, float]]:
        """
        Score semantic match between candidates and body topic.
        Uses ChromaDB's embedding for comparison.
        """
        if not candidates:
            return []
        
        # Create temporary collection for matching
        collection = self._get_collection("_temp_semantic_match")
        
        try:
            # Add body topic
            collection.upsert(
                ids=["body_topic"],
                documents=[body_topic]
            )
            
            # Query all candidates
            results = []
            for cand in candidates:
                query_result = collection.query(
                    query_texts=[cand["text"]],
                    n_results=1
                )
                
                if query_result and query_result.get("distances"):
                    distance = query_result["distances"][0][0]
                    similarity = 1 - (distance / 2)  # Normalize
                    results.append((cand, similarity))
                else:
                    results.append((cand, 0.5))
            
            return results
            
        finally:
            # Cleanup temp collection
            try:
                self._get_client().delete_collection("_temp_semantic_match")
            except Exception:
                pass
    
    # =========================================================================
    # LEGACY COMPATIBILITY
    # =========================================================================
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Legacy search function - searches default collection.
        
        For backwards compatibility with existing code.
        """
        collection = self._get_collection(self.DEFAULT_COLLECTION)
        
        if collection.count() == 0:
            # Try patterns collection as fallback
            return await self.search_patterns(query, n_results)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
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
        Add a single clip to the default collection.
        
        For backwards compatibility.
        """
        collection = self._get_collection(self.DEFAULT_COLLECTION)
        collection.upsert(
            ids=[clip_id],
            documents=[text[:2000]],
            metadatas=[metadata]
        )
    
    async def initialize_from_training_data(
        self,
        min_views: int = 10000,
        batch_size: int = 100
    ) -> int:
        """
        Legacy initialization - now initializes all collections.
        """
        print("Initializing all V3 collections...")
        
        hooks_count = await self.initialize_hooks_collection(min_views=100000)
        patterns_count = await self.initialize_patterns_collection(min_views=min_views)
        
        return hooks_count + patterns_count
    
    def clear(self, collection: str = None):
        """Clear a collection or all collections."""
        client = self._get_client()
        
        if collection:
            try:
                client.delete_collection(collection)
                if collection in self._collections:
                    del self._collections[collection]
                print(f"Cleared collection: {collection}")
            except Exception:
                pass
        else:
            # Clear all
            for coll_name in [self.HOOKS_COLLECTION, self.PATTERNS_COLLECTION, 
                             self.BLUEPRINTS_COLLECTION, self.DEFAULT_COLLECTION]:
                try:
                    client.delete_collection(coll_name)
                except Exception:
                    pass
            self._collections = {}
            print("Cleared all collections")


# =============================================================================
# Helper Functions
# =============================================================================

async def initialize_brain() -> Dict[str, int]:
    """
    Initialize the BRAIN system with V3 collections.
    
    Returns:
        Dict with counts for each collection
    """
    store = VectorStore()
    
    counts = store.get_all_counts()
    
    if counts["hooks"] > 0 and counts["patterns"] > 0:
        print(f"Vector store already initialized:")
        for name, count in counts.items():
            print(f"  {name}: {count}")
        return counts
    
    print("Initializing V3 vector store...")
    await store.initialize_from_training_data()
    
    return store.get_all_counts()


async def scan_for_hooks(
    transcript_segments: List[Dict],
    similarity_threshold: float = 0.75
) -> List[SentenceScanResult]:
    """
    Convenience function to scan a transcript for potential viral hooks.
    
    Args:
        transcript_segments: Transcript segments with text and timestamps
        similarity_threshold: Minimum similarity (0-1) to flag
        
    Returns:
        List of sentences that match known viral hooks
    """
    store = VectorStore()
    return await store.scan_transcript_for_hooks(
        transcript_segments,
        similarity_threshold=similarity_threshold
    )


async def find_global_hooks(
    body_topic: str,
    transcript_segments: List[Dict],
    top_k: int = 10
) -> List[GlobalHookCandidate]:
    """
    Find the best hook candidates from the ENTIRE transcript (no time limits!).
    
    This is the main function for "Global Hook Hunting" - Phase 2 of the
    Editor Workflow.
    
    The hook can be ANYWHERE in the video:
    - 5 minutes before the body
    - 20 minutes after the body
    - In the recap at the very end
    
    Args:
        body_topic: The topic/summary of the content body
        transcript_segments: The COMPLETE transcript (all segments)
        top_k: Number of top candidates to return
        
    Returns:
        List of GlobalHookCandidate sorted by combined score (best first)
    
    Example:
        >>> body_topic = "Geschichte über alten Mann der Kindern Geld gibt"
        >>> hooks = await find_global_hooks(body_topic, transcript_segments)
        >>> best_hook = hooks[0]
        >>> print(f"Best hook at {best_hook.timestamp}s: {best_hook.sentence}")
        # Output: "Best hook at 720s: Arbeite niemals für Geld."
    """
    store = VectorStore()
    return await store.find_global_hook_candidates(
        body_topic=body_topic,
        transcript_segments=transcript_segments,
        top_k=top_k
    )

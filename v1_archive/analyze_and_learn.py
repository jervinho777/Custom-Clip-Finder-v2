#!/usr/bin/env python3
"""
📊 WORKFLOW 1: ANALYZE & LEARN

This script handles ALL training, analysis and pattern learning.
Run this when you have new GOAT clips or want to update the AI brain.

WHAT IT DOES:
1. Load/Update training data (CSV + Videos)
2. Transcribe new videos (with caching)
3. AI + ML Pattern Recognition
4. Save learned patterns (the "brain" for clip creation)

OUTPUT:
- data/learned_patterns.json (AI learned patterns)
- data/ml_model.pkl (ML model for scoring)
- data/training_stats.json (Statistics & insights)
"""

import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

import numpy as np
import pandas as pd
from anthropic import Anthropic

# Optional ML imports
try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    import pickle
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ sklearn not installed - ML features disabled")

# Optional Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class AnalyzeAndLearn:
    """
    Main class for training data analysis and pattern learning
    """
    
    def __init__(self):
        # API
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        
        # Paths
        self.data_dir = Path("data")
        self.training_dir = self.data_dir / "training"
        self.cache_dir = self.data_dir / "cache" / "transcripts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Output files
        self.patterns_file = self.data_dir / "learned_patterns.json"
        self.model_file = self.data_dir / "ml_model.pkl"
        self.stats_file = self.data_dir / "training_stats.json"
        
        # Data
        self.clips = []
        self.patterns = {}
        
        print("="*70)
        print("📊 ANALYZE & LEARN - Training System")
        print("="*70)
        print(f"   🤖 AI: {'Connected' if self.client else 'Not available'}")
        print(f"   📈 ML: {'Available' if ML_AVAILABLE else 'Not available'}")
        print(f"   🎤 Whisper: {'Available' if WHISPER_AVAILABLE else 'Not available'}")
    
    # =========================================================================
    # DATA LOADING
    # =========================================================================
    
    def load_training_data(self, csv_path=None, videos_dir=None):
        """
        Load or update training data
        
        Args:
            csv_path: Path to goat_clips.csv (auto-detected if None)
            videos_dir: Path to video files (auto-detected if None)
        """
        
        print(f"\n{'='*70}")
        print("📥 LOADING TRAINING DATA")
        print(f"{'='*70}")
        
        # Find CSV
        if csv_path is None:
            csv_candidates = [
                self.training_dir / "goat_clips.csv",
                self.data_dir / "goat_clips.csv",
                Path("goat_clips.csv"),
            ]
            for path in csv_candidates:
                if path.exists():
                    csv_path = path
                    break
        
        if csv_path is None or not Path(csv_path).exists():
            print("❌ No CSV found!")
            return None
        
        print(f"   📄 CSV: {csv_path}")
        
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"   📊 Rows: {len(df)}")
        
        # Find videos directory
        if videos_dir is None:
            video_candidates = [
                self.training_dir / "goat_clips",
                self.data_dir / "videos",
                Path("data/training/goat_clips"),
            ]
            for path in video_candidates:
                if path.exists() and list(path.glob("*.mp4")):
                    videos_dir = path
                    break
        
        if videos_dir:
            mp4_count = len(list(Path(videos_dir).glob("*.mp4")))
            print(f"   🎬 Videos: {mp4_count} MP4 files in {videos_dir}")
        
        # Load existing training data if available
        training_data_path = self.training_dir / "goat_training_data.json"
        if training_data_path.exists():
            with open(training_data_path, 'r') as f:
                self.clips = json.load(f)
            print(f"   📦 Existing data: {len(self.clips)} clips with transcripts")
        else:
            self.clips = []
        
        # Check for new clips that need processing
        existing_ids = {c.get('video_id') for c in self.clips}
        
        new_clips_needed = 0
        for idx, row in df.iterrows():
            video_id = self._extract_video_id(row.get('URL', '')) or f"clip_{idx+1}"
            if video_id not in existing_ids:
                new_clips_needed += 1
        
        if new_clips_needed > 0:
            print(f"\n   🆕 New clips to process: {new_clips_needed}")
            update = input("   Process new clips? (y/n): ").strip().lower()
            if update == 'y':
                self._process_new_clips(df, videos_dir)
        
        # Calculate relative performance
        self._calculate_relative_performance()
        
        print(f"\n✅ Loaded {len(self.clips)} clips")
        
        return self.clips
    
    def _extract_video_id(self, url):
        """Extract video ID from URL"""
        if not url or pd.isna(url):
            return None
        
        url = str(url)
        
        if 'instagram.com' in url:
            match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            if match: return f"ig_{match.group(1)}"
        elif 'tiktok.com' in url:
            match = re.search(r'/video/(\d+)', url)
            if match: return f"tt_{match.group(1)}"
        elif 'youtube.com' in url or 'youtu.be' in url:
            match = re.search(r'/shorts/([A-Za-z0-9_-]+)', url)
            if match: return f"yt_{match.group(1)}"
        elif 'facebook.com' in url:
            match = re.search(r'/reel/(\d+)', url)
            if match: return f"fb_{match.group(1)}"
        
        return None
    
    def _process_new_clips(self, df, videos_dir):
        """Process new clips from CSV"""
        # Implementation for processing new clips
        # This would transcribe new videos and add them to self.clips
        print("   🔄 Processing new clips...")
        # TODO: Implement batch processing
        pass
    
    def _calculate_relative_performance(self):
        """Calculate relative performance per account"""
        
        if not self.clips:
            return
        
        # Group by account
        by_account = defaultdict(list)
        for clip in self.clips:
            account = clip.get('account', 'unknown')
            by_account[account].append(clip)
        
        # Calculate relative performance
        for account, clips in by_account.items():
            views = [c['performance']['views'] for c in clips if c.get('performance')]
            if not views:
                continue
            
            median = np.median(views)
            
            for clip in clips:
                clip_views = clip.get('performance', {}).get('views', 0)
                clip['relative_performance'] = clip_views / median if median > 0 else 1
                clip['is_outlier'] = clip['relative_performance'] >= 2.0
        
        # Stats
        outliers = sum(1 for c in self.clips if c.get('is_outlier'))
        print(f"   📊 Outliers (2x+ performance): {outliers} clips")
    
    # =========================================================================
    # AI PATTERN LEARNING
    # =========================================================================
    
    def learn_patterns(self, sample_size=40):
        """
        Use AI to learn patterns from training data
        
        Analyzes outliers vs normal clips to find what makes content viral
        """
        
        if not self.client:
            print("❌ No API key - cannot learn patterns")
            return None
        
        if not self.clips:
            print("❌ No training data loaded")
            return None
        
        print(f"\n{'='*70}")
        print("🧠 AI PATTERN LEARNING")
        print(f"{'='*70}")
        
        # Get outliers and normal clips
        outliers = [c for c in self.clips if c.get('is_outlier') and c.get('content')]
        normal = [c for c in self.clips if not c.get('is_outlier') and c.get('content')]
        
        print(f"   📊 Outliers with content: {len(outliers)}")
        print(f"   📊 Normal with content: {len(normal)}")
        
        if len(outliers) < 5:
            print("⚠️ Not enough outliers for pattern learning")
            return None
        
        # Sample for AI analysis
        outlier_samples = sorted(outliers, key=lambda x: x.get('relative_performance', 1), reverse=True)[:sample_size]
        normal_samples = normal[:sample_size]
        
        # Prepare data
        outlier_data = [{
            'content': c.get('content', '')[:800],
            'views': c['performance']['views'],
            'outperformance': f"{c.get('relative_performance', 1):.1f}x",
            'account': c.get('account', '')
        } for c in outlier_samples]
        
        normal_data = [{
            'content': c.get('content', '')[:800],
            'views': c['performance']['views'],
            'account': c.get('account', '')
        } for c in normal_samples]
        
        prompt = self._build_learning_prompt(outlier_data, normal_data)
        
        print("\n   🔄 Sending to AI for pattern analysis...")
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                self.patterns = json.loads(json_match.group())
                
                # Add metadata
                self.patterns['metadata'] = {
                    'learned_at': datetime.now().isoformat(),
                    'outliers_analyzed': len(outlier_samples),
                    'normal_analyzed': len(normal_samples),
                    'total_training_clips': len(self.clips)
                }
                
                # Save
                with open(self.patterns_file, 'w') as f:
                    json.dump(self.patterns, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Patterns learned and saved!")
                print(f"   📁 {self.patterns_file}")
                print(f"   🔥 {len(self.patterns.get('viral_patterns', []))} viral patterns found")
                
                self._print_pattern_summary()
                
                return self.patterns
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def _build_learning_prompt(self, outlier_data, normal_data):
        """Build the AI prompt for pattern learning"""
        
        return f"""Du bist ein Elite-Analyst für virale Video-Content mit Expertise in:
- Social Media Algorithmen (Watchtime-Optimierung)
- Hook Point Methodik (3-Sekunden Welt)
- Cialdini's Principles of Persuasion
- Storytelling & Content-Struktur

ANALYSE-AUFTRAG:
Vergleiche diese zwei Gruppen von Video-Transcripts und extrahiere KONKRETE, ACTIONABLE Patterns.

GRUPPE A - VIRAL OUTLIERS (2x-10x besser als Account-Durchschnitt):
{json.dumps(outlier_data, indent=2, ensure_ascii=False)}

GRUPPE B - NORMALE PERFORMER:
{json.dumps(normal_data, indent=2, ensure_ascii=False)}

WICHTIG - Analysiere nach diesen Frameworks:

1. DIE 12 VIRALITY TRIGGERS:
   - Mass Appeal, Humor, Berühmtheiten, Headline/Hook
   - Storytime, Kontroverse, Learning, Shareability
   - Einfachheit, Primacy-Recency, Information Gap, Trend

2. WATCHTIME-OPTIMIERUNG:
   - Hook (0-3s): Sofort Spannung, Information Gap
   - Loop-Struktur: Unvollständige Loops
   - Pattern Interrupts: Alle 5-7 Sekunden
   - Emotionale Achterbahn

3. CIALDINI PRINCIPLES:
   - Reciprocity, Commitment, Social Proof
   - Authority, Liking, Scarcity

Antworte EXAKT in diesem JSON-Format:

{{
    "viral_patterns": [
        {{
            "id": "VP001",
            "name": "Pattern Name",
            "description": "Detaillierte Beschreibung",
            "detection_keywords": ["keyword1", "keyword2"],
            "detection_rules": "Wie erkennt man es",
            "frequency_viral": 0.8,
            "frequency_normal": 0.2,
            "impact_score": 0.9,
            "examples": ["Beispiel aus den Daten"]
        }}
    ],
    
    "hook_patterns": {{
        "winning_hooks": [
            {{
                "type": "Hook-Typ",
                "template": "Formel/Template",
                "examples": ["Beispiel 1"],
                "effectiveness": 0.9
            }}
        ],
        "hook_red_flags": ["Was NICHT funktioniert"],
        "strong_first_words": ["Wort1", "Wort2"],
        "weak_first_words": ["Wort1", "Wort2"]
    }},
    
    "content_structure": {{
        "optimal_flow": "Hook → Loop → Content → Payoff",
        "timing": {{
            "hook_duration": "0-3 Sekunden",
            "first_loop": "3-10 Sekunden",
            "pattern_interrupts": "alle 5-7 Sekunden"
        }},
        "key_elements": ["Element 1", "Element 2"]
    }},
    
    "emotional_triggers": {{
        "primary_emotions": ["Emotion 1", "Emotion 2"],
        "trigger_words_german": ["Wort1", "Wort2"],
        "emotional_arc": "Beschreibung des emotionalen Verlaufs"
    }},
    
    "scoring_criteria": {{
        "hook_strength": {{"weight": 0.25, "indicators": ["..."]}},
        "information_gap": {{"weight": 0.20, "indicators": ["..."]}},
        "emotional_intensity": {{"weight": 0.15, "indicators": ["..."]}},
        "mass_appeal": {{"weight": 0.15, "indicators": ["..."]}},
        "simplicity": {{"weight": 0.10, "indicators": ["..."]}},
        "storytime": {{"weight": 0.10, "indicators": ["..."]}},
        "shareability": {{"weight": 0.05, "indicators": ["..."]}}
    }},
    
    "red_flags": [
        "Warnung 1",
        "Warnung 2"
    ],
    
    "quick_checks": [
        {{"check": "Frage mit Ja/Nein", "impact": "+10 oder -5"}}
    ],
    
    "actionable_insights": [
        "Konkrete Handlungsempfehlung 1",
        "Konkrete Handlungsempfehlung 2"
    ]
}}"""
    
    def _print_pattern_summary(self):
        """Print summary of learned patterns"""
        
        if not self.patterns:
            return
        
        print(f"\n📋 LEARNED PATTERNS SUMMARY:")
        print("-"*50)
        
        # Viral patterns
        for p in self.patterns.get('viral_patterns', [])[:5]:
            print(f"\n   🔥 {p.get('name', 'Unknown')}")
            print(f"      Impact: {p.get('impact_score', 0)*100:.0f}%")
            print(f"      {p.get('description', '')[:80]}...")
        
        # Hook patterns
        hooks = self.patterns.get('hook_patterns', {}).get('winning_hooks', [])
        if hooks:
            print(f"\n   🪝 TOP HOOKS:")
            for h in hooks[:3]:
                print(f"      • {h.get('type')}: {h.get('template', '')[:50]}")
    
    # =========================================================================
    # ML MODEL TRAINING
    # =========================================================================
    
    def train_ml_model(self):
        """
        Train ML model for virality scoring
        """
        
        if not ML_AVAILABLE:
            print("❌ sklearn not installed")
            return None
        
        if not self.clips:
            print("❌ No training data")
            return None
        
        print(f"\n{'='*70}")
        print("📈 TRAINING ML MODEL")
        print(f"{'='*70}")
        
        # Extract features
        features_list = []
        labels = []
        
        for clip in self.clips:
            content = clip.get('content', '')
            if not content:
                continue
            
            features = self._extract_ml_features(content)
            features_list.append(features)
            labels.append(1 if clip.get('is_outlier') else 0)
        
        if len(features_list) < 50:
            print(f"⚠️ Only {len(features_list)} clips with content - need more data")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(features_list)
        X = df.fillna(0)
        y = np.array(labels)
        
        print(f"   📊 Features: {len(df.columns)}")
        print(f"   📊 Samples: {len(X)}")
        print(f"   📊 Outliers: {sum(y)} ({sum(y)/len(y)*100:.1f}%)")
        
        # Train
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        cv_scores = cross_val_score(model, X, y, cv=5)
        
        print(f"\n   📈 Results:")
        print(f"      Train Accuracy: {train_acc:.2%}")
        print(f"      Test Accuracy: {test_acc:.2%}")
        print(f"      CV Score: {cv_scores.mean():.2%} (+/- {cv_scores.std()*2:.2%})")
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': df.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n   🎯 Top Features:")
        for _, row in importance.head(10).iterrows():
            print(f"      {row['feature']:25s} {row['importance']:.3f}")
        
        # Save
        with open(self.model_file, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': list(df.columns),
                'scaler': None,  # Add if needed
                'trained_at': datetime.now().isoformat()
            }, f)
        
        print(f"\n✅ Model saved: {self.model_file}")
        
        return model
    
    def _extract_ml_features(self, content):
        """Extract ML features from content"""
        
        content_lower = content.lower()
        words = content.split()
        
        features = {}
        
        # Basic stats
        features['word_count'] = len(words)
        features['char_count'] = len(content)
        features['avg_word_length'] = np.mean([len(w) for w in words]) if words else 0
        
        # Questions & Exclamations
        features['question_count'] = content.count('?')
        features['exclamation_count'] = content.count('!')
        
        # Hook indicators (first 50 chars)
        first_50 = content_lower[:50]
        hook_words = ['warum', 'wie', 'was', 'wann', 'geheimnis', 'fehler', 'trick', 'niemals', 'immer']
        features['hook_word_count'] = sum(1 for w in hook_words if w in first_50)
        
        # Emotional words
        emotion_words = ['unglaublich', 'krass', 'heftig', 'wahnsinn', 'schockierend', 'liebe', 'hass', 'angst']
        features['emotion_count'] = sum(1 for w in emotion_words if w in content_lower)
        
        # Numbers
        features['number_count'] = len(re.findall(r'\d+', content))
        
        # Personal address
        personal = ['du', 'dein', 'dir', 'dich', 'ihr', 'euch']
        features['personal_count'] = sum(content_lower.count(f' {w} ') for w in personal)
        
        # Story indicators
        story_words = ['als', 'dann', 'plötzlich', 'eines tages', 'geschichte']
        features['story_count'] = sum(1 for w in story_words if w in content_lower)
        
        return features
    
    # =========================================================================
    # SAVE STATISTICS
    # =========================================================================
    
    def save_stats(self):
        """Save training statistics"""
        
        if not self.clips:
            return
        
        stats = {
            'total_clips': len(self.clips),
            'clips_with_content': sum(1 for c in self.clips if c.get('content')),
            'outliers': sum(1 for c in self.clips if c.get('is_outlier')),
            'total_views': sum(c.get('performance', {}).get('views', 0) for c in self.clips),
            'accounts': len(set(c.get('account', '') for c in self.clips)),
            'updated_at': datetime.now().isoformat()
        }
        
        # Top accounts
        by_account = defaultdict(list)
        for clip in self.clips:
            by_account[clip.get('account', 'unknown')].append(clip)
        
        stats['top_accounts'] = [
            {'account': acc, 'clips': len(clips), 'median_views': int(np.median([c['performance']['views'] for c in clips]))}
            for acc, clips in sorted(by_account.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        ]
        
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📊 Stats saved: {self.stats_file}")
    
    # =========================================================================
    # MAIN WORKFLOW
    # =========================================================================
    
    def run_full_analysis(self):
        """Run complete analysis workflow"""
        
        print("\n" + "="*70)
        print("🚀 FULL ANALYSIS WORKFLOW")
        print("="*70)
        
        # 1. Load data
        self.load_training_data()
        
        if not self.clips:
            print("\n❌ No data to analyze")
            return
        
        # 2. Learn patterns with AI
        if self.client:
            print("\n" + "-"*50)
            learn = input("🧠 Run AI pattern learning? (y/n): ").strip().lower()
            if learn == 'y':
                self.learn_patterns()
        
        # 3. Train ML model
        if ML_AVAILABLE:
            print("\n" + "-"*50)
            train = input("📈 Train ML model? (y/n): ").strip().lower()
            if train == 'y':
                self.train_ml_model()
        
        # 4. Save stats
        self.save_stats()
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE!")
        print("="*70)
        print(f"\n📁 Output files:")
        print(f"   • {self.patterns_file}")
        print(f"   • {self.model_file}")
        print(f"   • {self.stats_file}")
        print(f"\n🎬 Ready to create clips with: python create_clips.py")


def main():
    """Main entry point"""
    
    analyzer = AnalyzeAndLearn()
    
    print("\n" + "-"*50)
    print("📝 OPTIONS:")
    print("   1. 🚀 Full Analysis (recommended)")
    print("   2. 📥 Load/Update Training Data only")
    print("   3. 🧠 Learn Patterns (AI) only")
    print("   4. 📈 Train ML Model only")
    print("   5. 📊 Show Statistics")
    print("-"*50)
    
    choice = input("\nChoice (1-5): ").strip()
    
    if choice == '1':
        analyzer.run_full_analysis()
    elif choice == '2':
        analyzer.load_training_data()
        analyzer.save_stats()
    elif choice == '3':
        analyzer.load_training_data()
        analyzer.learn_patterns()
    elif choice == '4':
        analyzer.load_training_data()
        analyzer.train_ml_model()
    elif choice == '5':
        if analyzer.stats_file.exists():
            with open(analyzer.stats_file, 'r') as f:
                stats = json.load(f)
            print(json.dumps(stats, indent=2))
        else:
            print("No stats file found")


if __name__ == "__main__":
    main()

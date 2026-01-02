#!/usr/bin/env python3
"""
ULTIMATE ALGORITHM-OPTIMIZED FEATURE EXTRACTOR

Basierend auf:
1. Social Media Algorithmus (Watchtime > all)
2. Hook Point (3-Second World)
3. Psychology of Persuasion (Cialdini)
4. 12 Viral Content Criteria

METRIKEN-HIERARCHIE (wie Algorithmus denkt):
1. Watch Time (50% weight) - ABSOLUTE PRIORITÄT
2. Completion Rate (25%)
3. Engagement (15%)
4. Session Duration (10%)

GOAL: "Make content so good people cannot physically scroll past"
"""

import librosa
import numpy as np
from typing import Dict, List
import re
from collections import Counter

class UltimateFeatureExtractor:
    """
    Extrahiert Features die DIREKT mit Algorithmus-Success korrelieren
    
    Categories:
    1. HOOK FEATURES (0-3s) - KRITISCH für Initial Test
    2. RETENTION MECHANICS - Pattern Interrupts, Loops, Payoffs
    3. PSYCHOLOGICAL TRIGGERS - Cialdini Principles
    4. 12 VIRAL CRITERIA - Mass Appeal bis Trend
    5. ALGORITHM ALIGNMENT - Watchtime optimization
    """
    
    def __init__(self):
        self.viral_criteria = [
            'mass_appeal', 'humor', 'celebrity', 'headline_loop',
            'storytime', 'controversy', 'learning', 'shareability',
            'simplicity', 'primacy_recency', 'information_gap', 'trend'
        ]
        
        self.cialdini_triggers = [
            'reciprocity', 'commitment', 'social_proof',
            'authority', 'liking', 'scarcity'
        ]
    
    def extract_all_features(self, audio_path: str, transcript: Dict) -> Dict:
        """Extract complete feature set - Algorithm optimized"""
        
        features = {}
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=22050)
        duration = librosa.get_duration(y=y, sr=sr)
        
        segments = transcript.get('segments', [])
        text = transcript.get('text', '')
        
        # === CRITICAL: HOOK FEATURES (0-3s) ===
        # Algorithm zeigt zuerst kleiner Testgruppe
        # Wenn Hook fails → Video stirbt sofort
        hook_features = self._extract_hook_features(y, sr, segments, duration)
        features.update(hook_features)
        
        # === RETENTION MECHANICS ===
        # Jede Sekunde muss Grund geben weiterzuschauen
        retention_features = self._extract_retention_mechanics(y, sr, segments, text)
        features.update(retention_features)
        
        # === 12 VIRAL CRITERIA ===
        viral_features = self._extract_viral_criteria(text, segments, y, sr)
        features.update(viral_features)
        
        # === PSYCHOLOGICAL TRIGGERS ===
        psych_features = self._extract_cialdini_triggers(text, segments)
        features.update(psych_features)
        
        # === ALGORITHM ALIGNMENT ===
        algo_features = self._extract_algorithm_features(y, sr, segments, duration)
        features.update(algo_features)
        
        # === BASIC FEATURES ===
        basic_features = self._extract_basic_features(y, sr, text, duration)
        features.update(basic_features)
        
        return features
    
    # ========================================
    # HOOK FEATURES (0-3s) - KRITISCH!
    # ========================================
    
    def _extract_hook_features(self, y, sr, segments, duration):
        """
        First 3 seconds = Leben oder Tod des Videos
        
        Hook Point Prinzip: 3-Second World
        - 60 BILLION messages/day
        - Average person sees 4000-10000 ads/day
        - Attention span → 3 seconds
        
        MUST HAVE:
        - Sofort Spannung
        - Klare Value Proposition
        - Visueller Stop-Trigger
        - Information Gap
        """
        
        hook_samples = min(int(3 * sr), len(y))
        hook_audio = y[:hook_samples]
        
        # Hook Energy (Stop-Trigger)
        hook_rms = librosa.feature.rms(y=hook_audio)[0]
        hook_energy = float(np.mean(hook_rms))
        hook_energy_peak = float(np.max(hook_rms))
        
        # Hook Pitch Variance (Emotional modulation)
        pitches, magnitudes = librosa.piptrack(y=hook_audio, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        hook_pitch_variance = float(np.std(pitch_values)) if pitch_values else 0
        
        # Hook Text Analysis
        hook_segments = [s for s in segments if s['start'] < 3]
        hook_text = ' '.join(s['text'] for s in hook_segments)
        
        # Information Gap (macht neugierig?)
        gap_triggers = [
            'aber', 'jedoch', 'was wenn', 'stell dir vor',
            'weißt du', 'hast du', 'kannst du', 'warum',
            'wie', 'wann', 'geheimnis', 'niemand', 'unglaublich'
        ]
        hook_information_gap = sum(
            hook_text.lower().count(trigger) for trigger in gap_triggers
        )
        
        # Question in Hook (opens loop)
        hook_has_question = 1 if '?' in hook_text else 0
        hook_question_marks = hook_text.count('?')
        
        # Value Proposition indicators
        value_words = [
            'lerne', 'zeige', 'entdecke', 'finde', 'vermeide',
            'verdiene', 'spare', 'gewinne', 'erreiche', 'schaffe'
        ]
        hook_value_proposition = sum(
            hook_text.lower().count(word) for word in value_words
        )
        
        # Urgency/FOMO in hook
        urgency_words = ['jetzt', 'sofort', 'heute', 'schnell', 'limitiert']
        hook_urgency = sum(hook_text.lower().count(word) for word in urgency_words)
        
        # Word count (optimal: 7-15 words)
        hook_word_count = len(hook_text.split())
        
        # Hook completeness score
        hook_completeness = min(1.0, (
            (hook_energy > 0.3) * 0.3 +
            (hook_pitch_variance > 0.2) * 0.2 +
            (hook_information_gap > 0) * 0.2 +
            (hook_value_proposition > 0 or hook_has_question) * 0.3
        ))
        
        return {
            # Energy
            'hook_energy': hook_energy,
            'hook_energy_peak': hook_energy_peak,
            
            # Audio variation
            'hook_pitch_variance': hook_pitch_variance,
            
            # Text triggers
            'hook_information_gap': hook_information_gap,
            'hook_has_question': hook_has_question,
            'hook_question_marks': hook_question_marks,
            'hook_value_proposition': hook_value_proposition,
            'hook_urgency': hook_urgency,
            'hook_word_count': hook_word_count,
            
            # Composite
            'hook_completeness_score': hook_completeness
        }
    
    # ========================================
    # RETENTION MECHANICS
    # ========================================
    
    def _extract_retention_mechanics(self, y, sr, segments, text):
        """
        Algorithmus optimiert auf Watchtime
        
        Retention Mechanics:
        - Pattern Interrupts (jede 10-15s)
        - Unvollständige Loops (Zeigarnik Effect)
        - Mini-Payoffs (keep watching)
        - Emotional Achterbahn (nicht Flatline)
        - Pacing Variation
        """
        
        # Pattern Interrupts (energy spikes)
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = np.mean(rms)
        energy_std = np.std(rms)
        
        # Significant spikes (>1.5 std above mean)
        spike_threshold = energy_mean + 1.5 * energy_std
        energy_spikes = np.where(rms > spike_threshold)[0]
        pattern_interrupts = len(energy_spikes)
        
        # Pattern interrupt frequency (optimal: every 10-15s)
        duration = len(y) / sr
        interrupts_per_minute = (pattern_interrupts / duration) * 60 if duration > 0 else 0
        
        # Emotional Variance (pitch variation over time)
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        pitch_std = np.std(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        emotional_variance = float(pitch_std / pitch_mean if pitch_mean > 0 else 0)
        
        # Pacing Changes (segment length variance)
        if segments and len(segments) > 1:
            segment_lengths = [s['end'] - s['start'] for s in segments]
            pacing_variance = float(np.std(segment_lengths))
            pacing_changes = int(np.sum(np.abs(np.diff(segment_lengths)) > 0.5))
        else:
            pacing_variance = 0
            pacing_changes = 0
        
        # Unvollständige Loops (Zeigarnik Effect)
        loop_indicators = [
            'aber', 'jedoch', 'und dann', 'plötzlich', 'warte',
            'moment', 'bevor', 'erst', 'nachdem', 'bis'
        ]
        unfinished_loops = sum(text.lower().count(word) for word in loop_indicators)
        
        # Teaser/Promises (keep watching)
        teaser_phrases = [
            'gleich', 'später', 'am ende', 'zum schluss', 'warte ab',
            'du wirst sehen', 'zeige ich dir', 'erkläre ich'
        ]
        teaser_count = sum(text.lower().count(phrase) for phrase in teaser_phrases)
        
        # Energy consistency (avoid flatline)
        energy_changes = int(np.sum(np.abs(np.diff(rms)) > 0.05))
        energy_flatline_risk = 1.0 - min(1.0, energy_changes / (len(rms) * 0.1))
        
        return {
            'pattern_interrupts': pattern_interrupts,
            'interrupts_per_minute': float(interrupts_per_minute),
            'emotional_variance': emotional_variance,
            'pacing_variance': pacing_variance,
            'pacing_changes': pacing_changes,
            'unfinished_loops': unfinished_loops,
            'teaser_count': teaser_count,
            'energy_changes': energy_changes,
            'energy_flatline_risk': float(energy_flatline_risk)
        }
    
    # ========================================
    # 12 VIRAL CRITERIA
    # ========================================
    
    def _extract_viral_criteria(self, text, segments, y, sr):
        """
        12 Ansätze für viralen Content:
        
        a. Mass Appeal - Breite Masse
        b. Humor - Lustig
        c. Celebrity - Berühmtheiten
        d. Headline Loop - Opens Loops
        e. Storytime - Spannende Geschichte
        f. Controversy - Meinungsverschiedenheiten
        g. Learning - Direkt anwendbar
        h. Shareability - Weitersenden?
        i. Simplicity - Nach 1x klar
        j. Primacy-Recency - Erster & Letzter Eindruck
        k. Information Gap - Nach 1. Satz dranbleiben
        l. Trend - Neu/Trending
        """
        
        text_lower = text.lower()
        
        # a. MASS APPEAL
        # Universal topics: Familie, Geld, Gesundheit, Beziehungen
        universal_topics = [
            'familie', 'kind', 'eltern', 'liebe', 'beziehung',
            'geld', 'reich', 'erfolg', 'gesundheit', 'glück',
            'karriere', 'leben', 'menschen'
        ]
        mass_appeal_score = sum(text_lower.count(topic) for topic in universal_topics)
        mass_appeal_score = min(1.0, mass_appeal_score / 10)  # Normalize
        
        # b. HUMOR
        humor_indicators = [
            'haha', 'lol', 'lustig', 'witzig', 'komisch',
            'lachen', 'spaß', '😂', '😄', '🤣'
        ]
        humor_score = sum(text_lower.count(ind) for ind in humor_indicators)
        humor_score = min(1.0, humor_score / 5)
        
        # c. CELEBRITY (Name recognition)
        # Check for proper nouns (capitalized words)
        words = text.split()
        proper_nouns = sum(1 for w in words if w and w[0].isupper() and len(w) > 2)
        celebrity_score = min(1.0, proper_nouns / 20)
        
        # d. HEADLINE LOOP
        # Opens curiosity loops
        loop_openers = [
            'warum', 'wie', 'was', 'wann', 'wo', 'wer',
            'geheimnis', 'trick', 'methode', 'weg', 'lösung',
            'niemand', 'jeder', 'alle', 'kein'
        ]
        headline_loop_score = sum(text_lower.count(opener) for opener in loop_openers)
        headline_loop_score = min(1.0, headline_loop_score / 10)
        
        # e. STORYTIME
        # Narrative indicators
        story_markers = [
            'ich', 'mein', 'mir', 'mich',
            'war', 'hatte', 'wurde', 'kam',
            'dann', 'danach', 'plötzlich', 'endlich',
            'geschichte', 'erlebnis', 'erfahrung'
        ]
        storytime_score = sum(text_lower.count(marker) for marker in story_markers)
        storytime_score = min(1.0, storytime_score / 20)
        
        # f. CONTROVERSY
        controversy_words = [
            'falsch', 'schlecht', 'problem', 'fehler', 'lüge',
            'skandal', 'schock', 'unglaublich', 'gefährlich',
            'verbieten', 'gegen', 'kritik', 'streit'
        ]
        controversy_score = sum(text_lower.count(word) for word in controversy_words)
        controversy_score = min(1.0, controversy_score / 8)
        
        # g. LEARNING
        learning_indicators = [
            'lerne', 'tipp', 'trick', 'methode', 'strategie',
            'wie du', 'so kannst', 'damit du', 'schritt',
            'anleitung', 'tutorial', 'zeige', 'erkläre'
        ]
        learning_score = sum(text_lower.count(ind) for ind in learning_indicators)
        learning_score = min(1.0, learning_score / 8)
        
        # h. SHAREABILITY
        share_triggers = [
            'teile', 'sende', 'zeige', 'tag', 'freund',
            'jeder', 'alle', 'unglaublich', 'krass', 'wow',
            'schau', 'guck', 'sieh'
        ]
        shareability_score = sum(text_lower.count(trigger) for trigger in share_triggers)
        shareability_score = min(1.0, shareability_score / 6)
        
        # i. SIMPLICITY
        # Simple language, short sentences
        words_list = text.split()
        avg_word_length = np.mean([len(w) for w in words_list]) if words_list else 0
        simplicity_score = 1.0 - min(1.0, (avg_word_length - 4) / 6)  # Optimal: 4-6 chars
        
        # j. PRIMACY-RECENCY
        # First & last impression quality
        first_10_percent = ' '.join([s['text'] for s in segments[:max(1, len(segments)//10)]])
        last_10_percent = ' '.join([s['text'] for s in segments[-max(1, len(segments)//10):]])
        
        # Check if starts/ends strong
        strong_start_words = ['warum', 'wie', 'unglaublich', 'schock', 'geheimnis']
        strong_end_words = ['jetzt', 'sofort', 'vergiss nicht', 'denk dran', 'wichtig']
        
        primacy_score = sum(first_10_percent.lower().count(w) for w in strong_start_words)
        recency_score = sum(last_10_percent.lower().count(w) for w in strong_end_words)
        primacy_recency_score = min(1.0, (primacy_score + recency_score) / 4)
        
        # k. INFORMATION GAP
        # Already covered in hook, but check throughout
        gap_phrases = [
            'aber', 'jedoch', 'was wenn', 'stell dir vor',
            'weißt du was', 'rate mal', 'das problem',
            'das geheimnis', 'der trick'
        ]
        information_gap_score = sum(text_lower.count(phrase) for phrase in gap_phrases)
        information_gap_score = min(1.0, information_gap_score / 6)
        
        # l. TREND
        # Trending topics/words (simplified: recency indicators)
        trend_words = [
            'neu', 'aktuell', 'trend', 'viral', 'jetzt',
            '2024', '2025', 'heute', 'gerade', 'momentan'
        ]
        trend_score = sum(text_lower.count(word) for word in trend_words)
        trend_score = min(1.0, trend_score / 5)
        
        return {
            'mass_appeal': float(mass_appeal_score),
            'humor': float(humor_score),
            'celebrity': float(celebrity_score),
            'headline_loop': float(headline_loop_score),
            'storytime': float(storytime_score),
            'controversy': float(controversy_score),
            'learning': float(learning_score),
            'shareability': float(shareability_score),
            'simplicity': float(simplicity_score),
            'primacy_recency': float(primacy_recency_score),
            'information_gap': float(information_gap_score),
            'trend': float(trend_score)
        }
    
    # ========================================
    # CIALDINI PSYCHOLOGICAL TRIGGERS
    # ========================================
    
    def _extract_cialdini_triggers(self, text, segments):
        """
        Psychology of Persuasion - 6 Principles:
        
        1. Reciprocity - Give & Take
        2. Commitment & Consistency - Small yes → Big yes
        3. Social Proof - Everyone does it
        4. Authority - Expert/Celebrity
        5. Liking - Similarity, Compliments
        6. Scarcity - Limited, Exclusive
        """
        
        text_lower = text.lower()
        
        # 1. RECIPROCITY
        reciprocity_words = [
            'kostenlos', 'gratis', 'schenke', 'gebe', 'teile',
            'für dich', 'bonus', 'geschenk', 'freebie'
        ]
        reciprocity_score = sum(text_lower.count(word) for word in reciprocity_words)
        
        # 2. COMMITMENT & CONSISTENCY
        commitment_phrases = [
            'schritt', 'zuerst', 'dann', 'als nächstes',
            'beginnst du', 'fang an', 'starte', 'probiere'
        ]
        commitment_score = sum(text_lower.count(phrase) for phrase in commitment_phrases)
        
        # 3. SOCIAL PROOF
        social_proof_words = [
            'millionen', 'tausende', 'viele', 'alle', 'jeder',
            'beweis', 'studie', 'forschung', 'bewertung',
            'andere', 'menschen', 'nutzer'
        ]
        social_proof_score = sum(text_lower.count(word) for word in social_proof_words)
        
        # 4. AUTHORITY
        authority_indicators = [
            'experte', 'professor', 'doktor', 'wissenschaft',
            'studie', 'forschung', 'beweis', 'erfahrung',
            'jahre', 'spezialist', 'profi'
        ]
        authority_score = sum(text_lower.count(ind) for ind in authority_indicators)
        
        # 5. LIKING
        liking_words = [
            'du', 'dein', 'dir', 'wie du', 'verstehe',
            'ähnlich', 'gleich', 'auch', 'genau wie',
            'gemeinsam', 'zusammen'
        ]
        liking_score = sum(text_lower.count(word) for word in liking_words)
        
        # 6. SCARCITY
        scarcity_words = [
            'limitiert', 'begrenzt', 'nur', 'wenige', 'knapp',
            'jetzt', 'sofort', 'schnell', 'bevor', 'letzte',
            'exklusiv', 'selten', 'einmalig'
        ]
        scarcity_score = sum(text_lower.count(word) for word in scarcity_words)
        
        # Normalize (0-1 scale)
        return {
            'reciprocity_trigger': min(1.0, reciprocity_score / 5),
            'commitment_trigger': min(1.0, commitment_score / 6),
            'social_proof_trigger': min(1.0, social_proof_score / 8),
            'authority_trigger': min(1.0, authority_score / 5),
            'liking_trigger': min(1.0, liking_score / 15),
            'scarcity_trigger': min(1.0, scarcity_score / 6)
        }
    
    # ========================================
    # ALGORITHM ALIGNMENT
    # ========================================
    
    def _extract_algorithm_features(self, y, sr, segments, duration):
        """
        Features die DIREKT Algorithm Metriken beeinflussen:
        
        1. Watch Time optimization
        2. Completion Rate indicators
        3. Engagement triggers
        4. Session Duration factors
        """
        
        # Optimal duration (algorithm sweet spot: 45-90s)
        duration_score = 1.0
        if duration < 30:
            duration_score = duration / 30  # Too short
        elif duration > 120:
            duration_score = 1.0 - ((duration - 120) / 180)  # Too long
        duration_score = max(0.0, min(1.0, duration_score))
        
        # Energy consistency (avoid drop-offs)
        rms = librosa.feature.rms(y=y)[0]
        
        # Check for energy dips (risk of scroll-past)
        energy_threshold = np.mean(rms) * 0.5
        energy_dips = np.sum(rms < energy_threshold)
        dip_risk = energy_dips / len(rms) if len(rms) > 0 else 0
        
        # Completion indicators
        # Strong ending (last 10%)
        last_10_percent = int(len(rms) * 0.1)
        ending_energy = np.mean(rms[-last_10_percent:]) if last_10_percent > 0 else 0
        avg_energy = np.mean(rms)
        strong_ending = 1 if ending_energy > avg_energy else 0
        
        # Call-to-action indicators (engagement)
        if segments:
            last_segments = segments[-3:]  # Last 3 segments
            ending_text = ' '.join(s['text'] for s in last_segments).lower()
            
            cta_words = [
                'like', 'subscribe', 'folge', 'teile', 'kommentar',
                'schreib', 'sag', 'erzähl', 'zeig', 'tag'
            ]
            cta_present = sum(ending_text.count(word) for word in cta_words)
        else:
            cta_present = 0
        
        # Pacing optimization (neither too fast nor too slow)
        if segments and len(segments) > 1:
            words_per_second = len(' '.join(s['text'] for s in segments).split()) / duration
            optimal_pace = 1.0
            if words_per_second < 1.5:  # Too slow
                optimal_pace = words_per_second / 1.5
            elif words_per_second > 3.5:  # Too fast
                optimal_pace = 1.0 - ((words_per_second - 3.5) / 3.5)
            optimal_pace = max(0.0, min(1.0, optimal_pace))
        else:
            optimal_pace = 0.5
        
        return {
            'duration_optimization': float(duration_score),
            'energy_dip_risk': float(dip_risk),
            'strong_ending': strong_ending,
            'cta_present': min(1, cta_present),
            'pacing_optimization': float(optimal_pace),
            'completion_likelihood': float((1 - dip_risk) * strong_ending * duration_score)
        }
    
    # ========================================
    # BASIC FEATURES
    # ========================================
    
    def _extract_basic_features(self, y, sr, text, duration):
        """Standard audio/text features"""
        
        # Audio
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        pitch_variance = float(np.std(pitch_values)) if pitch_values else 0
        
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_centroid_var = float(np.var(spectral_centroid))
        
        rms = librosa.feature.rms(y=y)[0]
        avg_energy = float(np.mean(rms))
        max_energy = float(np.max(rms))
        
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])
        
        # Text
        char_count = len(text)
        word_count = len(text.split())
        question_marks = text.count('?')
        exclamation_marks = text.count('!')
        
        return {
            'pitch_variance': pitch_variance,
            'spectral_centroid_var': spectral_centroid_var,
            'avg_energy': avg_energy,
            'max_energy': max_energy,
            'tempo': tempo,
            'duration': duration,
            'char_count': char_count,
            'word_count': word_count,
            'question_marks': question_marks,
            'exclamation_marks': exclamation_marks
        }


if __name__ == "__main__":
    print("="*70)
    print("🎯 ULTIMATE ALGORITHM-OPTIMIZED FEATURE EXTRACTOR")
    print("="*70)
    print("\nFeature Categories:")
    print("  1. Hook Features (0-3s) - CRITICAL")
    print("  2. Retention Mechanics - Pattern Interrupts, Loops")
    print("  3. 12 Viral Criteria - Mass Appeal → Trend")
    print("  4. Cialdini Triggers - 6 Persuasion Principles")
    print("  5. Algorithm Alignment - Watchtime Optimization")
    print("  6. Basic Features - Audio/Text fundamentals")
    print("\nTotal: ~70 features extracted per clip")
    print("="*70)

"""
Cognitive Analyzer
NLP-based cognitive health analysis with 5 key metrics:
1. Vocabulary Diversity (TTR)
2. Topic Coherence (sentence embeddings)
3. Repetition Detection
4. Word-Finding Pauses
5. Response Latency
"""

import logging
import re
from datetime import datetime, UTC
from typing import Optional
from collections import Counter

logger = logging.getLogger(__name__)

# Lazy-load heavy NLP models
_spacy_nlp = None
_sentence_model = None


def get_spacy_model():
    """Lazy load spaCy model"""
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model: en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            # Return a dummy that won't crash
            import spacy
            _spacy_nlp = spacy.blank("en")
    return _spacy_nlp


def get_sentence_transformer():
    """Lazy load sentence-transformer model"""
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"⚡ Loading SentenceTransformer on device: {device.upper()}")
            
            _sentence_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            logger.info(f"✓ SentenceTransformer loaded successfully on {device.upper()}")
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformer: {e}")
            _sentence_model = None
    return _sentence_model


class CognitiveAnalyzer:
    """
    Analyzes patient conversation transcripts for cognitive health indicators
    """
    
    def __init__(self):
        """Initialize analyzer (models loaded lazily on first use)"""
        pass
    
    async def analyze_conversation(
        self,
        transcript: str,
        patient_name: str,
        response_times: Optional[list[float]] = None,
        conversation_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        history_transcripts: Optional[list[str]] = None
    ) -> dict:
        """
        Main entry point: analyze a conversation transcript
        
        Args:
            transcript: Full conversation transcript with speaker labels
            patient_name: Name of the patient (to extract their turns)
            response_times: Optional list of response latencies in seconds
            conversation_id: Optional conversation ID for tracking
            patient_id: Optional patient ID for tracking
            history_transcripts: Optional list of recent conversation transcripts for cross-conversation repetition
            
        Returns:
            CognitiveMetrics as dict
        """
        logger.info(f"Analyzing conversation for patient: {patient_name}")
        
        # Extract patient's turns from transcript
        patient_turns = self._extract_patient_turns(transcript, patient_name)
        
        # Extract history turns for cross-conversation repetition detection
        history_turns = []
        if history_transcripts:
            for hist_transcript in history_transcripts:
                history_turns.extend(self._extract_patient_turns(hist_transcript, patient_name))
        
        # Guard: minimum conversation length
        if len(patient_turns) < 3:
            logger.warning(f"Insufficient patient turns ({len(patient_turns)}). Returning partial metrics.")
            return self._partial_metrics(conversation_id, patient_id)
        
        # Compute each metric
        vocabulary_diversity = self.compute_vocabulary_diversity(patient_turns)
        topic_coherence = self.compute_topic_coherence(patient_turns)
        repetition_count, repetition_rate = self.detect_repetitions(
            patient_turns,
            history_turns=history_turns if history_turns else None
        )
        word_finding_pauses = self.count_word_finding_pauses(patient_turns)
        response_latency = self.compute_response_latency(response_times)
        
        metrics = {
            "vocabulary_diversity": vocabulary_diversity,
            "topic_coherence": topic_coherence,
            "repetition_count": repetition_count,
            "repetition_rate": repetition_rate,
            "word_finding_pauses": word_finding_pauses,
            "response_latency": response_latency,
            "analyzed_at": datetime.now(UTC).isoformat(),
            "conversation_id": conversation_id,
            "patient_id": patient_id
        }
        
        logger.info(f"Analysis complete. TTR={vocabulary_diversity:.3f}, "
                   f"Coherence={topic_coherence:.3f}, Repetitions={repetition_count} "
                   f"(cross-convo: {len(history_turns)} history turns), "
                   f"Word-finding={word_finding_pauses}")
        
        return metrics
    
    def _partial_metrics(self, conversation_id: Optional[str], patient_id: Optional[str]) -> dict:
        """Return None metrics when conversation is too short to prevent baseline contamination"""
        return {
            "vocabulary_diversity": None,
            "topic_coherence": None,
            "repetition_count": 0,
            "repetition_rate": 0.0,
            "word_finding_pauses": 0,
            "response_latency": None,
            "analyzed_at": datetime.now(UTC).isoformat(),
            "conversation_id": conversation_id,
            "patient_id": patient_id,
            "_partial": True
        }
    
    def _extract_patient_turns(self, transcript: str, patient_name: str) -> list[str]:
        """
        Extract only the patient's utterances from transcript
        
        Matches multiple speaker label formats:
        - "Dorothy: ..." (patient name)
        - "Patient: ..." (V1 Deepgram label)
        - "Emily: ..." (preferred name)
        """
        turns = []
        lines = transcript.split('\n')
        
        # Build set of labels that identify the patient
        patient_labels = {"Patient"}
        if patient_name:
            patient_labels.add(patient_name)
            # Also match first name only (e.g. "Emily" from "Emily Chen")
            first_name = patient_name.split()[0] if ' ' in patient_name else patient_name
            patient_labels.add(first_name)
        
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            # Extract speaker label (everything before first colon)
            speaker = line.split(':', 1)[0].strip()
            
            # Check if this speaker is the patient (case-insensitive)
            if any(speaker.lower() == label.lower() for label in patient_labels):
                text = line.split(':', 1)[1].strip()
                if text:
                    turns.append(text)
        
        logger.debug(f"Extracted {len(turns)} patient turns from transcript (labels: {patient_labels})")
        return turns
    
    def compute_vocabulary_diversity(self, patient_turns: list[str]) -> float:
        """
        Compute Type-Token Ratio (TTR): unique lemmas / total lemmas
        Higher = better vocabulary diversity
        """
        nlp = get_spacy_model()
        
        all_lemmas = []
        for turn in patient_turns:
            doc = nlp(turn)
            # Extract lemmas, filter stopwords and punctuation
            lemmas = [
                token.lemma_.lower() 
                for token in doc 
                if not token.is_stop 
                and not token.is_punct 
                and token.is_alpha
            ]
            all_lemmas.extend(lemmas)
        
        if not all_lemmas:
            return 0.0
        
        unique_lemmas = len(set(all_lemmas))
        total_lemmas = len(all_lemmas)
        
        ttr = unique_lemmas / total_lemmas
        return round(ttr, 3)
    
    def compute_topic_coherence(self, patient_turns: list[str]) -> float:
        """
        Compute topic coherence via sentence embeddings
        Measure: average pairwise cosine similarity of consecutive turns
        Higher = more coherent conversation flow
        """
        if len(patient_turns) < 2:
            return 1.0  # Single turn is perfectly coherent with itself
        
        model = get_sentence_transformer()
        if model is None:
            logger.warning("Sentence transformer not available. Using fallback coherence.")
            return 0.75  # Reasonable default
        
        try:
            # Encode all turns
            embeddings = model.encode(patient_turns)
            
            # Compute cosine similarity between consecutive turns
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[i+1].reshape(1, -1)
                )[0][0]
                similarities.append(sim)
            
            avg_coherence = float(np.mean(similarities))
            return round(avg_coherence, 3)
            
        except Exception as e:
            logger.error(f"Error computing topic coherence: {e}")
            return 0.75
    
    def detect_repetitions(
        self,
        patient_turns: list[str],
        history_turns: Optional[list[str]] = None
    ) -> tuple[int, float]:
        """
        Detect repeated trigrams (3-word sequences)
        
        Args:
            patient_turns: Current conversation turns
            history_turns: Optional recent conversation history for cross-conversation detection
            
        Returns:
            (count of repetitions, repetition rate)
        """
        nlp = get_spacy_model()
        
        all_turns = patient_turns + (history_turns or [])
        all_trigrams = []
        
        for turn in all_turns:
            doc = nlp(turn)
            words = [token.text.lower() for token in doc if token.is_alpha]
            
            # Generate trigrams
            for i in range(len(words) - 2):
                trigram = tuple(words[i:i+3])
                all_trigrams.append(trigram)
        
        if not all_trigrams:
            return 0, 0.0
        
        # Count repetitions (trigrams appearing more than once)
        trigram_counts = Counter(all_trigrams)
        repeated = sum(1 for count in trigram_counts.values() if count > 1)
        
        repetition_rate = repeated / len(all_trigrams) if all_trigrams else 0.0
        
        return repeated, round(repetition_rate, 3)
    
    def count_word_finding_pauses(self, patient_turns: list[str]) -> int:
        """
        Count word-finding difficulty indicators
        
        Patterns:
        - Filler words: um, uh, uhh, hmm
        - Explicit word-finding: "what's the word", "you know", "the thing"
        - Memory gaps: "I can't remember the name", "what do you call it"
        - Ellipsis patterns: ". . .", "..."
        """
        patterns = [
            r'\bum+\b',
            r'\buh+\b',
            r'\bhm+\b',
            r'\bhmm+\b',
            r"what'?s the word",
            r'\byou know\b',
            r'\bthe thing\b',
            r"can'?t remember",
            r'what do (?:you|they) call',
            r'\.\s*\.\s*\.',  # Ellipsis with spaces
            r'\.{2,}',  # Multiple periods
        ]
        
        combined_pattern = '|'.join(patterns)
        total_count = 0
        
        for turn in patient_turns:
            matches = re.findall(combined_pattern, turn.lower())
            total_count += len(matches)
        
        return total_count
    
    def compute_response_latency(self, response_times: Optional[list[float]]) -> Optional[float]:
        """
        Compute average response latency
        
        Args:
            response_times: List of response latencies in seconds
            
        Returns:
            Average latency or None if unavailable
        """
        if not response_times:
            return None
        
        avg_latency = sum(response_times) / len(response_times)
        return round(avg_latency, 2)

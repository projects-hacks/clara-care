"""Tracks discussed topics during a call to prevent repetition."""

import logging

logger = logging.getLogger(__name__)


class TopicTracker:
    """Tracks topics discussed in the current call."""

    def __init__(self):
        self.topics_discussed: list[str] = []

    def detect_topics(self, text: str) -> list[str]:
        """Detect topics from patient speech and add to tracking list."""
        topic_keywords = {
            "health": ["doctor", "medication", "pain", "sleep", "tired"],
            "family": ["daughter", "son", "grandchild", "family", "wife", "husband"],
            "activities": ["walk", "garden", "cook", "read", "tv", "movie"],
            "emotions": ["happy", "sad", "lonely", "worried", "scared"],
            "food": ["eat", "breakfast", "lunch", "dinner", "cook"],
            "weather": ["weather", "rain", "sun", "cold", "warm"],
        }
        text_lower = text.lower()
        new_topics = []
        for topic, keywords in topic_keywords.items():
            if topic not in self.topics_discussed:
                if any(kw in text_lower for kw in keywords):
                    self.topics_discussed.append(topic)
                    new_topics.append(topic)
        return new_topics

    def get_state_summary(self) -> str:
        """Return a summary of discussed topics for LLM injection."""
        if not self.topics_discussed:
            return ""
        return (
            f"Topics already covered: {', '.join(self.topics_discussed)}. "
            "Steer toward something NEW and different."
        )

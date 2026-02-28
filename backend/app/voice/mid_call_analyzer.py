"""Mid-call sentiment analysis — runs as background task during calls."""

import asyncio
import logging
import os
from collections import deque
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class MidCallAnalyzer:
    """
    Analyzes accumulated transcript for sentiment during a call.
    Runs as fire-and-forget background task.
    """

    def __init__(self, max_history: int = 20):
        self.last_sentiment: str = "neutral"
        self.sentiment_history: deque[str] = deque(maxlen=max_history)
        self.check_interval: int = 5  # Check every N patient turns
        self._task: Optional[asyncio.Task] = None
        self._http_client: httpx.AsyncClient = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        """Close the HTTP client."""
        if self._task and not self._task.done():
            self._task.cancel()
        await self._http_client.aclose()

    def should_check(self, patient_turn_count: int) -> bool:
        """Whether it's time for a sentiment check."""
        return patient_turn_count > 0 and patient_turn_count % self.check_interval == 0

    async def analyze_sentiment(self, transcript_lines: list[dict], call_sid: str) -> tuple[str, str]:
        """
        Analyze accumulated transcript for sentiment via Deepgram.
        Returns the (previous_sentiment, new_sentiment) tuple.
        """
        text = "\n".join(f"{t['speaker']}: {t['text']}" for t in transcript_lines[-10:])
        prev = self.last_sentiment

        try:
            dg_key = os.getenv("DEEPGRAM_API_KEY", "")
            if not dg_key:
                return prev, self.last_sentiment

            resp = await self._http_client.post(
                "https://api.deepgram.com/v1/read?sentiment=true&language=en",
                headers={"Authorization": f"Token {dg_key}", "Content-Type": "application/json"},
                json={"text": text},
            )
            if resp.status_code == 200:
                data = resp.json()
                segments = (
                    data.get("results", {}).get("sentiments", {}).get("segments", [])
                )
                if segments:
                    sentiment = segments[-1].get("sentiment", "neutral")
                    self.sentiment_history.append(sentiment)
                    self.last_sentiment = sentiment
                    return prev, sentiment
        except Exception as e:
            logger.warning(f"[SENTIMENT] {call_sid} analysis failed: {e}")

        return prev, self.last_sentiment

    def get_emotional_guidance(self, prev_sentiment: str, new_sentiment: str) -> str:
        """Generate emotional guidance for Clara based on detected sentiment shift."""
        if prev_sentiment == new_sentiment:
            return ""
        shift = f"{prev_sentiment} → {new_sentiment}"

        # If previous was negative or positive, and new is opposite.
        guidance = ""
        if new_sentiment == "negative" and prev_sentiment != "negative":
            guidance = (
                "[EMOTIONAL CONTEXT] The patient's tone has shifted — they seem a bit down or upset now. "
                "Be warmer and more gentle. Ask how they're feeling. Don't try to fix anything — "
                "just listen and validate. Slow down your pace."
            )
        elif new_sentiment == "positive" and prev_sentiment == "negative":
            guidance = (
                "[EMOTIONAL CONTEXT] Good news — the patient's mood has lifted! "
                "Match their energy. This is a good moment to explore what made them happy."
            )
        elif new_sentiment == "negative" and len(self.sentiment_history) >= 3 and all(
            s == "negative" for s in list(self.sentiment_history)[-3:]
        ):
            guidance = (
                "[EMOTIONAL CONTEXT] The patient has been consistently low throughout this conversation. "
                "Consider gently asking if something is bothering them, or if they'd like to talk another time. "
                "Don't push — respect their space."
            )

        if guidance:
            logger.info(f"[SENTIMENT_SHIFT] {shift} — injecting guidance")
        return guidance

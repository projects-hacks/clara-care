"""
You.com API Client for ClaraCare Nostalgia Integration

Official Documentation: https://you.com/platform
Hackathon Track: Build AI Agents That Think, Reason & Search Live

This client powers:
- Nostalgia Mode: Era-specific content from patient's golden years (ages 15-25)
- Real-time Q&A: Live web search for answering patient questions

API Features:
- LLM-ready, citation-backed answers
- Structured JSON with URLs, snippets, and metadata
- Perfect for grounding models in real-time data
"""

import logging
import os
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)


class YouComClient:
    """
    You.com Search API Client
    
    Provides real-time web search with citations for:
    1. Nostalgia Mode - Era-specific content based on birth year
    2. Real-time Q&A - Live answers to patient questions
    
    Get your API key: https://you.com/platform (free $100 credits)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize You.com Search API client
        
        Args:
            api_key: You.com API key (or from YOUCOM_API_KEY env var)
                    Sign up at https://you.com/platform for $100 free credits
        """
        self.api_key = api_key or os.getenv("YOUCOM_API_KEY")
        self.base_url = "https://ydc-index.io"
        
        if self.api_key:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-API-Key": self.api_key},
                timeout=15.0
            )
            logger.info("✓ YouComClient initialized with API key")
        else:
            self._client = None
            logger.warning("⚠ YouComClient: No API key - using fallback responses (Get key: https://you.com/platform)")
    
    async def search_nostalgia(
        self,
        birth_year: Optional[int] = None,
        trigger_reason: str = "general"
    ) -> Dict[str, Any]:
        """
        Search for era-specific nostalgic content from patient's golden years
        
        Golden years = ages 15-25 (formative years with strongest memories)
        
        Args:
            birth_year: Patient's birth year (e.g., 1951)
            trigger_reason: Why nostalgia was triggered (e.g., "feeling lonely", "reminiscing")
        
        Returns:
            Dict with nostalgic content:
            {
                "music": ["Song 1", "Song 2", ...],
                "events": ["Historical event 1", ...],
                "culture": "Cultural summary",
                "era": "1966-1976"
            }
        """
        # Calculate golden years (ages 15-25)
        if birth_year:
            from app.nostalgia.era import calculate_golden_years
            year_start, year_end = calculate_golden_years(birth_year)
        else:
            # Default to 1960s if no birth year
            year_start, year_end = 1965, 1975
        
        if not self._client:
            return self._fallback_nostalgia_content(year_start, year_end)
        
        try:
            # Search for era-specific music
            music_results = await self._search_era_content(
                f"popular music hits {year_start}-{year_end}",
                count=5
            )
            
            # Search for era events
            events_results = await self._search_era_content(
                f"major events news {year_start}-{year_end}",
                count=5
            )
            
            # Combine results
            music = [r.get("title", "") for r in music_results[:3]]
            events = [r.get("snippet", "") for r in events_results[:3]]
            
            return {
                "music": music if music else ["Classic hits from the era"],
                "events": events if events else ["Historical events from the time"],
                "culture": f"Popular culture from {year_start}-{year_end}",
                "era": f"{year_start}-{year_end}"
            }
            
        except httpx.HTTPError as e:
            logger.warning(f"You.com API request failed: {e}")
            return self._fallback_nostalgia_content(year_start, year_end)
        except Exception as e:
            logger.error(f"Unexpected error in You.com search: {e}")
            return self._fallback_nostalgia_content(year_start, year_end)
    
    async def _search_era_content(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Internal helper for era-specific searches
        
        Uses You.com Search API v1: GET /v1/search
        """
        try:
            response = await self._client.get(
                "/v1/search",
                params={"query": query}
            )
            response.raise_for_status()
            data = response.json()

            # /v1/search returns {results: {web: [{url, title, description, snippets}]}}
            # Handle both the nested dict shape and any legacy flat-list shape.
            raw = data.get("results", {})
            web_list = raw.get("web", []) if isinstance(raw, dict) else raw

            results = []
            for result in web_list[:count]:
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("description", "") or (
                        result.get("snippets", [""])[0] if result.get("snippets") else ""
                    ),
                    "url": result.get("url", "")
                })

            return results
            
        except Exception as e:
            logger.warning(f"Era search failed: {e}")
            return []
    
    async def search_realtime(self, query: str) -> Dict[str, Any]:
        """
        Search for real-time information using You.com Search API
        
        Perfect for answering patient questions with up-to-date, citation-backed info.
        
        Examples:
            - "What's the weather today?"
            - "Latest news about gardening"
            - "How to make chocolate chip cookies"
        
        Args:
            query: Natural language search query
        
        Returns:
            Dict with:
            {
                "answer": "Primary answer text",
                "results": [{"title", "snippet", "url"}, ...],
                "citations": ["url1", "url2", ...]
            }
        """
        if not self._client:
            return self._fallback_realtime(query)
        
        try:
            # Official You.com Search API endpoint
            response = await self._client.get(
                "/v1/search",
                params={"query": query}
            )
            response.raise_for_status()
            data = response.json()

            # /v1/search returns {results: {web: [{url, title, description, snippets}]}}
            raw = data.get("results", {})
            web_list = raw.get("web", []) if isinstance(raw, dict) else raw

            answer = ""
            results = []
            citations = []

            if web_list:
                first = web_list[0]
                # Prefer snippets (richer context) over description for the answer
                snippets = first.get("snippets", [])
                answer = snippets[0] if snippets else first.get("description", "")

                for result in web_list[:3]:
                    snips = result.get("snippets", [])
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": snips[0] if snips else result.get("description", ""),
                        "url": result.get("url", "")
                    })
                    citations.append(result.get("url", ""))

            return {
                "answer": answer or "I found some information about that.",
                "results": results,
                "citations": citations
            }
            
        except httpx.HTTPError as e:
            logger.warning(f"You.com API request failed: {e}")
            return self._fallback_realtime(query)
        except Exception as e:
            logger.error(f"Unexpected error in You.com search: {e}")
            return self._fallback_realtime(query)
    
    def _fallback_nostalgia_content(self, year_start: int, year_end: int) -> Dict[str, Any]:
        """
        Graceful fallback when You.com API is unavailable
        Returns era-appropriate generic nostalgic content
        """
        era = f"{year_start}-{year_end}"
        decade = (year_start // 10) * 10
        
        # Generic nostalgic content by decade
        content_map = {
            1950: {
                "music": ["Elvis Presley - Hound Dog", "Chuck Berry - Johnny B. Goode", "Buddy Holly - That'll Be the Day"],
                "events": ["Korean War ends (1953)", "Rosa Parks and Montgomery Bus Boycott (1955)", "Sputnik launched (1957)"],
                "culture": "Rock and roll was born, drive-in movies were popular, and TV became mainstream"
            },
            1960: {
                "music": ["The Beatles - I Want to Hold Your Hand", "The Rolling Stones - Satisfaction", "Bob Dylan - Blowin' in the Wind"],
                "events": ["Moon landing (1969)", "Woodstock Festival (1969)", "Civil Rights Act (1964)"],
                "culture": "The British Invasion, hippie movement, and counterculture defined the era"
            },
            1970: {
                "music": ["Led Zeppelin - Stairway to Heaven", "Fleetwood Mac - Dreams", "Queen - Bohemian Rhapsody"],
                "events": ["Watergate scandal (1974)", "Vietnam War ends (1975)", "Disco era"],
                "culture": "Disco, punk rock, and progressive rock shaped the music scene"
            },
            1980: {
                "music": ["Michael Jackson - Thriller", "Madonna - Like a Virgin", "Prince - Purple Rain"],
                "events": ["Fall of Berlin Wall (1989)", "MTV launches (1981)", "Live Aid concert (1985)"],
                "culture": "MTV, arcade games, and new wave music dominated youth culture"
            },
            1990: {
                "music": ["Nirvana - Smells Like Teen Spirit", "Whitney Houston - I Will Always Love You", "TLC - Waterfalls"],
                "events": ["Fall of Soviet Union (1991)", "World Wide Web goes public (1991)", "Nelson Mandela released (1990)"],
                "culture": "Grunge, hip-hop, and boy bands were everywhere"
            }
        }
        
        content = content_map.get(decade, content_map[1960])  # Default to 1960s
        
        return {
            "music": content["music"],
            "events": content["events"],
            "culture": content["culture"],
            "era": era,
            "_note": "Fallback content - Get You.com API key at https://you.com/platform"
        }
    
    def _fallback_realtime(self, query: str) -> Dict[str, Any]:
        """Fallback for real-time queries when API unavailable"""
        return {
            "answer": f"I'd love to help answer that, but I need an internet connection. Let's talk about something else!",
            "results": [],
            "citations": [],
            "_note": "Fallback - Get You.com API key at https://you.com/platform ($100 free credits)"
        }
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            logger.info("Closed YouComClient HTTP client")

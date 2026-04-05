"""Indian Kanoon API Service — Fetch legal judgments and case law.

Uses api.indiankanoon.org to search for relevant legal precedents and case law
that matches user queries. Provides real-time judicial decisions and commentary.

API: https://indiankanoon.org/api/
Documentation: https://indiankanoon.org/doc/api/
Rate limit: No strict limit, but be respectful with requests
"""

import logging
import httpx
import json
from typing import Optional, List
from urllib.parse import quote

logger = logging.getLogger("lexindia.services.indiakanoon")

# Indian Kanoon API base URL
INDIANKANOON_API_BASE = "https://indiankanoon.org/api"
INDIANKANOON_SEARCH_URL = f"{INDIANKANOON_API_BASE}/search"
INDIANKANOON_DOCS_URL = f"{INDIANKANOON_API_BASE}/doc"

# HTTP client with timeouts
TIMEOUT = httpx.Timeout(10.0, connect=5.0)


async def search_indiakanoon(query: str, limit: int = 5) -> List[dict]:
    """Search Indian Kanoon for relevant legal cases and judgments.
    
    Args:
        query: Search query (law section, case name, or legal concept)
        limit: Maximum number of results to return
        
    Returns:
        List of legal documents with title, summary, and link
        
    Example response:
        {
            "title": "Case Name vs Case Name",
            "summary": "Summary of judgment...",
            "url": "https://indiankanoon.org/doc/...",
            "year": 2023,
            "court": "Supreme Court of India"
        }
    """
    try:
        logger.info(f"Searching Indian Kanoon for: {query}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Query Indian Kanoon API
            params = {
                "q": query,
                "pagenum": 0,
                "sortby": "asc"
            }
            
            response = await client.get(INDIANKANOON_SEARCH_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Parse search results
            if "docs" in data:
                for doc in data["docs"][:limit]:
                    try:
                        result = {
                            "title": doc.get("title", "Untitled"),
                            "summary": doc.get("short", "No summary available"),
                            "url": f"https://indiankanoon.org/doc/{doc.get('id', '')}",
                            "year": doc.get("year"),
                            "court": doc.get("court", "Unknown Court"),
                            "relevance": doc.get("score", 0)
                        }
                        results.append(result)
                        logger.info(f"  Found: {result['title'][:50]}...")
                    except Exception as e:
                        logger.warning(f"Error parsing document: {e}")
                        continue
            
            logger.info(f"Indian Kanoon search returned {len(results)} results")
            return results
            
    except httpx.RequestError as e:
        logger.error(f"Indian Kanoon API request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Indian Kanoon response: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in Indian Kanoon search: {e}")
        return []


async def get_document_details(doc_id: str) -> Optional[dict]:
    """Fetch detailed information about a specific Indian Kanoon document.
    
    Args:
        doc_id: The document ID from Indian Kanoon
        
    Returns:
        Dictionary with full document details or None if error
    """
    try:
        logger.info(f"Fetching Indian Kanoon document: {doc_id}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{INDIANKANOON_DOCS_URL}/{doc_id}")
            response.raise_for_status()
            
            doc = response.json()
            logger.info(f"Retrieved document: {doc.get('title', 'Unknown')}")
            return doc
            
    except Exception as e:
        logger.error(f"Error fetching document details: {e}")
        return None


async def search_by_law_section(section: str) -> List[dict]:
    """Search for cases related to a specific Indian law section.
    
    Args:
        section: Law section (e.g., "IPC 498A", "PWDVA 3", "CPA 35")
        
    Returns:
        List of relevant case judgments
    """
    try:
        # Format: "Section XYZ of [Act Name]"
        query = f"Section {section.split()[-1]} of {' '.join(section.split()[:-1])}"
        logger.info(f"Searching Indian Kanoon for section: {query}")
        
        return await search_indiakanoon(query)
        
    except Exception as e:
        logger.error(f"Error searching by section: {e}")
        return []

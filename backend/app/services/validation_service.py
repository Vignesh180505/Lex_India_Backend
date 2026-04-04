"""Data validation service for LLM outputs and database integrity.

Validates simplification quality, severity classifications, and data completeness.
Prevents storing incomplete or hallucinated data.
"""

import logging
import json
from typing import Optional, Dict, Any

from app.config import settings

logger = logging.getLogger("lexindia.services.validation")


def validate_simplified_text(
    original: str,
    simplified: str,
    section_id: str,
) -> tuple[bool, Optional[str]]:
    """Validate that simplified text is actually simpler and doesn't hallucinate.
    
    Args:
        original: Original section text
        simplified: Simplified/translated text from LLM
        section_id: Section identifier for logging
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check minimum length
    if not simplified or len(simplified.strip()) < settings.MIN_SIMPLIFIED_TEXT_LENGTH:
        return False, f"Simplified text too short ({len(simplified)} chars)"
    
    # Check maximum length (should be at most 80 words per spec)
    word_count = len(simplified.split())
    if word_count > 120:  # Allow some margin
        logger.warning(f"[{section_id}] Simplified text exceeds 120 words ({word_count} words)")
    
    # Check that simplified text is actually different from original
    if simplified.lower() == original.lower():
        return False, "Simplified text is identical to original"
    
    # Check that it's not empty or just whitespace
    if not simplified.strip():
        return False, "Simplified text is empty or whitespace-only"
    
    # Check for common hallucination markers
    hallucination_markers = [
        "[citation needed]",
        "TODO",
        "FILL_IN",
        "null",
        "undefined",
        "???",
        "...",  # Excessive ellipsis
    ]
    
    for marker in hallucination_markers:
        if marker in simplified:
            return False, f"Potential hallucination: contains '{marker}'"
    
    return True, None


def validate_severity_classification(severity: str, section_id: str) -> tuple[bool, Optional[str]]:
    """Validate severity is one of the allowed values.
    
    Args:
        severity: Severity value from LLM
        section_id: Section identifier for logging
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_severities = {"low", "medium", "high"}
    
    if not severity or severity.lower() not in valid_severities:
        logger.warning(f"[{section_id}] Invalid severity: {severity}")
        return False, f"Invalid severity value: {severity}"
    
    return True, None


def validate_llm_json_response(
    response_text: str,
    expected_keys: list[str],
    task_name: str,
) -> tuple[bool, Optional[Dict[str, Any]]]:
    """Validate and parse LLM JSON responses.
    
    Args:
        response_text: Raw response text from LLM
        expected_keys: List of required keys in JSON
        task_name: Name of task for logging
        
    Returns:
        Tuple of (is_valid, parsed_dict)
    """
    try:
        # Try to extract JSON from response (in case it has extra text)
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            logger.error(f"[{task_name}] No JSON found in response: {response_text[:100]}")
            return False, None
        
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            logger.error(f"[{task_name}] Failed to parse JSON: {e}")
            return False, None
    
    # Check for required keys
    missing_keys = [key for key in expected_keys if key not in data]
    if missing_keys:
        logger.error(f"[{task_name}] Missing keys: {missing_keys}")
        return False, None
    
    # Check for null/empty values in critical fields
    for key in expected_keys:
        if not data[key]:
            logger.warning(f"[{task_name}] Empty value for key: {key}")
    
    return True, data


def validate_section_for_storage(
    section_id: str,
    section_text: str,
    simplified_en: Optional[str],
    severity: Optional[str],
    punishment: Optional[str],
) -> tuple[bool, Optional[str]]:
    """Comprehensive validation before storing to database.
    
    Args:
        section_id: Section identifier
        section_text: Original legal text
        simplified_en: Simplified English text
        severity: Severity classification
        punishment: Punishment description
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate section text
    if not section_text or len(section_text) < settings.MIN_SECTION_TEXT_LENGTH:
        return False, f"Section text too short ({len(section_text)} chars, min {settings.MIN_SECTION_TEXT_LENGTH})"
    
    # Validate simplified text if present
    if simplified_en:
        is_valid, error = validate_simplified_text(section_text, simplified_en, section_id)
        if not is_valid:
            return False, f"Simplified text validation failed: {error}"
    
    # Validate severity if present
    if severity:
        is_valid, error = validate_severity_classification(severity, section_id)
        if not is_valid:
            return False, f"Severity validation failed: {error}"
    
    return True, None


def check_confidence_level(similarity_score: float, section_id: str) -> Optional[str]:
    """Check if similarity score is below confidence threshold and warn.
    
    Args:
        similarity_score: Cosine similarity score (0-1)
        section_id: Section identifier for logging
        
    Returns:
        Warning message if confidence is low, None otherwise
    """
    if similarity_score < settings.MIN_RESULT_CONFIDENCE:
        return (
            f"⚠️ LOW CONFIDENCE: Section {section_id} matched with only "
            f"{similarity_score:.0%} confidence. May not be relevant to your query."
        )
    return None

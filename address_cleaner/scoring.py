"""
Confidence scoring logic for address cleaning.

This module calculates confidence scores for parsed addresses based on
various factors like parsing quality, G-NAF matches, and corrections applied.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for parsed addresses."""

    def __init__(self, config: Dict):
        """
        Initialize confidence scorer.

        Args:
            config: Configuration dictionary containing scoring rules
        """
        self.config = config
        self.scoring_config = config.get('scoring', {})
        self.base_score = self.scoring_config.get('base_score', 100)
        self.penalties = self.scoring_config.get('penalties', {})

    def calculate_score(self, components: Dict, parsing_notes: List[str],
                       inconsistency_flags: List[str], gnaf_flags: List[str] = None,
                       gnaf_match_score: float = 0.0, corrections_applied: List[str] = None,
                       ml_confidence: float = None) -> int:
        """
        Calculate overall confidence score for an address.

        Args:
            components: Parsed address components
            parsing_notes: List of notes from parsing
            inconsistency_flags: List of inconsistency flags
            gnaf_flags: List of G-NAF matching flags
            gnaf_match_score: G-NAF match score (0.0-1.0)
            corrections_applied: List of corrections made
            ml_confidence: ML model confidence (0.0-1.0)

        Returns:
            Integer confidence score (0-100)
        """
        score = self.base_score

        gnaf_flags = gnaf_flags or []
        corrections_applied = corrections_applied or []

        # Apply penalties based on parsing notes
        score -= self._penalty_for_parsing_notes(parsing_notes)

        # Apply penalties for inconsistencies
        score -= self._penalty_for_inconsistencies(inconsistency_flags)

        # Apply penalties for G-NAF matching
        score -= self._penalty_for_gnaf(gnaf_flags, gnaf_match_score)

        # Apply penalties for corrections
        score -= self._penalty_for_corrections(corrections_applied)

        # Apply penalties for unparsed components
        if components.get('unparsed_components'):
            score -= self.penalties.get('unparsed_components_present', 12)

        # Apply penalties for missing components
        score -= self._penalty_for_missing_components(components)

        # Adjust based on ML confidence if available
        if ml_confidence is not None:
            score = self._adjust_for_ml_confidence(score, ml_confidence)

        # Ensure score is in valid range
        score = max(0, min(100, score))

        return int(score)

    def _penalty_for_parsing_notes(self, parsing_notes: List[str]) -> int:
        """Calculate penalty based on parsing notes."""
        penalty = 0

        note_penalties = {
            'INTERNATIONAL_ADDRESS': self.penalties.get('international_address', 80),
            'PO_BOX': 0,  # No penalty for PO Box
            'RMB': 0,  # No penalty for RMB
            'UNABLE_TO_PARSE': self.penalties.get('invalid_address', 90),
            'AMBIGUOUS_STREET_NUMBER': self.penalties.get('ambiguous_street_number', 7),
            'AMBIGUOUS_UNIT_NUMBER': self.penalties.get('ambiguous_unit_number', 5),
            'CONFLICTING_INDICATORS': self.penalties.get('conflicting_indicators', 10),
        }

        for note in parsing_notes:
            penalty += note_penalties.get(note, 0)

        return penalty

    def _penalty_for_inconsistencies(self, inconsistency_flags: List[str]) -> int:
        """Calculate penalty based on inconsistency flags."""
        penalty = 0

        flag_penalties = {
            'INVALID_POSTCODE_FORMAT': 15,
            'POSTCODE_STATE_MISMATCH': 12,
            'INVALID_STREET_NUMBER': 10,
            'SUBURB_POSTCODE_MISMATCH': 12,
        }

        for flag in inconsistency_flags:
            penalty += flag_penalties.get(flag, 5)

        return penalty

    def _penalty_for_gnaf(self, gnaf_flags: List[str], gnaf_match_score: float) -> int:
        """Calculate penalty based on G-NAF matching results."""
        penalty = 0

        if 'NO_GNAF_MATCH' in gnaf_flags:
            penalty += self.penalties.get('no_gnaf_match', 15)
        elif 'GNAF_APPROXIMATE_MATCH' in gnaf_flags:
            penalty += self.penalties.get('approximate_gnaf_match', 8)

            # Additional penalty based on match quality
            if gnaf_match_score < 0.8:
                penalty += 5
            elif gnaf_match_score < 0.9:
                penalty += 3

        if 'GNAF_DISABLED' in gnaf_flags:
            penalty += 5  # Small penalty for not using G-NAF

        if 'GNAF_CONNECTION_ERROR' in gnaf_flags or 'GNAF_QUERY_ERROR' in gnaf_flags:
            penalty += 5

        return penalty

    def _penalty_for_corrections(self, corrections_applied: List[str]) -> int:
        """Calculate penalty based on corrections applied."""
        penalty = 0

        correction_penalties = {
            'SUBURB_CORRECTED': self.penalties.get('suburb_corrected', 10),
            'STATE_CORRECTED': self.penalties.get('state_corrected', 10),
            'POSTCODE_CORRECTED': self.penalties.get('postcode_corrected', 10),
            'STREET_TYPE_FUZZY_MATCH': self.penalties.get('fuzzy_street_type', 5),
            'SUBURB_FUZZY_MATCH': self.penalties.get('fuzzy_suburb', 8),
        }

        for correction in corrections_applied:
            penalty += correction_penalties.get(correction, 3)

        return penalty

    def _penalty_for_missing_components(self, components: Dict) -> int:
        """Calculate penalty for missing essential components."""
        penalty = 0

        # Critical components
        if not components.get('street_name'):
            penalty += 30

        if not components.get('suburb'):
            penalty += 20

        if not components.get('state'):
            penalty += 20

        if not components.get('postcode'):
            penalty += 15

        # Important but not critical
        if not components.get('street_number'):
            penalty += 10

        return penalty

    def _adjust_for_ml_confidence(self, score: int, ml_confidence: float) -> int:
        """
        Adjust score based on ML model confidence.

        Args:
            score: Current score
            ml_confidence: ML confidence (0.0-1.0)

        Returns:
            Adjusted score
        """
        # If ML confidence is very high, give a small boost
        if ml_confidence >= 0.95:
            score += 2
        elif ml_confidence >= 0.90:
            score += 1

        # If ML confidence is low, apply penalty
        elif ml_confidence < 0.7:
            score -= 5
        elif ml_confidence < 0.8:
            score -= 3

        return score

    def classify_confidence(self, score: int) -> str:
        """
        Classify confidence score into categories.

        Args:
            score: Confidence score (0-100)

        Returns:
            Confidence category string
        """
        if score >= 95:
            return "EXCELLENT"
        elif score >= 85:
            return "VERY_HIGH"
        elif score >= 75:
            return "HIGH"
        elif score >= 60:
            return "MODERATE"
        elif score >= 40:
            return "LOW"
        else:
            return "VERY_LOW"

    def is_valid_address(self, components: Dict, score: int) -> bool:
        """
        Determine if address should be considered valid.

        Args:
            components: Parsed address components
            score: Confidence score

        Returns:
            True if address is valid, False otherwise
        """
        # Minimum score threshold
        if score < 30:
            return False

        # Must have essential components
        if not components.get('suburb') or not components.get('state'):
            return False

        # Special cases that are valid
        if components.get('street_type') in ['PO Box', 'RMB']:
            return True

        # Regular addresses must have street name
        if not components.get('street_name'):
            return False

        return True

    def get_score_breakdown(self, components: Dict, parsing_notes: List[str],
                           inconsistency_flags: List[str], gnaf_flags: List[str] = None,
                           gnaf_match_score: float = 0.0,
                           corrections_applied: List[str] = None,
                           ml_confidence: float = None) -> Dict:
        """
        Get detailed breakdown of confidence score calculation.

        Args:
            Same as calculate_score()

        Returns:
            Dictionary with score breakdown
        """
        gnaf_flags = gnaf_flags or []
        corrections_applied = corrections_applied or []

        breakdown = {
            'base_score': self.base_score,
            'penalties': {},
            'adjustments': {},
            'final_score': 0
        }

        # Calculate individual penalties
        breakdown['penalties']['parsing_notes'] = self._penalty_for_parsing_notes(parsing_notes)
        breakdown['penalties']['inconsistencies'] = self._penalty_for_inconsistencies(
            inconsistency_flags
        )
        breakdown['penalties']['gnaf'] = self._penalty_for_gnaf(gnaf_flags, gnaf_match_score)
        breakdown['penalties']['corrections'] = self._penalty_for_corrections(corrections_applied)

        if components.get('unparsed_components'):
            breakdown['penalties']['unparsed_components'] = self.penalties.get(
                'unparsed_components_present', 12
            )

        breakdown['penalties']['missing_components'] = self._penalty_for_missing_components(
            components
        )

        # Calculate total
        total_penalty = sum(breakdown['penalties'].values())
        score = self.base_score - total_penalty

        # ML adjustment
        if ml_confidence is not None:
            adjusted_score = self._adjust_for_ml_confidence(score, ml_confidence)
            breakdown['adjustments']['ml_confidence'] = adjusted_score - score
            score = adjusted_score

        breakdown['final_score'] = max(0, min(100, int(score)))

        return breakdown

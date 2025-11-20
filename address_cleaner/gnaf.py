"""
G-NAF (Geocoded National Address File) database integration.

This module handles connections to the G-NAF PostgreSQL database for
address validation, correction, and confidence boosting.
"""

import logging
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz
import pandas as pd

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Engine = None

logger = logging.getLogger(__name__)


class GNAFMatcher:
    """Matches and validates addresses against the G-NAF database."""

    def __init__(self, config: Dict, connection_url: Optional[str] = None):
        """
        Initialize G-NAF matcher.

        Args:
            config: Configuration dictionary
            connection_url: Optional database connection URL (overrides config)

        Raises:
            ImportError: If SQLAlchemy is not installed
            ValueError: If G-NAF is enabled but no connection URL provided
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "SQLAlchemy is required for G-NAF integration. "
                "Install it with: pip install sqlalchemy psycopg2-binary"
            )

        self.config = config
        self.gnaf_config = config.get('gnaf', {})

        # Determine connection URL
        self.connection_url = connection_url or self.gnaf_config.get('connection_url', '')

        if self.gnaf_config.get('enabled', True) and not self.connection_url:
            logger.warning(
                "G-NAF is enabled but no connection URL provided. "
                "G-NAF matching will be disabled."
            )
            self.enabled = False
            self.engine = None
        else:
            self.enabled = self.gnaf_config.get('enabled', True) and bool(self.connection_url)
            self.engine = self._create_engine() if self.enabled else None

    def _create_engine(self) -> Optional[Engine]:
        """Create SQLAlchemy engine for G-NAF database."""
        try:
            engine = create_engine(self.connection_url, pool_pre_ping=True)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to G-NAF database")
            return engine
        except Exception as e:
            logger.error(f"Failed to connect to G-NAF database: {e}")
            self.enabled = False
            return None

    def match_address(self, components: Dict) -> Tuple[Optional[Dict], float, List[str]]:
        """
        Match address components against G-NAF.

        Args:
            components: Dictionary of address components

        Returns:
            Tuple of (matched_components, match_score, flags)
            - matched_components: Dict with corrected components, or None if no match
            - match_score: Float 0.0-1.0 indicating match quality
            - flags: List of flags like 'GNAF_EXACT_MATCH', 'GNAF_APPROXIMATE_MATCH'
        """
        if not self.enabled:
            return None, 0.0, ['GNAF_DISABLED']

        if not self.engine:
            return None, 0.0, ['GNAF_CONNECTION_ERROR']

        street_number = components.get('street_number', '')
        street_name = components.get('street_name', '')
        street_type = components.get('street_type', '')
        suburb = components.get('suburb', '')
        state = components.get('state', '')
        postcode = components.get('postcode', '')

        # Skip if insufficient data
        if not street_name or not suburb:
            return None, 0.0, ['INSUFFICIENT_DATA_FOR_GNAF']

        try:
            # Try exact match first
            exact_match = self._exact_match(
                street_number, street_name, street_type, suburb, state, postcode
            )

            if exact_match:
                return exact_match, 1.0, ['GNAF_EXACT_MATCH']

            # Try approximate match if enabled
            if self.gnaf_config.get('allow_approximate_match', True):
                approx_match, score = self._approximate_match(
                    street_number, street_name, street_type, suburb, state, postcode
                )

                if approx_match and score >= self.gnaf_config.get(
                    'matching_thresholds', {}
                ).get('min_acceptable_score', 0.75):
                    return approx_match, score, ['GNAF_APPROXIMATE_MATCH']

            # No match found
            return None, 0.0, ['NO_GNAF_MATCH']

        except Exception as e:
            logger.error(f"Error during G-NAF matching: {e}")
            return None, 0.0, ['GNAF_QUERY_ERROR']

    def _exact_match(self, street_number: str, street_name: str, street_type: str,
                    suburb: str, state: str, postcode: str) -> Optional[Dict]:
        """
        Attempt exact match against G-NAF.

        Returns:
            Dictionary of matched components, or None
        """
        # Build query - this is a simplified version
        # In production, you'd query actual G-NAF tables
        query = text("""
            SELECT
                street_number,
                street_name,
                street_type,
                locality_name as suburb,
                state_abbreviation as state,
                postcode
            FROM gnaf.address_view
            WHERE UPPER(street_name) = UPPER(:street_name)
            AND UPPER(locality_name) = UPPER(:suburb)
            AND state_abbreviation = :state
            AND (:postcode = '' OR postcode = :postcode)
            AND (:street_number = '' OR street_number = :street_number)
            AND (:street_type = '' OR UPPER(street_type) = UPPER(:street_type))
            LIMIT 1
        """)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    'street_number': street_number,
                    'street_name': street_name,
                    'street_type': street_type,
                    'suburb': suburb,
                    'state': state,
                    'postcode': postcode
                })

                row = result.fetchone()

                if row:
                    return {
                        'street_number': str(row[0]) if row[0] else '',
                        'street_name': str(row[1]) if row[1] else '',
                        'street_type': str(row[2]) if row[2] else '',
                        'suburb': str(row[3]) if row[3] else '',
                        'state': str(row[4]) if row[4] else '',
                        'postcode': str(row[5]) if row[5] else '',
                    }

        except Exception as e:
            logger.debug(f"Exact match query failed: {e}")

        return None

    def _approximate_match(self, street_number: str, street_name: str, street_type: str,
                          suburb: str, state: str, postcode: str) -> Tuple[Optional[Dict], float]:
        """
        Attempt approximate/fuzzy match against G-NAF.

        Returns:
            Tuple of (matched_components, score)
        """
        # Simplified fuzzy matching
        # In production, this would use more sophisticated matching
        query = text("""
            SELECT
                street_number,
                street_name,
                street_type,
                locality_name as suburb,
                state_abbreviation as state,
                postcode
            FROM gnaf.address_view
            WHERE state_abbreviation = :state
            AND (:postcode = '' OR postcode = :postcode)
            AND UPPER(locality_name) LIKE UPPER(:suburb_pattern)
            LIMIT 10
        """)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    'state': state,
                    'postcode': postcode,
                    'suburb_pattern': f"%{suburb}%"
                })

                rows = result.fetchall()

                if not rows:
                    return None, 0.0

                # Calculate similarity scores
                best_match = None
                best_score = 0.0

                for row in rows:
                    # Calculate composite similarity score
                    street_name_sim = fuzz.ratio(
                        street_name.upper(),
                        str(row[1]).upper() if row[1] else ''
                    ) / 100.0

                    suburb_sim = fuzz.ratio(
                        suburb.upper(),
                        str(row[3]).upper() if row[3] else ''
                    ) / 100.0

                    # Weighted average
                    score = (street_name_sim * 0.6 + suburb_sim * 0.4)

                    if score > best_score:
                        best_score = score
                        best_match = {
                            'street_number': str(row[0]) if row[0] else '',
                            'street_name': str(row[1]) if row[1] else '',
                            'street_type': str(row[2]) if row[2] else '',
                            'suburb': str(row[3]) if row[3] else '',
                            'state': str(row[4]) if row[4] else '',
                            'postcode': str(row[5]) if row[5] else '',
                        }

                return best_match, best_score

        except Exception as e:
            logger.debug(f"Approximate match query failed: {e}")

        return None, 0.0

    def apply_corrections(self, original: Dict, matched: Dict, match_score: float) -> Dict:
        """
        Apply corrections from G-NAF match to original components.

        Args:
            original: Original parsed components
            matched: Matched components from G-NAF
            match_score: Quality of the match (0.0-1.0)

        Returns:
            Corrected components dictionary
        """
        corrected = original.copy()

        if not matched:
            return corrected

        corrections_config = self.gnaf_config.get('corrections', {})
        min_score = corrections_config.get('min_score_for_correction', 0.9)

        # Only apply corrections if match score is high enough
        if match_score < min_score:
            return corrected

        correctable_fields = corrections_config.get('correctable_fields', [])

        for field in correctable_fields:
            if field in matched and matched[field]:
                if corrected.get(field) != matched[field]:
                    # Record that we made a correction
                    if 'corrections_applied' not in corrected:
                        corrected['corrections_applied'] = []
                    corrected['corrections_applied'].append(f"{field.upper()}_CORRECTED")

                corrected[field] = matched[field]

        return corrected

    def batch_match(self, addresses_df: pd.DataFrame) -> pd.DataFrame:
        """
        Match a batch of addresses against G-NAF.

        Args:
            addresses_df: DataFrame with address components

        Returns:
            DataFrame with match results and scores
        """
        if not self.enabled:
            logger.warning("G-NAF matching is disabled")
            addresses_df['gnaf_match_score'] = 0.0
            addresses_df['gnaf_flags'] = 'GNAF_DISABLED'
            return addresses_df

        results = []

        for idx, row in addresses_df.iterrows():
            components = {
                'street_number': row.get('street_number', ''),
                'street_name': row.get('street_name', ''),
                'street_type': row.get('street_type', ''),
                'suburb': row.get('suburb', ''),
                'state': row.get('state', ''),
                'postcode': row.get('postcode', ''),
            }

            matched, score, flags = self.match_address(components)

            results.append({
                'gnaf_matched': matched,
                'gnaf_match_score': score,
                'gnaf_flags': ','.join(flags)
            })

        results_df = pd.DataFrame(results)

        # Merge results back
        for col in results_df.columns:
            addresses_df[col] = results_df[col]

        return addresses_df

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Closed G-NAF database connection")

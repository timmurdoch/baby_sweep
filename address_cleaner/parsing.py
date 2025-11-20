"""
Rule-based address parsing utilities.

This module contains functions for parsing and normalizing Australian address components
including street numbers, unit numbers, street names, street types, suburbs, states, and postcodes.
"""

import re
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process
import logging

logger = logging.getLogger(__name__)


class AddressParser:
    """Parser for Australian addresses using rule-based logic."""

    def __init__(self, config: Dict):
        """
        Initialize address parser with configuration.

        Args:
            config: Configuration dictionary containing parsing rules
        """
        self.config = config
        self.parsing_config = config.get('parsing', {})
        self.street_types_config = config.get('street_types', {})
        self.localities_config = config.get('localities', {})
        self.validation_config = config.get('validation', {})
        self.international_config = config.get('international_detection', {})

        # Build street type lookups
        self._build_street_type_mappings()

        # Build state lookups
        self._build_state_mappings()

    def _build_street_type_mappings(self):
        """Build lookup dictionaries for street type normalization."""
        self.street_type_map = {}
        self.canonical_street_types = []

        canonical = self.street_types_config.get('canonical', {})

        for key, data in canonical.items():
            label = data.get('label', key)
            aliases = data.get('aliases', [])

            self.canonical_street_types.append(label.upper())

            # Map canonical name to label
            self.street_type_map[label.upper()] = label
            self.street_type_map[key.upper()] = label

            # Map aliases to label
            for alias in aliases:
                self.street_type_map[alias.upper()] = label

        # Add misspellings
        misspellings = self.street_types_config.get('misspellings', {})
        for misspelling, correct_key in misspellings.items():
            # Find the label for the correct key
            for key, data in canonical.items():
                if key == correct_key:
                    self.street_type_map[misspelling.upper()] = data.get('label', key)
                    break

    def _build_state_mappings(self):
        """Build lookup dictionaries for state normalization."""
        self.state_map = {}
        self.valid_states = self.localities_config.get('states', {}).get('valid', [])

        # Map canonical states
        for state in self.valid_states:
            self.state_map[state.upper()] = state

        # Map aliases
        aliases = self.localities_config.get('states', {}).get('aliases', {})
        for alias, canonical in aliases.items():
            self.state_map[alias.upper()] = canonical

    def parse_address(self, street_address: str, suburb: str = "", state: str = "",
                     postcode: str = "") -> Dict:
        """
        Parse a complete address into components.

        Args:
            street_address: Street address string
            suburb: Suburb name
            state: State abbreviation
            postcode: Postcode

        Returns:
            Dictionary containing parsed address components and metadata
        """
        result = {
            'unit_number': '',
            'street_number': '',
            'street_name': '',
            'street_type': '',
            'suburb': '',
            'state': '',
            'postcode': '',
            'unparsed_components': '',
            'inconsistency_flags': [],
            'parsing_notes': []
        }

        # Clean inputs
        street_address = self._clean_text(street_address)
        suburb = self._clean_text(suburb)
        state = self._clean_text(state)
        postcode = self._clean_text(postcode)

        # Check for international address
        if self._is_international(street_address, suburb, state, postcode):
            result['parsing_notes'].append('INTERNATIONAL_ADDRESS')
            return result

        # Check for special cases
        if self._is_po_box(street_address):
            return self._parse_po_box(street_address, suburb, state, postcode)

        if self._is_rmb(street_address):
            return self._parse_rmb(street_address, suburb, state, postcode)

        # Parse street address components
        street_components = self._parse_street_address(street_address)

        result['unit_number'] = street_components.get('unit_number', '')
        result['street_number'] = street_components.get('street_number', '')
        result['street_name'] = street_components.get('street_name', '')
        result['street_type'] = street_components.get('street_type', '')
        result['unparsed_components'] = street_components.get('unparsed_components', '')
        result['parsing_notes'].extend(street_components.get('parsing_notes', []))

        # Parse locality components
        result['suburb'] = self._normalize_suburb(suburb)
        result['state'] = self._normalize_state(state)
        result['postcode'] = self._normalize_postcode(postcode)

        # Validate consistency
        inconsistencies = self._check_consistency(result)
        result['inconsistency_flags'].extend(inconsistencies)

        return result

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text or not isinstance(text, str):
            return ""

        # Convert to uppercase
        text = text.upper().strip()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        return text

    def _is_international(self, street_address: str, suburb: str, state: str,
                         postcode: str) -> bool:
        """Check if address appears to be international."""
        if not self.international_config.get('enabled', True):
            return False

        # Check for country tokens
        country_tokens = self.international_config.get('country_tokens', [])
        full_address = f"{street_address} {suburb} {state} {postcode}".upper()

        for country in country_tokens:
            if country.upper() in full_address:
                return True

        # Check postcode format
        if self.international_config.get('require_four_digit_postcode', True):
            if postcode and not re.match(r'^\d{4}$', postcode):
                return True

        # Check state validity
        if state and state not in self.valid_states:
            # Try to normalize it
            normalized_state = self.state_map.get(state.upper())
            if not normalized_state:
                return True

        return False

    def _is_po_box(self, street_address: str) -> bool:
        """Check if address is a PO Box."""
        po_box_prefixes = self.parsing_config.get('po_box_prefixes', [])

        for prefix in po_box_prefixes:
            if street_address.startswith(prefix.upper()):
                return True

        return False

    def _is_rmb(self, street_address: str) -> bool:
        """Check if address is an RMB (Roadside Mail Bag)."""
        rmb_prefixes = self.parsing_config.get('rmb_prefixes', [])

        for prefix in rmb_prefixes:
            if street_address.startswith(prefix.upper()):
                return True

        return False

    def _parse_po_box(self, street_address: str, suburb: str, state: str,
                     postcode: str) -> Dict:
        """Parse PO Box address."""
        result = {
            'unit_number': '',
            'street_number': '',
            'street_name': '',
            'street_type': 'PO Box',
            'suburb': self._normalize_suburb(suburb),
            'state': self._normalize_state(state),
            'postcode': self._normalize_postcode(postcode),
            'unparsed_components': '',
            'inconsistency_flags': [],
            'parsing_notes': ['PO_BOX']
        }

        # Extract box number
        box_number_match = re.search(r'BOX\s+(\d+[A-Z]?)', street_address)
        if box_number_match:
            result['street_number'] = box_number_match.group(1)

        return result

    def _parse_rmb(self, street_address: str, suburb: str, state: str,
                  postcode: str) -> Dict:
        """Parse RMB (Roadside Mail Bag) address."""
        result = {
            'unit_number': '',
            'street_number': '',
            'street_name': '',
            'street_type': 'RMB',
            'suburb': self._normalize_suburb(suburb),
            'state': self._normalize_state(state),
            'postcode': self._normalize_postcode(postcode),
            'unparsed_components': '',
            'inconsistency_flags': [],
            'parsing_notes': ['RMB']
        }

        # Extract RMB number
        rmb_number_match = re.search(r'RMB\s+(\d+[A-Z]?)', street_address)
        if rmb_number_match:
            result['street_number'] = rmb_number_match.group(1)

        return result

    def _parse_street_address(self, street_address: str) -> Dict:
        """Parse street address into components."""
        result = {
            'unit_number': '',
            'street_number': '',
            'street_name': '',
            'street_type': '',
            'unparsed_components': '',
            'parsing_notes': []
        }

        if not street_address:
            return result

        # Tokenize
        tokens = street_address.split()

        # Extract street type (usually at the end)
        street_type, street_type_index = self._extract_street_type(tokens)
        result['street_type'] = street_type

        if street_type_index >= 0:
            # Remove street type from tokens
            tokens = tokens[:street_type_index]

        # Extract unit and street number
        unit_number, street_number, number_end_index = self._extract_numbers(tokens)
        result['unit_number'] = unit_number
        result['street_number'] = street_number

        # Remaining tokens are street name
        if number_end_index >= 0 and number_end_index < len(tokens):
            street_name_tokens = tokens[number_end_index + 1:]
            result['street_name'] = self._normalize_street_name(' '.join(street_name_tokens))
        elif number_end_index < 0 and len(tokens) > 0:
            # No number found, everything might be street name
            result['street_name'] = self._normalize_street_name(' '.join(tokens))

        # Check for unparsed components
        if not result['street_number'] and not result['street_name']:
            result['unparsed_components'] = street_address
            result['parsing_notes'].append('UNABLE_TO_PARSE')

        return result

    def _extract_street_type(self, tokens: List[str]) -> Tuple[str, int]:
        """
        Extract and normalize street type from token list.

        Returns:
            Tuple of (normalized_street_type, token_index)
        """
        # Try to find street type starting from the end
        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]

            # Direct lookup
            if token in self.street_type_map:
                return self.street_type_map[token], i

        # Fuzzy matching
        if self.street_types_config.get('fuzzy_matching', {}).get('enabled', True):
            min_score = self.street_types_config.get('fuzzy_matching', {}).get('min_score', 85)

            for i in range(len(tokens) - 1, max(-1, len(tokens) - 3), -1):
                token = tokens[i]

                match = process.extractOne(
                    token,
                    self.canonical_street_types,
                    scorer=fuzz.ratio
                )

                if match and match[1] >= min_score:
                    return match[0], i

        return '', -1

    def _extract_numbers(self, tokens: List[str]) -> Tuple[str, str, int]:
        """
        Extract unit and street numbers from tokens.

        Returns:
            Tuple of (unit_number, street_number, end_index)
        """
        unit_number = ''
        street_number = ''
        end_index = -1

        unit_prefixes = [p.upper() for p in self.parsing_config.get('unit_prefixes', [])]
        unit_street_separators = self.parsing_config.get('unit_street_separators', ['/'])

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Check for unit prefix
            if token in unit_prefixes:
                # Next token should be unit number
                if i + 1 < len(tokens):
                    unit_number = self._extract_numeric(tokens[i + 1])
                    end_index = i + 1
                    i += 2
                    continue

            # Check for unit/street separator (e.g., "5/6")
            if '/' in token or '\\' in token:
                parts = re.split(r'[/\\]', token)
                if len(parts) == 2:
                    unit_number = self._extract_numeric(parts[0])
                    street_number = self._extract_numeric(parts[1])
                    end_index = i
                    break

            # Check if token is numeric (could be street number or unit)
            if re.match(r'^\d+[A-Z]?$', token):
                # Check if next token is also numeric (then this is unit, next is street)
                if i + 1 < len(tokens) and re.match(r'^\d+[A-Z]?$', tokens[i + 1]):
                    unit_number = self._extract_numeric(token)
                    street_number = self._extract_numeric(tokens[i + 1])
                    end_index = i + 1
                    break
                else:
                    # This is the street number
                    street_number = self._extract_numeric(token)
                    end_index = i
                    break

            i += 1

        # Handle street number ranges (e.g., "10-12")
        if street_number and '-' in street_number:
            street_number = self._handle_range(street_number)

        return unit_number, street_number, end_index

    def _extract_numeric(self, token: str) -> str:
        """Extract numeric portion from token."""
        # Check if we should strip alpha suffix
        if self.parsing_config.get('strip_street_number_alpha_suffix', True):
            match = re.match(r'^(\d+)', token)
            if match:
                return match.group(1)

        return token

    def _handle_range(self, number: str) -> str:
        """Handle street number ranges, return lowest number."""
        separators = self.parsing_config.get('street_number_range_separators', ['-'])

        for sep in separators:
            if sep in number:
                parts = number.split(sep)
                if len(parts) >= 2 and parts[0].isdigit():
                    return parts[0]

        return number

    def _normalize_street_name(self, name: str) -> str:
        """Normalize street name capitalization."""
        if not name:
            return ""

        # Title case
        name = name.title()

        # Handle special cases (Mc, Mac, O')
        name = re.sub(r'\bMc([a-z])', lambda m: f"Mc{m.group(1).upper()}", name)
        name = re.sub(r'\bMac([a-z])', lambda m: f"Mac{m.group(1).upper()}", name)
        name = re.sub(r"\bO'([a-z])", lambda m: f"O'{m.group(1).upper()}", name)

        return name

    def _normalize_suburb(self, suburb: str) -> str:
        """Normalize suburb name."""
        if not suburb:
            return ""

        suburb_upper = suburb.upper()

        # Check for direct misspelling corrections
        misspellings = self.localities_config.get('suburb_misspellings', {})
        if suburb_upper in misspellings:
            return misspellings[suburb_upper].title()

        # Apply title case
        return suburb.title()

    def _normalize_state(self, state: str) -> str:
        """Normalize state abbreviation."""
        if not state:
            return ""

        state_upper = state.upper()

        # Direct lookup
        if state_upper in self.state_map:
            return self.state_map[state_upper]

        return state

    def _normalize_postcode(self, postcode: str) -> str:
        """Normalize postcode."""
        if not postcode:
            return ""

        # Remove non-digits
        postcode = re.sub(r'\D', '', postcode)

        # Ensure 4 digits
        if len(postcode) == 4:
            return postcode

        # Pad with zeros if needed
        if len(postcode) < 4:
            return postcode.zfill(4)

        return postcode[:4]

    def _check_consistency(self, components: Dict) -> List[str]:
        """Check consistency between address components."""
        flags = []

        state = components.get('state', '')
        postcode = components.get('postcode', '')

        # Validate postcode format
        postcode_config = self.validation_config.get('postcode', {})
        pattern = postcode_config.get('pattern', r'^\d{4}$')

        if postcode and not re.match(pattern, postcode):
            flags.append('INVALID_POSTCODE_FORMAT')

        # Check postcode/state consistency
        if state and postcode:
            ranges = postcode_config.get('ranges', {}).get(state, [])
            if ranges:
                postcode_int = int(postcode) if postcode.isdigit() else 0
                in_range = any(start <= postcode_int <= end for start, end in ranges)

                if not in_range:
                    flags.append('POSTCODE_STATE_MISMATCH')

        # Validate street number
        street_number = components.get('street_number', '')
        if street_number and street_number.isdigit():
            street_num_config = self.validation_config.get('street_number', {})
            max_val = street_num_config.get('max_value', 99999)
            min_val = street_num_config.get('min_value', 1)

            num = int(street_number)
            if num < min_val or num > max_val:
                flags.append('INVALID_STREET_NUMBER')

        return flags

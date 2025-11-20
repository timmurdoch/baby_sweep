"""
Core address cleaning functionality.

This module provides the main clean_addresses function that orchestrates
all address cleaning components: schema mapping, parsing, ML prediction,
G-NAF validation, and confidence scoring.
"""

import os
import yaml
import logging
from typing import Dict, Optional
import pandas as pd

from .schemas import SchemaMapper, ensure_record_id
from .parsing import AddressParser
from .ml_model import AddressMLModel
from .gnaf import GNAFMatcher
from .scoring import ConfidenceScorer

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file. If None, uses default.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If config file is invalid
    """
    if config_path is None:
        # Use default config from package
        package_dir = os.path.dirname(__file__)
        config_path = os.path.join(package_dir, 'config', 'default_config.yaml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_path}")
    return config


def clean_addresses(
    df: pd.DataFrame,
    config_path: Optional[str] = None,
    config: Optional[Dict] = None,
    schema_name: str = 'default',
    gnaf_connection_url: Optional[str] = None,
    ml_model_path: Optional[str] = None,
    use_ml: bool = True,
    use_gnaf: bool = True
) -> pd.DataFrame:
    """
    Clean and normalize a batch of addresses.

    This is the main entry point for the address cleaning library.

    Args:
        df: Input DataFrame with address columns
        config_path: Path to YAML configuration file (optional)
        config: Configuration dictionary (overrides config_path if provided)
        schema_name: Name of schema to use for column mapping
        gnaf_connection_url: G-NAF database connection URL (overrides config)
        ml_model_path: Path to ML model file (overrides config)
        use_ml: Whether to use ML model predictions
        use_gnaf: Whether to use G-NAF validation

    Returns:
        DataFrame with cleaned address components and metadata

    Raises:
        ValueError: If input validation fails
    """
    # Load configuration
    if config is None:
        config = load_config(config_path)

    # Setup logging
    _setup_logging(config)

    # Validate input
    if df is None or len(df) == 0:
        raise ValueError("Input DataFrame is empty")

    logger.info(f"Starting address cleaning for {len(df)} records")

    # Check batch size limit
    max_batch_size = config.get('processing', {}).get('max_batch_size', 50000)
    if len(df) > max_batch_size:
        logger.warning(
            f"Input has {len(df)} rows, which exceeds max_batch_size of {max_batch_size}. "
            f"Consider processing in smaller batches."
        )

    # Initialize components
    schema_mapper = SchemaMapper(config)
    parser = AddressParser(config)
    scorer = ConfidenceScorer(config)

    # Initialize optional components
    ml_model = None
    gnaf_matcher = None

    if use_ml:
        ml_model = AddressMLModel(config, model_path=ml_model_path)
        if not ml_model.is_enabled():
            logger.warning("ML model is not available, proceeding with rule-based parsing only")

    if use_gnaf:
        try:
            gnaf_matcher = GNAFMatcher(config, connection_url=gnaf_connection_url)
            if not gnaf_matcher.enabled:
                logger.warning("G-NAF matching is not available")
        except Exception as e:
            logger.warning(f"Could not initialize G-NAF matcher: {e}")

    # Map columns according to schema
    try:
        df_mapped = schema_mapper.map_columns(df.copy(), schema_name)
    except ValueError as e:
        logger.error(f"Schema mapping failed: {e}")
        raise

    # Ensure record ID
    df_mapped = ensure_record_id(df_mapped)

    # Process each address
    results = []

    for idx, row in df_mapped.iterrows():
        try:
            result = _clean_single_address(
                row,
                parser,
                ml_model,
                gnaf_matcher,
                scorer,
                config
            )
            results.append(result)

        except Exception as e:
            if config.get('processing', {}).get('continue_on_error', True):
                logger.error(f"Error processing record {idx}: {e}")
                # Create error result
                error_result = _create_error_result(row, str(e))
                results.append(error_result)
            else:
                raise

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Merge with original data if configured
    if config.get('processing', {}).get('preserve_original_columns', True):
        # Add prefix to original columns to distinguish them
        original_cols = {}
        for col in df.columns:
            if col not in results_df.columns:
                original_cols[f'original_{col}'] = df[col]

        if original_cols:
            for col_name, col_data in original_cols.items():
                results_df[col_name] = col_data.values

    logger.info(f"Successfully cleaned {len(results_df)} addresses")

    return results_df


def _clean_single_address(
    row: pd.Series,
    parser: AddressParser,
    ml_model: Optional[AddressMLModel],
    gnaf_matcher: Optional[GNAFMatcher],
    scorer: ConfidenceScorer,
    config: Dict
) -> Dict:
    """
    Clean a single address.

    Args:
        row: DataFrame row with address data
        parser: Address parser instance
        ml_model: ML model instance (optional)
        gnaf_matcher: G-NAF matcher instance (optional)
        scorer: Confidence scorer instance
        config: Configuration dictionary

    Returns:
        Dictionary of cleaned address components
    """
    # Extract input fields
    street_address = str(row.get('street_address', ''))
    suburb = str(row.get('suburb', ''))
    state = str(row.get('state', ''))
    postcode = str(row.get('postcode', ''))
    record_id = row.get('record_id', '')

    # Try ML prediction first
    ml_prediction = None
    ml_confidence = None

    if ml_model and ml_model.is_enabled():
        ml_prediction = ml_model.predict(street_address)
        if ml_prediction:
            ml_confidence = ml_prediction.get('ml_confidence')

    # Use ML prediction or fall back to rule-based parsing
    use_ml_prediction = ml_model and ml_prediction and ml_model.should_use_prediction(ml_prediction)

    if use_ml_prediction:
        logger.debug(f"Using ML prediction for record {record_id}")
        components = ml_prediction
        parsing_notes = ['ML_PREDICTION_USED']
    else:
        logger.debug(f"Using rule-based parsing for record {record_id}")
        components = parser.parse_address(street_address, suburb, state, postcode)
        parsing_notes = components.pop('parsing_notes', [])

    # Extract flags
    inconsistency_flags = components.pop('inconsistency_flags', [])
    corrections_applied = components.pop('corrections_applied', [])

    # G-NAF matching and correction
    gnaf_flags = []
    gnaf_match_score = 0.0

    if gnaf_matcher and gnaf_matcher.enabled:
        matched_components, gnaf_match_score, gnaf_flags = gnaf_matcher.match_address(components)

        if matched_components:
            # Apply corrections if appropriate
            components = gnaf_matcher.apply_corrections(
                components,
                matched_components,
                gnaf_match_score
            )

            # Track corrections
            if 'corrections_applied' in components:
                corrections_applied.extend(components.pop('corrections_applied'))

    else:
        gnaf_flags = ['GNAF_DISABLED']

    # Calculate confidence score
    confidence_level = scorer.calculate_score(
        components,
        parsing_notes,
        inconsistency_flags,
        gnaf_flags,
        gnaf_match_score,
        corrections_applied,
        ml_confidence
    )

    # Determine if address is valid
    is_valid = scorer.is_valid_address(components, confidence_level)
    is_international = 'INTERNATIONAL_ADDRESS' in parsing_notes

    # Mark invalid addresses
    if not is_valid:
        components['street_name'] = "INVALID ADDRESS"
        components['is_invalid_address'] = True
    else:
        components['is_invalid_address'] = False

    # Build final result
    result = {
        'record_id': record_id,
        'unit_number': components.get('unit_number', ''),
        'street_number': components.get('street_number', ''),
        'street_name': components.get('street_name', ''),
        'street_type': components.get('street_type', ''),
        'suburb': components.get('suburb', ''),
        'state': components.get('state', ''),
        'postcode': components.get('postcode', ''),
        'confidence_level': confidence_level,
        'is_international': is_international,
        'is_invalid_address': components.get('is_invalid_address', False),
        'inconsistency_flags': _format_flags(inconsistency_flags + gnaf_flags, config),
        'unparsed_components': components.get('unparsed_components', ''),
        # Preserve raw input fields
        'raw_street_address': street_address,
        'raw_suburb': suburb,
        'raw_state': state,
        'raw_postcode': postcode,
    }

    return result


def _create_error_result(row: pd.Series, error_message: str) -> Dict:
    """Create a result dictionary for a failed record."""
    return {
        'record_id': row.get('record_id', ''),
        'unit_number': '',
        'street_number': '',
        'street_name': 'INVALID ADDRESS',
        'street_type': '',
        'suburb': '',
        'state': '',
        'postcode': '',
        'confidence_level': 0,
        'is_international': False,
        'is_invalid_address': True,
        'inconsistency_flags': f'PROCESSING_ERROR: {error_message}',
        'unparsed_components': str(row.get('street_address', '')),
        'raw_street_address': str(row.get('street_address', '')),
        'raw_suburb': str(row.get('suburb', '')),
        'raw_state': str(row.get('state', '')),
        'raw_postcode': str(row.get('postcode', '')),
    }


def _format_flags(flags: list, config: Dict) -> str:
    """Format flags according to configuration."""
    flags_format = config.get('output', {}).get('inconsistency_flags_format', 'comma_separated')

    if not flags:
        return ''

    if flags_format == 'json':
        import json
        return json.dumps(flags)
    else:
        # comma_separated
        return ', '.join(flags)


def _setup_logging(config: Dict):
    """Setup logging based on configuration."""
    logging_config = config.get('logging', {})

    log_level = logging_config.get('level', 'INFO')
    log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format
    )

    # Configure file logging if enabled
    if logging_config.get('log_to_file', False):
        log_file_path = logging_config.get('log_file_path', 'address_cleaner.log')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)


def clean_csv(
    input_path: str,
    output_path: str,
    config_path: Optional[str] = None,
    schema_name: str = 'default',
    gnaf_connection_url: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Clean addresses from a CSV file and write results to another CSV.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file
        config_path: Path to configuration file
        schema_name: Name of schema to use
        gnaf_connection_url: G-NAF database connection URL
        **kwargs: Additional arguments passed to clean_addresses()

    Returns:
        Cleaned DataFrame

    Raises:
        FileNotFoundError: If input file not found
    """
    logger.info(f"Reading addresses from {input_path}")

    # Read input CSV
    df = pd.read_csv(input_path, encoding='utf-8')

    # Clean addresses
    cleaned_df = clean_addresses(
        df,
        config_path=config_path,
        schema_name=schema_name,
        gnaf_connection_url=gnaf_connection_url,
        **kwargs
    )

    # Write output CSV
    logger.info(f"Writing cleaned addresses to {output_path}")
    cleaned_df.to_csv(output_path, index=False, encoding='utf-8')

    return cleaned_df

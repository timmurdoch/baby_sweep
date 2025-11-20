"""
Command-line interface for address cleaner.

Provides a CLI wrapper around the core cleaning functionality.
"""

import argparse
import sys
import logging
from typing import Optional

from .core import clean_csv, load_config

logger = logging.getLogger(__name__)


def main(args: Optional[list] = None):
    """
    Main CLI entry point.

    Args:
        args: Optional list of arguments (for testing). If None, uses sys.argv.
    """
    parser = argparse.ArgumentParser(
        description='Clean and normalize Australian addresses from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default configuration
  python -m address_cleaner --input addresses.csv --output cleaned.csv

  # Use custom configuration
  python -m address_cleaner --input addresses.csv --output cleaned.csv \\
    --config my_config.yaml

  # Specify schema and G-NAF connection
  python -m address_cleaner --input addresses.csv --output cleaned.csv \\
    --schema vendor_x \\
    --gnaf-url postgresql://user:pass@localhost:5432/gnaf

  # Disable G-NAF matching
  python -m address_cleaner --input addresses.csv --output cleaned.csv \\
    --no-gnaf

  # Disable ML model
  python -m address_cleaner --input addresses.csv --output cleaned.csv \\
    --no-ml
        """
    )

    # Required arguments
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='Input CSV file path'
    )

    parser.add_argument(
        '--output',
        '-o',
        required=True,
        help='Output CSV file path'
    )

    # Optional arguments
    parser.add_argument(
        '--config',
        '-c',
        help='Path to YAML configuration file (default: uses built-in config)'
    )

    parser.add_argument(
        '--schema',
        '-s',
        default='default',
        help='Schema name for column mapping (default: default)'
    )

    parser.add_argument(
        '--gnaf-url',
        help='G-NAF PostgreSQL connection URL (e.g., postgresql://user:pass@host:port/dbname)'
    )

    parser.add_argument(
        '--ml-model',
        help='Path to ML model file (overrides config)'
    )

    parser.add_argument(
        '--no-gnaf',
        action='store_true',
        help='Disable G-NAF validation'
    )

    parser.add_argument(
        '--no-ml',
        action='store_true',
        help='Disable ML model predictions'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Suppress all output except errors'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Setup logging
    if parsed_args.quiet:
        log_level = logging.ERROR
    elif parsed_args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Validate inputs
    try:
        # Check if input file exists
        import os
        if not os.path.exists(parsed_args.input):
            logger.error(f"Input file not found: {parsed_args.input}")
            return 1

        # Check if output directory exists
        output_dir = os.path.dirname(parsed_args.output)
        if output_dir and not os.path.exists(output_dir):
            logger.error(f"Output directory does not exist: {output_dir}")
            return 1

        # Load and validate config if provided
        if parsed_args.config:
            if not os.path.exists(parsed_args.config):
                logger.error(f"Config file not found: {parsed_args.config}")
                return 1

            try:
                load_config(parsed_args.config)
            except Exception as e:
                logger.error(f"Invalid configuration file: {e}")
                return 1

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return 1

    # Run address cleaning
    try:
        logger.info("Starting address cleaning...")
        logger.info(f"Input: {parsed_args.input}")
        logger.info(f"Output: {parsed_args.output}")
        logger.info(f"Schema: {parsed_args.schema}")

        if parsed_args.config:
            logger.info(f"Config: {parsed_args.config}")

        if parsed_args.no_gnaf:
            logger.info("G-NAF validation: DISABLED")
        elif parsed_args.gnaf_url:
            logger.info(f"G-NAF URL: {parsed_args.gnaf_url}")

        if parsed_args.no_ml:
            logger.info("ML model: DISABLED")
        elif parsed_args.ml_model:
            logger.info(f"ML model: {parsed_args.ml_model}")

        # Clean addresses
        result_df = clean_csv(
            input_path=parsed_args.input,
            output_path=parsed_args.output,
            config_path=parsed_args.config,
            schema_name=parsed_args.schema,
            gnaf_connection_url=parsed_args.gnaf_url,
            ml_model_path=parsed_args.ml_model,
            use_ml=not parsed_args.no_ml,
            use_gnaf=not parsed_args.no_gnaf
        )

        # Print summary
        total_records = len(result_df)
        invalid_count = result_df['is_invalid_address'].sum()
        international_count = result_df['is_international'].sum()
        avg_confidence = result_df['confidence_level'].mean()

        logger.info("=" * 60)
        logger.info("CLEANING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Invalid addresses: {invalid_count} ({invalid_count/total_records*100:.1f}%)")
        logger.info(f"International addresses: {international_count} ({international_count/total_records*100:.1f}%)")
        logger.info(f"Average confidence score: {avg_confidence:.1f}")

        # Confidence distribution
        confidence_bins = {
            'Excellent (95-100)': ((result_df['confidence_level'] >= 95) & (result_df['confidence_level'] <= 100)).sum(),
            'Very High (85-94)': ((result_df['confidence_level'] >= 85) & (result_df['confidence_level'] < 95)).sum(),
            'High (75-84)': ((result_df['confidence_level'] >= 75) & (result_df['confidence_level'] < 85)).sum(),
            'Moderate (60-74)': ((result_df['confidence_level'] >= 60) & (result_df['confidence_level'] < 75)).sum(),
            'Low (40-59)': ((result_df['confidence_level'] >= 40) & (result_df['confidence_level'] < 60)).sum(),
            'Very Low (0-39)': ((result_df['confidence_level'] >= 0) & (result_df['confidence_level'] < 40)).sum(),
        }

        logger.info("\nConfidence Distribution:")
        for category, count in confidence_bins.items():
            logger.info(f"  {category}: {count} ({count/total_records*100:.1f}%)")

        logger.info("=" * 60)
        logger.info(f"Results written to: {parsed_args.output}")
        logger.info("Address cleaning completed successfully!")

        return 0

    except KeyboardInterrupt:
        logger.error("\nOperation cancelled by user")
        return 130

    except Exception as e:
        logger.error(f"Error during address cleaning: {e}", exc_info=parsed_args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())

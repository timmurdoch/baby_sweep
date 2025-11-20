"""
Schema detection and column mapping for address cleaning.

This module handles mapping between physical column names in input data
and logical field names used by the address cleaning process.
"""

import pandas as pd
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class SchemaMapper:
    """Maps physical column names to logical field names."""

    def __init__(self, config: Dict):
        """
        Initialize schema mapper with configuration.

        Args:
            config: Configuration dictionary containing schema definitions
        """
        self.config = config
        self.schemas = config.get('schemas', {})

    def get_schema(self, schema_name: str = 'default') -> Dict[str, str]:
        """
        Get schema mapping by name.

        Args:
            schema_name: Name of the schema to retrieve

        Returns:
            Dictionary mapping logical field names to physical column names

        Raises:
            ValueError: If schema_name is not found in configuration
        """
        if schema_name not in self.schemas:
            available_schemas = ', '.join(self.schemas.keys())
            raise ValueError(
                f"Schema '{schema_name}' not found in configuration. "
                f"Available schemas: {available_schemas}"
            )

        return self.schemas[schema_name]

    def map_columns(self, df: pd.DataFrame, schema_name: str = 'default') -> pd.DataFrame:
        """
        Map physical column names to logical field names.

        Args:
            df: Input DataFrame with physical column names
            schema_name: Name of the schema to use for mapping

        Returns:
            DataFrame with standardized logical column names

        Raises:
            ValueError: If required columns are missing
        """
        schema = self.get_schema(schema_name)

        # Create mapping from physical to logical names
        column_mapping = {}
        missing_columns = []

        for logical_name, physical_name in schema.items():
            if physical_name in df.columns:
                column_mapping[physical_name] = logical_name
            else:
                # Check if it's optional (id_column is optional)
                if logical_name != 'id_column':
                    missing_columns.append(physical_name)
                else:
                    logger.debug(f"Optional column '{physical_name}' not found in input")

        if missing_columns:
            raise ValueError(
                f"Required columns missing from input DataFrame: {', '.join(missing_columns)}"
            )

        # Rename columns according to mapping
        df_mapped = df.rename(columns=column_mapping)

        # Generate synthetic ID if id_column not present
        if 'id' not in df_mapped.columns:
            df_mapped['_record_id'] = range(1, len(df_mapped) + 1)
            logger.info("Generated synthetic _record_id column")
        else:
            df_mapped['_record_id'] = df_mapped['id']

        return df_mapped

    def detect_schema(self, df: pd.DataFrame) -> str:
        """
        Attempt to auto-detect which schema matches the input DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Name of the best matching schema, or 'default'
        """
        df_columns = set(df.columns)
        best_match = 'default'
        best_match_count = 0

        for schema_name, schema in self.schemas.items():
            # Count how many physical columns from this schema exist in the DataFrame
            physical_columns = set(schema.values())
            match_count = len(physical_columns.intersection(df_columns))

            if match_count > best_match_count:
                best_match_count = match_count
                best_match = schema_name

        logger.info(f"Auto-detected schema: {best_match} (matched {best_match_count} columns)")
        return best_match

    def get_logical_columns(self, schema_name: str = 'default') -> List[str]:
        """
        Get list of logical column names for a schema.

        Args:
            schema_name: Name of the schema

        Returns:
            List of logical field names
        """
        schema = self.get_schema(schema_name)
        return list(schema.keys())

    def validate_dataframe(self, df: pd.DataFrame, schema_name: str = 'default') -> tuple:
        """
        Validate that DataFrame has required columns for the schema.

        Args:
            df: Input DataFrame
            schema_name: Name of the schema to validate against

        Returns:
            Tuple of (is_valid: bool, missing_columns: List[str])
        """
        schema = self.get_schema(schema_name)
        required_columns = [
            physical_name for logical_name, physical_name in schema.items()
            if logical_name != 'id_column'  # id_column is optional
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        is_valid = len(missing_columns) == 0

        return is_valid, missing_columns


def ensure_record_id(df: pd.DataFrame, id_column: Optional[str] = None) -> pd.DataFrame:
    """
    Ensure DataFrame has a record_id column for tracking.

    Args:
        df: Input DataFrame
        id_column: Name of existing ID column, if any

    Returns:
        DataFrame with record_id column added
    """
    df = df.copy()

    if id_column and id_column in df.columns:
        df['record_id'] = df[id_column]
    elif 'id' in df.columns:
        df['record_id'] = df['id']
    elif '_record_id' in df.columns:
        df['record_id'] = df['_record_id']
    else:
        # Generate synthetic ID
        df['record_id'] = [f"REC{i:06d}" for i in range(1, len(df) + 1)]
        logger.info("Generated synthetic record_id column")

    return df


def get_id_column_name(config: Dict, schema_name: str = 'default') -> Optional[str]:
    """
    Get the ID column name from configuration.

    Args:
        config: Configuration dictionary
        schema_name: Name of the schema

    Returns:
        ID column name, or None if not specified
    """
    schemas = config.get('schemas', {})
    schema = schemas.get(schema_name, {})
    return schema.get('id_column')

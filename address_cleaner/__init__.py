"""
Address Cleaner - Australian Address Cleaning and Normalization

A Python library for cleaning, parsing, and normalizing Australian addresses.
Supports batch processing, ML-based predictions, G-NAF validation, and confidence scoring.
"""

__version__ = "1.0.0"
__author__ = "Solucio"
__description__ = "Australian address cleaning and normalization library"

from .core import clean_addresses, clean_csv, load_config
from .parsing import AddressParser
from .schemas import SchemaMapper
from .ml_model import AddressMLModel
from .gnaf import GNAFMatcher
from .scoring import ConfidenceScorer

__all__ = [
    'clean_addresses',
    'clean_csv',
    'load_config',
    'AddressParser',
    'SchemaMapper',
    'AddressMLModel',
    'GNAFMatcher',
    'ConfidenceScorer',
]

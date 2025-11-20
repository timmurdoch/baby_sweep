"""
Machine Learning model infrastructure for address parsing.

This module provides infrastructure for training and using ML models
to predict address component labels from raw text.
"""

import os
import pickle
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. ML features will be disabled.")


class AddressMLModel:
    """Machine learning model for address component prediction."""

    def __init__(self, config: Dict, model_path: Optional[str] = None):
        """
        Initialize ML model.

        Args:
            config: Configuration dictionary
            model_path: Optional path to saved model (overrides config)
        """
        self.config = config
        self.ml_config = config.get('ml_model', {})
        self.enabled = self.ml_config.get('enabled', True) and SKLEARN_AVAILABLE

        if not SKLEARN_AVAILABLE and self.enabled:
            logger.warning("ML model is enabled but scikit-learn is not available")
            self.enabled = False

        self.model_path = model_path or self.ml_config.get('model_path', '')
        self.min_confidence = self.ml_config.get('min_confidence', 0.7)
        self.fallback_to_rules = self.ml_config.get('fallback_to_rules', True)

        self.model = None
        self.vectorizer = None
        self.label_encoder = None

        if self.enabled and self.model_path and os.path.exists(self.model_path):
            self.load_model(self.model_path)

    def load_model(self, model_path: str) -> bool:
        """
        Load trained model from disk.

        Args:
            model_path: Path to pickled model file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data.get('model')
            self.vectorizer = model_data.get('vectorizer')
            self.label_encoder = model_data.get('label_encoder')

            logger.info(f"Successfully loaded ML model from {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load ML model from {model_path}: {e}")
            self.enabled = False
            return False

    def train(self, training_data: pd.DataFrame) -> bool:
        """
        Train the model on labeled address data.

        Args:
            training_data: DataFrame with columns:
                - raw_street_address
                - clean_unit_number
                - clean_street_number
                - clean_street_name
                - clean_street_type
                - clean_suburb
                - clean_state
                - clean_postcode

        Returns:
            True if training successful, False otherwise
        """
        if not SKLEARN_AVAILABLE:
            logger.error("Cannot train model: scikit-learn not available")
            return False

        try:
            # Prepare training data
            X, y = self._prepare_training_data(training_data)

            if len(X) == 0:
                logger.error("No training data available")
                return False

            # Initialize components
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                analyzer='char_wb'
            )

            self.label_encoder = LabelEncoder()

            # Fit vectorizer and encoder
            X_vectorized = self.vectorizer.fit_transform(X)
            y_encoded = self.label_encoder.fit_transform(y)

            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )

            self.model.fit(X_vectorized, y_encoded)

            logger.info(f"Successfully trained model on {len(X)} samples")
            self.enabled = True
            return True

        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            return False

    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Prepare training data from labeled addresses.

        Returns:
            Tuple of (tokens, labels)
        """
        tokens = []
        labels = []

        for _, row in df.iterrows():
            raw_address = str(row.get('raw_street_address', ''))

            # Extract labeled components
            components = {
                'UNIT_NUMBER': str(row.get('clean_unit_number', '')),
                'STREET_NUMBER': str(row.get('clean_street_number', '')),
                'STREET_NAME': str(row.get('clean_street_name', '')),
                'STREET_TYPE': str(row.get('clean_street_type', '')),
                'SUBURB': str(row.get('clean_suburb', '')),
                'STATE': str(row.get('clean_state', '')),
                'POSTCODE': str(row.get('clean_postcode', '')),
            }

            # Tokenize and label
            address_tokens = raw_address.split()

            for token in address_tokens:
                tokens.append(token)

                # Assign label based on content
                label = self._assign_label(token, components)
                labels.append(label)

        return tokens, labels

    def _assign_label(self, token: str, components: Dict[str, str]) -> str:
        """
        Assign a label to a token based on labeled components.

        Args:
            token: Token to label
            components: Dictionary of labeled components

        Returns:
            Label string
        """
        token_upper = token.upper()

        # Check each component
        for label, value in components.items():
            if value and token_upper in value.upper():
                return label

        return 'OTHER'

    def predict(self, street_address: str) -> Optional[Dict]:
        """
        Predict address components from raw street address.

        Args:
            street_address: Raw street address string

        Returns:
            Dictionary of predicted components with confidence scores,
            or None if prediction not available
        """
        if not self.enabled or not self.model:
            return None

        try:
            tokens = street_address.split()

            if not tokens:
                return None

            # Vectorize tokens
            X = self.vectorizer.transform(tokens)

            # Predict labels and probabilities
            predictions = self.model.predict(X)
            probabilities = self.model.predict_proba(X)

            # Decode labels
            labels = self.label_encoder.inverse_transform(predictions)

            # Extract components
            components = self._extract_components_from_labels(
                tokens, labels, probabilities
            )

            return components

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

    def _extract_components_from_labels(self, tokens: List[str], labels: List[str],
                                       probabilities: np.ndarray) -> Dict:
        """
        Extract address components from labeled tokens.

        Args:
            tokens: List of tokens
            labels: List of predicted labels
            probabilities: Prediction probabilities

        Returns:
            Dictionary of components with confidence scores
        """
        components = {
            'unit_number': '',
            'street_number': '',
            'street_name': '',
            'street_type': '',
            'suburb': '',
            'state': '',
            'postcode': '',
            'ml_confidence': 0.0,
            'ml_predictions': []
        }

        # Group consecutive tokens with same label
        current_label = None
        current_tokens = []
        current_confidences = []

        for i, (token, label) in enumerate(zip(tokens, labels)):
            confidence = probabilities[i].max()

            if label == current_label:
                current_tokens.append(token)
                current_confidences.append(confidence)
            else:
                # Save previous group
                if current_label and current_label != 'OTHER':
                    self._add_component(
                        components,
                        current_label,
                        ' '.join(current_tokens),
                        np.mean(current_confidences)
                    )

                # Start new group
                current_label = label
                current_tokens = [token]
                current_confidences = [confidence]

        # Save last group
        if current_label and current_label != 'OTHER':
            self._add_component(
                components,
                current_label,
                ' '.join(current_tokens),
                np.mean(current_confidences)
            )

        # Calculate overall confidence
        if len(current_confidences) > 0:
            components['ml_confidence'] = float(np.mean(probabilities.max(axis=1)))

        return components

    def _add_component(self, components: Dict, label: str, value: str, confidence: float):
        """Add a predicted component to the results dictionary."""
        label_map = {
            'UNIT_NUMBER': 'unit_number',
            'STREET_NUMBER': 'street_number',
            'STREET_NAME': 'street_name',
            'STREET_TYPE': 'street_type',
            'SUBURB': 'suburb',
            'STATE': 'state',
            'POSTCODE': 'postcode',
        }

        field_name = label_map.get(label)
        if field_name:
            components[field_name] = value
            components['ml_predictions'].append({
                'field': field_name,
                'value': value,
                'confidence': float(confidence)
            })

    def save_model(self, model_path: str) -> bool:
        """
        Save trained model to disk.

        Args:
            model_path: Path to save model

        Returns:
            True if successful, False otherwise
        """
        if not self.model or not self.vectorizer or not self.label_encoder:
            logger.error("Cannot save model: model not trained")
            return False

        try:
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'config': self.ml_config
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(model_path), exist_ok=True)

            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)

            logger.info(f"Successfully saved model to {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model to {model_path}: {e}")
            return False

    def is_enabled(self) -> bool:
        """Check if ML model is enabled and ready."""
        return self.enabled and self.model is not None

    def should_use_prediction(self, prediction: Optional[Dict]) -> bool:
        """
        Determine if ML prediction should be used or fall back to rules.

        Args:
            prediction: ML prediction dictionary

        Returns:
            True if prediction should be used, False if should fall back to rules
        """
        if not prediction:
            return False

        confidence = prediction.get('ml_confidence', 0.0)

        if confidence < self.min_confidence:
            if self.fallback_to_rules:
                logger.debug(f"ML confidence {confidence:.2f} below threshold, falling back to rules")
                return False
            else:
                return True

        return True

#!/usr/bin/env python3
"""
Example of training an ML model for address parsing.

This example demonstrates:
- Loading training data
- Training an ML model
- Saving the trained model
- Using the model for predictions
"""

import pandas as pd
from address_cleaner import AddressMLModel, load_config, clean_addresses


def main():
    print("=" * 60)
    print("Address Cleaner - ML Model Training Example")
    print("=" * 60)

    # Load configuration
    print("\n1. Loading configuration...")
    config = load_config()

    # Load training data
    print("\n2. Loading training data...")
    training_data = pd.read_csv('examples/sample_training_data.csv')
    print(f"   Loaded {len(training_data)} training samples")

    # Display sample training data
    print("\n3. Sample training data (first 3 rows):")
    display_cols = [
        'raw_street_address',
        'clean_street_number',
        'clean_street_name',
        'clean_street_type'
    ]
    print(training_data[display_cols].head(3).to_string(index=False))

    # Initialize ML model
    print("\n4. Initializing ML model...")
    ml_model = AddressMLModel(config)

    # Train the model
    print("\n5. Training ML model...")
    print("   This may take a moment...")

    success = ml_model.train(training_data)

    if success:
        print("   ✓ Model trained successfully!")

        # Save the model
        model_path = 'address_cleaner/models/address_parser_model.pkl'
        print(f"\n6. Saving model to {model_path}...")

        if ml_model.save_model(model_path):
            print("   ✓ Model saved successfully!")
        else:
            print("   ✗ Failed to save model")
            return

        # Test the model with predictions
        print("\n7. Testing model predictions...")

        test_addresses = [
            "Unit 3 45 Collins Street",
            "789 Smith Road",
            "PO Box 123"
        ]

        for address in test_addresses:
            print(f"\n   Input: {address}")
            prediction = ml_model.predict(address)

            if prediction:
                print(f"   Predicted components:")
                print(f"   - Unit: {prediction.get('unit_number', 'N/A')}")
                print(f"   - Street Number: {prediction.get('street_number', 'N/A')}")
                print(f"   - Street Name: {prediction.get('street_name', 'N/A')}")
                print(f"   - Street Type: {prediction.get('street_type', 'N/A')}")
                print(f"   - ML Confidence: {prediction.get('ml_confidence', 0):.2f}")
            else:
                print("   No prediction available")

        # Use the model with clean_addresses
        print("\n8. Using trained model with clean_addresses...")

        sample_data = pd.read_csv('examples/sample_addresses.csv').head(5)

        cleaned_with_ml = clean_addresses(
            sample_data,
            ml_model_path=model_path,
            use_ml=True,
            use_gnaf=False
        )

        print("\n   Results with ML model:")
        output_cols = ['street_number', 'street_name', 'street_type', 'confidence_level']
        print(cleaned_with_ml[output_cols].to_string(index=False))

        print("\n" + "=" * 60)
        print("ML model training completed successfully!")
        print("=" * 60)
        print(f"\nYou can now use the trained model with:")
        print(f"  clean_addresses(df, ml_model_path='{model_path}', use_ml=True)")

    else:
        print("   ✗ Model training failed!")
        print("\nNote: ML features require scikit-learn to be installed:")
        print("  pip install scikit-learn numpy")


if __name__ == '__main__':
    main()

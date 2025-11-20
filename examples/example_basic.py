#!/usr/bin/env python3
"""
Basic example of using the address_cleaner library.

This example demonstrates the simplest usage: loading a CSV,
cleaning addresses with default settings, and saving the results.
"""

import pandas as pd
from address_cleaner import clean_addresses


def main():
    print("=" * 60)
    print("Address Cleaner - Basic Example")
    print("=" * 60)

    # Load sample data
    print("\n1. Loading sample addresses...")
    df = pd.read_csv('examples/sample_addresses.csv')
    print(f"   Loaded {len(df)} addresses")

    # Display sample input
    print("\n2. Sample input (first 3 rows):")
    print(df.head(3).to_string(index=False))

    # Clean addresses
    print("\n3. Cleaning addresses...")
    cleaned_df = clean_addresses(df, use_gnaf=False, use_ml=False)
    print(f"   Cleaned {len(cleaned_df)} addresses")

    # Display sample output
    print("\n4. Sample output (first 3 rows):")
    output_cols = [
        'street_number', 'street_name', 'street_type',
        'suburb', 'state', 'postcode', 'confidence_level'
    ]
    print(cleaned_df[output_cols].head(3).to_string(index=False))

    # Display statistics
    print("\n5. Statistics:")
    print(f"   Average confidence score: {cleaned_df['confidence_level'].mean():.1f}")
    print(f"   Invalid addresses: {cleaned_df['is_invalid_address'].sum()}")
    print(f"   International addresses: {cleaned_df['is_international'].sum()}")

    # Confidence distribution
    print("\n6. Confidence Distribution:")
    bins = [0, 40, 60, 75, 85, 95, 100]
    labels = ['Very Low (0-39)', 'Low (40-59)', 'Moderate (60-74)',
              'High (75-84)', 'Very High (85-94)', 'Excellent (95-100)']
    confidence_dist = pd.cut(cleaned_df['confidence_level'], bins=bins, labels=labels)
    print(confidence_dist.value_counts().sort_index().to_string())

    # Save results
    output_path = 'examples/cleaned_addresses_basic.csv'
    print(f"\n7. Saving results to {output_path}...")
    cleaned_df.to_csv(output_path, index=False)
    print("   Done!")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()

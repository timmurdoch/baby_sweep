#!/usr/bin/env python3
"""
Advanced example of using the address_cleaner library.

This example demonstrates:
- Custom configuration
- Filtering and analysis of results
- Working with confidence scores
- Identifying problematic addresses
"""

import pandas as pd
from address_cleaner import clean_addresses, load_config
import json


def main():
    print("=" * 60)
    print("Address Cleaner - Advanced Example")
    print("=" * 60)

    # Load sample data
    print("\n1. Loading sample addresses...")
    df = pd.read_csv('examples/sample_addresses.csv')
    print(f"   Loaded {len(df)} addresses")

    # Clean addresses
    print("\n2. Cleaning addresses with default settings...")
    cleaned_df = clean_addresses(df, use_gnaf=False, use_ml=False)

    # Analyze results by confidence level
    print("\n3. Analyzing results by confidence level:")

    # High confidence addresses
    high_conf = cleaned_df[cleaned_df['confidence_level'] >= 85]
    print(f"\n   High confidence (≥85): {len(high_conf)} addresses")
    if len(high_conf) > 0:
        print(f"   Average score: {high_conf['confidence_level'].mean():.1f}")

    # Medium confidence addresses
    medium_conf = cleaned_df[
        (cleaned_df['confidence_level'] >= 60) &
        (cleaned_df['confidence_level'] < 85)
    ]
    print(f"\n   Medium confidence (60-84): {len(medium_conf)} addresses")
    if len(medium_conf) > 0:
        print(f"   Average score: {medium_conf['confidence_level'].mean():.1f}")
        print("\n   Sample medium confidence addresses:")
        for idx, row in medium_conf.head(3).iterrows():
            print(f"   - {row['raw_street_address']}, {row['suburb']}")
            print(f"     → {row['street_number']} {row['street_name']} {row['street_type']}")
            print(f"     Confidence: {row['confidence_level']}, Flags: {row['inconsistency_flags']}")

    # Low confidence addresses
    low_conf = cleaned_df[cleaned_df['confidence_level'] < 60]
    print(f"\n   Low confidence (<60): {len(low_conf)} addresses")
    if len(low_conf) > 0:
        print(f"   Average score: {low_conf['confidence_level'].mean():.1f}")

    # Identify addresses with issues
    print("\n4. Addresses requiring review:")

    # Addresses with inconsistencies
    with_issues = cleaned_df[cleaned_df['inconsistency_flags'].str.len() > 0]
    print(f"\n   Addresses with inconsistency flags: {len(with_issues)}")
    if len(with_issues) > 0:
        for idx, row in with_issues.head(5).iterrows():
            print(f"   - ID {row['record_id']}: {row['raw_street_address']}")
            print(f"     Flags: {row['inconsistency_flags']}")

    # Invalid addresses
    invalid = cleaned_df[cleaned_df['is_invalid_address'] == True]
    print(f"\n   Invalid addresses: {len(invalid)}")
    if len(invalid) > 0:
        for idx, row in invalid.head(3).iterrows():
            print(f"   - ID {row['record_id']}: {row['raw_street_address']}")

    # International addresses
    international = cleaned_df[cleaned_df['is_international'] == True]
    print(f"\n   International addresses: {len(international)}")

    # Special address types
    print("\n5. Special address types:")

    po_boxes = cleaned_df[cleaned_df['street_type'].str.contains('PO Box', na=False)]
    print(f"   PO Boxes: {len(po_boxes)}")

    rmb_addresses = cleaned_df[cleaned_df['street_type'].str.contains('RMB', na=False)]
    print(f"   RMB addresses: {len(rmb_addresses)}")

    unit_addresses = cleaned_df[cleaned_df['unit_number'].str.len() > 0]
    print(f"   Addresses with units: {len(unit_addresses)}")

    # Export different quality segments
    print("\n6. Exporting segmented results...")

    high_conf.to_csv('examples/cleaned_high_confidence.csv', index=False)
    print(f"   High confidence: examples/cleaned_high_confidence.csv")

    if len(medium_conf) > 0:
        medium_conf.to_csv('examples/cleaned_medium_confidence.csv', index=False)
        print(f"   Medium confidence: examples/cleaned_medium_confidence.csv")

    if len(low_conf) > 0:
        low_conf.to_csv('examples/cleaned_low_confidence.csv', index=False)
        print(f"   Low confidence: examples/cleaned_low_confidence.csv")

    # Create a summary report
    print("\n7. Creating summary report...")

    summary = {
        'total_addresses': len(cleaned_df),
        'average_confidence': float(cleaned_df['confidence_level'].mean()),
        'confidence_distribution': {
            'excellent_95_100': int((cleaned_df['confidence_level'] >= 95).sum()),
            'very_high_85_94': int(
                ((cleaned_df['confidence_level'] >= 85) &
                 (cleaned_df['confidence_level'] < 95)).sum()
            ),
            'high_75_84': int(
                ((cleaned_df['confidence_level'] >= 75) &
                 (cleaned_df['confidence_level'] < 85)).sum()
            ),
            'moderate_60_74': int(
                ((cleaned_df['confidence_level'] >= 60) &
                 (cleaned_df['confidence_level'] < 75)).sum()
            ),
            'low_40_59': int(
                ((cleaned_df['confidence_level'] >= 40) &
                 (cleaned_df['confidence_level'] < 60)).sum()
            ),
            'very_low_0_39': int((cleaned_df['confidence_level'] < 40).sum()),
        },
        'special_types': {
            'po_boxes': int(len(po_boxes)),
            'rmb_addresses': int(len(rmb_addresses)),
            'unit_addresses': int(len(unit_addresses)),
        },
        'quality_flags': {
            'invalid_addresses': int(invalid.shape[0]),
            'international_addresses': int(international.shape[0]),
            'addresses_with_issues': int(len(with_issues)),
        }
    }

    # Save summary as JSON
    with open('examples/cleaning_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("   Summary saved to: examples/cleaning_summary.json")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2))

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()

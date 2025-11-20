# Address Cleaner - Australian Address Cleaning and Normalization

A comprehensive Python library for cleaning, parsing, and normalizing Australian addresses. Combines rule-based parsing, machine learning predictions, and G-NAF database validation to provide high-quality address standardization.

## Features

- **Flexible Schema Mapping**: Support multiple input CSV schemas with configurable column mappings
- **Rule-Based Parsing**: Comprehensive rules for Australian address formats including:
  - Unit/apartment numbers
  - Street numbers (including ranges like "10-12")
  - Street names and types
  - PO Boxes and rural addresses (RMB)
  - Suburb, state, and postcode normalization
- **Machine Learning**: Optional ML model for intelligent address component prediction
- **G-NAF Integration**: Validate and correct addresses against the Geocoded National Address File
- **Confidence Scoring**: Sophisticated scoring system (0-100) indicating address quality
- **International Detection**: Automatically identify and flag non-Australian addresses
- **Batch Processing**: Efficiently process thousands of addresses
- **CLI and Library**: Use as a command-line tool or import as a Python library

## Installation

### Basic Installation

```bash
pip install -e .
```

### With Optional Features

```bash
# Install with G-NAF support
pip install -e ".[gnaf]"

# Install with ML support
pip install -e ".[ml]"

# Install all features
pip install -e ".[all]"

# Install for development
pip install -e ".[dev]"
```

### Manual Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# For G-NAF features
pip install sqlalchemy psycopg2-binary

# For ML features
pip install scikit-learn numpy
```

## Quick Start

### Command-Line Usage

```bash
# Basic usage
python -m address_cleaner --input addresses.csv --output cleaned.csv

# With custom configuration
python -m address_cleaner \
  --input addresses.csv \
  --output cleaned.csv \
  --config my_config.yaml

# With G-NAF validation
python -m address_cleaner \
  --input addresses.csv \
  --output cleaned.csv \
  --gnaf-url postgresql://user:pass@localhost:5432/gnaf

# Disable G-NAF or ML
python -m address_cleaner \
  --input addresses.csv \
  --output cleaned.csv \
  --no-gnaf --no-ml
```

### Python Library Usage

```python
from address_cleaner import clean_addresses
import pandas as pd

# Load your data
df = pd.read_csv('addresses.csv')

# Clean addresses (basic)
cleaned_df = clean_addresses(df)

# Clean with G-NAF validation
cleaned_df = clean_addresses(
    df,
    gnaf_connection_url="postgresql://user:pass@localhost:5432/gnaf"
)

# Clean with custom schema
cleaned_df = clean_addresses(
    df,
    schema_name='vendor_x',
    config_path='config/custom_config.yaml'
)

# Save results
cleaned_df.to_csv('cleaned_addresses.csv', index=False)
```

## Input Format

### Expected Columns (Default Schema)

Your input CSV should contain these columns:

- `street_address`: Street address (e.g., "Unit 5 123 Main Street")
- `suburb`: Suburb/locality name (e.g., "Richmond")
- `state`: State abbreviation (e.g., "VIC")
- `postcode`: 4-digit postcode (e.g., "3121")
- `id` (optional): Unique identifier for each record

### Example Input

```csv
id,street_address,suburb,state,postcode
1,"Unit 5 123 Main Street","Richmond","VIC","3121"
2,"PO Box 456","Melbourne","VIC","3000"
3,"10-12 Smith Rd","Fitzroy","VIC","3065"
```

## Output Format

The cleaned DataFrame includes all original columns plus:

### Standardized Address Components

- `unit_number`: Unit/apartment number (e.g., "5")
- `street_number`: Street number (e.g., "123")
- `street_name`: Normalized street name (e.g., "Main")
- `street_type`: Expanded street type (e.g., "Street")
- `suburb`: Corrected suburb (e.g., "Richmond")
- `state`: Corrected state (e.g., "VIC")
- `postcode`: Validated postcode (e.g., "3121")

### Metadata Fields

- `confidence_level`: Score 0-100 indicating parsing quality
- `is_international`: Boolean, true if address appears non-Australian
- `is_invalid_address`: Boolean, true if address is unusable
- `inconsistency_flags`: Comma-separated list of detected issues
- `unparsed_components`: Any text that couldn't be parsed

### Raw Input Preservation

- `raw_street_address`: Original street address
- `raw_suburb`: Original suburb
- `raw_state`: Original state
- `raw_postcode`: Original postcode

### Example Output

```csv
record_id,unit_number,street_number,street_name,street_type,suburb,state,postcode,confidence_level,is_international,is_invalid_address,inconsistency_flags,unparsed_components
1,5,123,Main,Street,Richmond,VIC,3121,95,false,false,,,
2,,456,,,Melbourne,VIC,3000,88,false,false,"PO_BOX",,
3,,10,Smith,Road,Fitzroy,VIC,3065,92,false,false,,,
```

## Configuration

### Using Custom Schemas

If your CSV uses different column names, configure a custom schema in YAML:

```yaml
schemas:
  my_schema:
    id_column: "RecordID"
    street_address: "AddressLine1"
    suburb: "City"
    state: "StateCode"
    postcode: "PostCode"
```

Then use it:

```python
cleaned_df = clean_addresses(df, schema_name='my_schema')
```

### Street Type Normalization

The default configuration includes common Australian street types and abbreviations:

- Street, Road, Avenue, Drive, Crescent, Court, Place, etc.
- Handles misspellings: "cresent" → "Crescent", "drove" → "Drive"
- Fuzzy matching for variations

### State Normalization

Recognizes all Australian states and territories:

- NSW, VIC, QLD, SA, WA, TAS, ACT, NT
- Handles full names: "New South Wales" → "NSW"
- Handles variations: "N.S.W." → "NSW"

### Postcode Validation

- Validates 4-digit format
- Checks postcode/state consistency
- Known ranges for each state

## Special Address Types

### PO Boxes

Automatically detected and parsed:

```
Input:  "PO Box 123, Melbourne VIC 3000"
Output: street_type="PO Box", street_number="123"
```

### Rural Addresses (RMB)

Roadside Mail Bags are properly handled:

```
Input:  "RMB 456, Bendigo VIC 3550"
Output: street_type="RMB", street_number="456"
```

### Unit Numbers

Recognizes multiple formats:

- "Unit 5 123 Main St" → unit=5, street=123
- "5/123 Main St" → unit=5, street=123
- "U5 123 Main St" → unit=5, street=123
- "Suite 5 123 Main St" → unit=5, street=123

### Street Number Ranges

Extracts the lowest number:

- "10-12 Smith Rd" → street_number="10"
- "10–12 Smith Rd" → street_number="10" (handles various dashes)

## Confidence Scoring

Confidence scores range from 0 to 100:

| Score Range | Category | Description |
|-------------|----------|-------------|
| 95-100 | Excellent | Clean parse, exact G-NAF match, no corrections needed |
| 85-94 | Very High | Minor fuzzy matching or approximate G-NAF match |
| 75-84 | High | Some corrections applied, good overall quality |
| 60-74 | Moderate | Multiple corrections or inconsistencies detected |
| 40-59 | Low | Significant parsing issues or missing components |
| 0-39 | Very Low | Invalid or unparseable address |

### Factors Affecting Score

**Positive factors:**
- Clear component separation
- Exact G-NAF match
- No fuzzy matching needed

**Negative factors:**
- Fuzzy matching required
- Corrections applied to suburb/state/postcode
- G-NAF approximate match or no match
- Unparsed components remain
- Missing essential fields
- Detected as international or invalid

## G-NAF Integration

### Setup

1. Install PostgreSQL dependencies:
   ```bash
   pip install sqlalchemy psycopg2-binary
   ```

2. Ensure G-NAF database is accessible

3. Configure connection:
   ```python
   cleaned_df = clean_addresses(
       df,
       gnaf_connection_url="postgresql://user:pass@host:5432/gnaf"
   )
   ```

### What G-NAF Does

- **Validates** parsed addresses against official records
- **Corrects** obvious mistakes (e.g., wrong postcode for suburb)
- **Boosts confidence** for exact matches
- **Flags** approximate or no matches

### G-NAF Flags

- `GNAF_EXACT_MATCH`: Address found exactly in G-NAF
- `GNAF_APPROXIMATE_MATCH`: Close match found (fuzzy)
- `NO_GNAF_MATCH`: No match found in database
- `GNAF_DISABLED`: G-NAF validation not used

## Machine Learning Model

### Training a Model

```python
from address_cleaner import AddressMLModel
import pandas as pd

# Load training data
training_data = pd.read_csv('training_data.csv')

# Expected columns:
# - raw_street_address
# - clean_unit_number
# - clean_street_number
# - clean_street_name
# - clean_street_type
# - clean_suburb
# - clean_state
# - clean_postcode

# Initialize and train
model = AddressMLModel(config)
model.train(training_data)

# Save model
model.save_model('models/address_parser_model.pkl')
```

### Using a Trained Model

```python
cleaned_df = clean_addresses(
    df,
    ml_model_path='models/address_parser_model.pkl',
    use_ml=True
)
```

### ML Behavior

- **High confidence predictions** (>70%) are used directly
- **Low confidence predictions** fall back to rule-based parsing
- ML confidence contributes to overall confidence score

## Advanced Usage

### Custom Configuration File

Create `my_config.yaml`:

```yaml
parsing:
  unit_prefixes:
    - "UNIT"
    - "APT"
    - "SUITE"

street_types:
  canonical:
    STREET:
      label: "Street"
      aliases: ["ST", "ST.", "STR"]

scoring:
  base_score: 100
  penalties:
    fuzzy_street_type: 5
    no_gnaf_match: 15
```

Use it:

```python
cleaned_df = clean_addresses(df, config_path='my_config.yaml')
```

### Batch Processing Large Files

For very large datasets:

```python
import pandas as pd
from address_cleaner import clean_addresses

# Process in chunks
chunk_size = 10000
output_file = 'cleaned_addresses.csv'

for i, chunk in enumerate(pd.read_csv('large_file.csv', chunksize=chunk_size)):
    cleaned_chunk = clean_addresses(chunk)

    # Write header only on first chunk
    mode = 'w' if i == 0 else 'a'
    header = i == 0

    cleaned_chunk.to_csv(output_file, mode=mode, header=header, index=False)
```

### Filtering Results

```python
# Get only high-confidence addresses
high_quality = cleaned_df[cleaned_df['confidence_level'] >= 85]

# Get addresses that needed correction
corrected = cleaned_df[cleaned_df['inconsistency_flags'].str.len() > 0]

# Get invalid addresses for manual review
invalid = cleaned_df[cleaned_df['is_invalid_address'] == True]

# Get international addresses
international = cleaned_df[cleaned_df['is_international'] == True]
```

## API Reference

### `clean_addresses()`

Main function for cleaning addresses.

**Parameters:**
- `df` (DataFrame): Input DataFrame with address columns
- `config_path` (str, optional): Path to YAML config file
- `config` (dict, optional): Configuration dictionary (overrides config_path)
- `schema_name` (str): Schema name for column mapping (default: 'default')
- `gnaf_connection_url` (str, optional): G-NAF database connection URL
- `ml_model_path` (str, optional): Path to ML model file
- `use_ml` (bool): Whether to use ML predictions (default: True)
- `use_gnaf` (bool): Whether to use G-NAF validation (default: True)

**Returns:**
- DataFrame with cleaned addresses and metadata

### `clean_csv()`

Clean addresses from CSV file.

**Parameters:**
- `input_path` (str): Input CSV file path
- `output_path` (str): Output CSV file path
- `config_path` (str, optional): Path to config file
- `schema_name` (str): Schema name (default: 'default')
- `gnaf_connection_url` (str, optional): G-NAF connection URL
- `**kwargs`: Additional arguments for clean_addresses()

**Returns:**
- Cleaned DataFrame

## Examples

### Example 1: Basic Cleaning

```python
from address_cleaner import clean_addresses
import pandas as pd

# Create sample data
data = {
    'street_address': ['123 Main St', 'PO Box 456', '10-12 Smith Rd'],
    'suburb': ['Richmond', 'Melbourne', 'Fitzroy'],
    'state': ['VIC', 'VIC', 'VIC'],
    'postcode': ['3121', '3000', '3065']
}

df = pd.DataFrame(data)

# Clean addresses
cleaned = clean_addresses(df)

# Inspect results
print(cleaned[['street_number', 'street_name', 'street_type', 'confidence_level']])
```

### Example 2: With G-NAF Validation

```python
cleaned = clean_addresses(
    df,
    gnaf_connection_url="postgresql://user:pass@localhost:5432/gnaf"
)

# Check G-NAF flags
print(cleaned[['street_name', 'suburb', 'inconsistency_flags']])
```

### Example 3: Custom Schema

```python
# Your data has different column names
custom_data = pd.read_csv('vendor_data.csv')
# Columns: AddressLine1, City, StateCode, PostCode

cleaned = clean_addresses(
    custom_data,
    schema_name='vendor_x'  # Defined in config
)
```

## Troubleshooting

### Common Issues

**Issue: "Schema 'xyz' not found"**
- Check your config file has the schema defined
- Verify schema_name parameter matches config

**Issue: Low confidence scores**
- Check if G-NAF is enabled and accessible
- Verify input addresses are reasonably formatted
- Review inconsistency_flags for specific issues

**Issue: G-NAF connection errors**
- Verify database connection URL format
- Check network connectivity to database
- Ensure G-NAF tables exist and are accessible

**Issue: ML model not loading**
- Check model file path exists
- Ensure scikit-learn is installed
- Verify model was trained with compatible library versions

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

cleaned = clean_addresses(df)
```

Or from CLI:

```bash
python -m address_cleaner --input data.csv --output clean.csv --verbose
```

## Performance

### Benchmarks

Approximate processing times (without G-NAF):

- 1,000 addresses: ~2 seconds
- 10,000 addresses: ~15 seconds
- 100,000 addresses: ~2.5 minutes

With G-NAF validation, times increase depending on database performance and network latency.

### Optimization Tips

1. **Disable unused features:**
   ```python
   cleaned = clean_addresses(df, use_ml=False, use_gnaf=False)
   ```

2. **Process in batches** for large files (see Advanced Usage)

3. **Index G-NAF database** on street_name, suburb, and postcode fields

4. **Use local G-NAF database** to minimize network latency

## License

MIT License

## Contributing

Contributions are welcome! Please submit issues and pull requests to the GitHub repository.

## Support

For questions, issues, or feature requests, please use the GitHub Issues tracker.

## Changelog

### Version 1.0.0 (Initial Release)
- Rule-based address parsing
- ML model infrastructure
- G-NAF database integration
- Confidence scoring system
- CLI and library interfaces
- Support for PO Boxes and rural addresses
- International address detection
- Comprehensive configuration system

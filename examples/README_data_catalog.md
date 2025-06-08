# Data Catalog Tool Example

This example demonstrates how to use the data catalog tool with Strands agents to search and retrieve metadata about available data products.

## What's Included

- **`data_catalog_example.py`**: Complete example showing both agent-based and direct tool usage
- Two sample data products:
  - Swiss Power Plants Registry
  - Swiss Population by Location and Year

## Features Demonstrated

1. **Agent Integration**: How to create a Strands agent with data catalog tools
2. **Interactive Queries**: Natural language questions about data products
3. **Direct Tool Usage**: Using the tools programmatically without an agent
4. **Search Functionality**: Finding data products by keywords
5. **Metadata Retrieval**: Getting detailed information about datasets

## Running the Example

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install strands-sdk
```

And ensure your environment variables are set up (in `config/.env`):

```
BEDROCK_MODEL='us.anthropic.claude-sonnet-4-20250514-v1:0'
AWS_REGION='us-east-1'
# or other model provider credentials
```

### Run the Example

```bash
cd /Users/patrickrotzetter/Library/CloudStorage/OneDrive-Personal/Documents/dev/multi-agents
python examples/data_catalog_example.py
```

### Example Interactions

The example will show you how to:

1. **List all available data products**
   ```
   "What data products do we have available?"
   ```

2. **Search for specific datasets**
   ```
   "Search for any data products related to energy"
   ```

3. **Get detailed information**
   ```
   "Tell me about the Swiss power plants dataset"
   "What attributes are available in the population data?"
   ```

4. **Find storage locations**
   ```
   "Where is the power plants data stored and in what format?"
   ```

## Sample Output

```
Query 1: What data products do we have available?
--------------------------------------------------
Response: I found 2 data products in our catalog:

1. **Swiss Power Plants Registry** (swiss_power_plants)
   - Format: parquet
   - Records: 2,847
   - Last updated: 2024-12-01

2. **Swiss Population by Location and Year** (swiss_population)
   - Format: csv  
   - Records: 156,789
   - Last updated: 2024-11-15

Both datasets contain comprehensive information about Switzerland's energy infrastructure and demographics respectively.
```

## Tool Functions

The example uses these data catalog tools:

- `search_data_catalog()` - Search or get specific data products
- `get_data_product_attributes()` - Get detailed attribute lists
- `list_data_products()` - Get summary of all products
- `get_data_product_location()` - Get storage and access information

## Extending the Example

You can easily extend this example by:

1. Adding more data products to the catalog
2. Creating specialized agents for different domains
3. Integrating with real data storage systems
4. Adding data quality and lineage information

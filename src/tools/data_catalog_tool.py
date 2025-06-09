"""
Data Catalog Tool for Strands Agents

This tool provides access to a dictionary of data product metadata,
providing information about available data products including their
attributes, location, format, and descriptions.

Updated to match actual CSV files in the docs folder.
"""

from typing import Dict, List, Optional, Any
from strands import tool


# Data catalog with metadata for data products based on actual CSV files in docs folder
DATA_CATALOG = {
    "swiss_power_plants": {
        "name": "Swiss Renewable Power Plants Registry",
        "description": "Comprehensive list of renewable power generation facilities in Switzerland, including detailed information about capacity, location, technology, and operational details",
        "attributes": [
            "electrical_capacity",
            "energy_source_level_1",
            "energy_source_level_2", 
            "energy_source_level_3",
            "technology",
            "data_source",
            "nuts_1_region",
            "nuts_2_region",
            "nuts_3_region",
            "lon",
            "lat",
            "municipality",
            "municipality_code",
            "postcode",
            "address",
            "canton",
            "commissioning_date",
            "contract_period_end",
            "company",
            "tariff",
            "project_name",
            "production"
        ],
        "location": "docs/renewable_power_plants_CH_filtered.csv",
        "format": "csv",
        "last_updated": "2024-06-07",
        "record_count": 12718,  # 12719 - 1 header row
        "data_owner": "Swiss Federal Office of Energy (BFE)",
        "update_frequency": "periodic"
    },
    "swiss_population": {
        "name": "Swiss Population Historical Data by Administrative Division",
        "description": "Historical population statistics for Switzerland from 1850 onwards, organized by administrative divisions (communes, districts, cantons) with detailed demographic breakdowns",
        "attributes": [
            "Année",  # Year
            "No_commune",  # Municipality number
            "Nom_commune",  # Municipality name
            "No_district",  # District number
            "Nom_district",  # District name
            "No_canton",  # Canton number
            "Canton",  # Canton code
            "Nom_canton",  # Canton name
            "Numéro_historisation",  # Historization number
            "Unité",  # Unit/Category
            "Nombre",  # Count/Number
            "OBS_STATUS"  # Observation status
        ],
        "location": "docs/su-f-01.01-vz1850-ge-01.csv",
        "format": "csv",
        "last_updated": "2024-06-08",
        "record_count": 1297502,  # 1297503 - 1 header row
        "data_owner": "Swiss Federal Statistical Office (FSO)",
        "update_frequency": "annual"
    }
}


@tool
def search_data_catalog(query: Optional[str] = None, data_product_id: Optional[str] = None) -> Dict[str, Any]:
    """Search the data catalog for available data products.
    
    Args:
        query: Optional search term to filter data products by name or description
        data_product_id: Optional specific data product ID to retrieve detailed metadata
        
    Returns:
        Dictionary containing matching data products and their metadata
    """
    
    if data_product_id:
        # Return specific data product if it exists
        if data_product_id in DATA_CATALOG:
            return {
                "status": "success",
                "data_product_id": data_product_id,
                "metadata": DATA_CATALOG[data_product_id],
                "message": f"Retrieved metadata for data product: {data_product_id}"
            }
        else:
            return {
                "status": "error",
                "message": f"Data product '{data_product_id}' not found in catalog",
                "available_products": list(DATA_CATALOG.keys())
            }
    
    # Search functionality
    if query:
        query_lower = query.lower()
        matching_products = {}
        
        for product_id, metadata in DATA_CATALOG.items():
            # Search in name and description
            if (query_lower in metadata["name"].lower() or 
                query_lower in metadata["description"].lower() or
                query_lower in product_id.lower()):
                matching_products[product_id] = metadata
        
        return {
            "status": "success",
            "query": query,
            "matching_products": matching_products,
            "total_matches": len(matching_products),
            "message": f"Found {len(matching_products)} data products matching '{query}'"
        }
    
    # Return all products if no specific query
    return {
        "status": "success",
        "all_products": DATA_CATALOG,
        "total_products": len(DATA_CATALOG),
        "message": "Retrieved all available data products from catalog"
    }


@tool
def get_data_product_attributes(data_product_id: str) -> Dict[str, Any]:
    """Get detailed attribute information for a specific data product.
    
    Args:
        data_product_id: The ID of the data product to get attributes for
        
    Returns:
        Dictionary containing detailed attribute information
    """
    
    if data_product_id not in DATA_CATALOG:
        return {
            "status": "error",
            "message": f"Data product '{data_product_id}' not found in catalog",
            "available_products": list(DATA_CATALOG.keys())
        }
    
    metadata = DATA_CATALOG[data_product_id]
    
    return {
        "status": "success",
        "data_product_id": data_product_id,
        "data_product_name": metadata["name"],
        "attributes": metadata["attributes"],
        "attribute_count": len(metadata["attributes"]),
        "format": metadata["format"],
        "location": metadata["location"],
        "message": f"Retrieved {len(metadata['attributes'])} attributes for {metadata['name']}"
    }


@tool
def list_data_products() -> Dict[str, Any]:
    """List all available data products in the catalog with basic information.
    
    Returns:
        Dictionary containing summary of all data products
    """
    
    products_summary = {}
    
    for product_id, metadata in DATA_CATALOG.items():
        products_summary[product_id] = {
            "name": metadata["name"],
            "description": metadata["description"][:100] + "..." if len(metadata["description"]) > 100 else metadata["description"],
            "format": metadata["format"],
            "record_count": metadata["record_count"],
            "last_updated": metadata["last_updated"]
        }
    
    return {
        "status": "success",
        "products": products_summary,
        "total_products": len(products_summary),
        "message": f"Listed {len(products_summary)} available data products"
    }


@tool
def get_data_product_location(data_product_id: str) -> Dict[str, Any]:
    """Get the storage location and access information for a data product.
    
    Args:
        data_product_id: The ID of the data product to get location for
        
    Returns:
        Dictionary containing location and access information
    """
    
    if data_product_id not in DATA_CATALOG:
        return {
            "status": "error",
            "message": f"Data product '{data_product_id}' not found in catalog",
            "available_products": list(DATA_CATALOG.keys())
        }
    
    metadata = DATA_CATALOG[data_product_id]
    
    return {
        "status": "success",
        "data_product_id": data_product_id,
        "data_product_name": metadata["name"],
        "location": metadata["location"],
        "format": metadata["format"],
        "data_owner": metadata["data_owner"],
        "last_updated": metadata["last_updated"],
        "update_frequency": metadata["update_frequency"],
        "record_count": metadata["record_count"],
        "message": f"Retrieved location information for {metadata['name']}"
    }

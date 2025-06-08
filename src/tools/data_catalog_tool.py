"""
Data Catalog Tool for Strands Agents

This tool simulates access to a dictionary of data product metadata,
providing information about available data products including their
attributes, location, format, and descriptions.
"""

from typing import Dict, List, Optional, Any
from strands import tool


# Simulated data catalog with metadata for data products
DATA_CATALOG = {
    "swiss_power_plants": {
        "name": "Swiss Power Plants Registry",
        "description": "Comprehensive list of all power generation facilities in Switzerland, including renewable and conventional energy sources",
        "attributes": [
            "plant_id",
            "plant_name", 
            "operator",
            "location_canton",
            "location_municipality",
            "coordinates_lat",
            "coordinates_lon",
            "energy_source",
            "technology_type",
            "capacity_mw",
            "commissioning_year",
            "status",
            "grid_connection_level"
        ],
        "location": "s3://swiss-energy-data/power-plants/",
        "format": "parquet",
        "last_updated": "2024-12-01",
        "record_count": 2847,
        "data_owner": "Swiss Federal Office of Energy (SFOE)",
        "update_frequency": "monthly"
    },
    "swiss_population": {
        "name": "Swiss Population by Location and Year",
        "description": "Historical and current population statistics for Switzerland by administrative divisions (cantons, districts, municipalities) with yearly granularity",
        "attributes": [
            "year",
            "canton_code",
            "canton_name",
            "district_code", 
            "district_name",
            "municipality_code",
            "municipality_name",
            "population_total",
            "population_male",
            "population_female",
            "population_swiss",
            "population_foreign",
            "age_group_0_19",
            "age_group_20_64",
            "age_group_65_plus",
            "area_km2",
            "population_density"
        ],
        "location": "s3://swiss-demographics/population/",
        "format": "csv",
        "last_updated": "2024-11-15",
        "record_count": 156789,
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

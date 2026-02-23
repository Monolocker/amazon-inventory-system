# Amazon Inventory System

A lightweight inventory management tool for small-scale Amazon wholesalers to track physical products within their workspace

## What It Does 
* Retrieves ASIN upon scanning barcode or manual input
* Stores ASIN-to-location mapping in a dictionary
* Enter ASIN → System returns location 

## Why It Exists
* Small-scale Amazon wholesalers often lack access to affordable inventory tooling. This free and simple solution narrows the gap on the core problem of quickly finding products in physical storage. 

## How To Use It 
* Scan (or manually input) ASIN with program open
* Manually input alphanumeric shelving (e.g., A2, B5) where item with correlated ASIN is located 
* Copy and paste ASIN from fulfillment upon order arrival to locate item

## Requirements

### Software 
- Python 3.6 or higher
- No external libraries required (uses built-in 'csv' module)

### Hardware 
- Barcode scanner (optional but strongly recommended)

### Knowledge 
- Basic command line/terminal usage 
- Basic python knowledge

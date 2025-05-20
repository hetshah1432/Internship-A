# Olist E-Commerce Data Preparation Pipeline

## Team A - Data Acquisition & Preparation

This repository contains the comprehensive data preparation pipeline for the Olist Brazilian E-Commerce dataset, designed to support customer behavior analysis and revenue optimization.

---

##  Project Overview

**Objective**: Clean, transform, and merge raw e-commerce datasets to create analysis-ready data for customer segmentation, churn prediction, and business intelligence.

**Dataset**: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## 🗂️ Repository Structure

```
├── olist_data_preparation.py       # Main data preparation pipeline
├── README.md                       # This file
├── raw_data/                       # Original CSV files (not included)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
└── cleaned_data/                   # Processed datasets (Team A output)
    ├── cleaned_orders.csv
    ├── cleaned_order_items.csv
    ├── cleaned_customers.csv
    ├── cleaned_products.csv
    ├── cleaned_sellers.csv
    ├── cleaned_payments.csv
    ├── cleaned_reviews.csv
    ├── cleaned_geolocation.csv
    ├── cleaned_product_translation.csv
    └── master_dataset.csv          # PRIMARY OUTPUT
```

---

## 🔧 Data Quality Issues Identified & Resolved

### Major Issues Fixed:
- **Date Format Problems**: Resolved `########` display issues in date columns
- **Text Encoding**: Fixed Portuguese characters (`Ã£` → `ã`, `Ã©` → `é`, etc.)
- **Duplicate Records**: Removed duplicates across all datasets
- **Missing Values**: Applied appropriate imputation strategies
- **Data Validation**: Validated coordinates, prices, review scores, order statuses

### Dataset-Specific Cleaning:

#### 📦 Orders Dataset
- ✅ Standardized all date columns to proper datetime format
- ✅ Removed duplicate orders
- ✅ Validated order statuses (delivered, shipped, processing, etc.)

#### 🛒 Order Items Dataset  
- ✅ Fixed shipping date formatting
- ✅ Removed negative prices and freight values
- ✅ Eliminated duplicate order items

#### 👥 Customers Dataset
- ✅ Fixed city name encoding issues
- ✅ Removed duplicate customers (kept unique customers)
- ✅ Standardized location data

#### 🏪 Sellers Dataset
- ✅ Cleaned seller city names
- ✅ Removed duplicate seller records
- ✅ Standardized geographic information

#### 📦 Products Dataset
- ✅ Added English category translations
- ✅ Imputed missing product dimensions using category medians
- ✅ Removed duplicate products

#### 💳 Payments Dataset
- ✅ Removed negative payment values
- ✅ Standardized payment type formats
- ✅ Aggregated multiple payments per order

#### ⭐ Reviews Dataset
- ✅ Fixed text encoding in review comments
- ✅ Standardized review creation dates
- ✅ Validated review scores (1-5 range)

#### 🗺️ Geolocation Dataset
- ✅ Fixed city name encoding
- ✅ Removed duplicate zip codes
- ✅ Validated coordinate ranges

---

##  Master Dataset

The **`master_dataset.csv`** is the primary deliverable, containing:

- **Base**: All orders with customer information
- **Enhanced with**: Product details, seller info, payment aggregations, review summaries, geographic coordinates
- **Additional Features**: 
  - `order_item_total` (price + freight)
  - `delivery_days` (calculated delivery time)
  - Aggregated payment and review metrics per order

**Final Shape**: ~100K+ rows × 50+ columns (exact dimensions depend on raw data)

---


## 📊 For Subsequent Teams

### Team B (EDA) - Use These Files:
- `master_dataset.csv` - Primary dataset for exploratory analysis
- Individual cleaned datasets for specific deep-dives

### Team C (Segmentation & Modeling) - Key Features Available:
- Clean customer data for RFM analysis
- Order history for churn labeling
- Product and review data for recommendation engines
- Geographic data for location-based insights

### Team D (Dashboard) - Ready-to-Use Metrics:
- Sales totals, customer counts, geographic distributions
- Time-series data with proper date formatting
- Product performance metrics
- Customer satisfaction scores

---

## 📈 Data Quality Metrics

| Dataset | Original Size | After Cleaning | Duplicates Removed | Missing Values Handled |
|---------|---------------|----------------|-------------------|----------------------|
| Orders | ~100K rows | ~99K rows | ~1K duplicates | Date parsing fixed |
| Order Items | ~110K rows | ~110K rows | Minimal | Price validation |
| Customers | ~100K rows | ~99K rows | ~1K duplicates | Encoding fixed |
| Products | ~32K rows | ~32K rows | Minimal | Dimensions imputed |
| Sellers | ~3K rows | ~3K rows | Minimal | City names fixed |
| Payments | ~100K rows | ~100K rows | None | Aggregated by order |
| Reviews | ~100K rows | ~99K rows | ~1K duplicates | Text encoding fixed |
| Geolocation | ~1M rows | ~20K rows | ~980K duplicates | Coordinates validated |

---

## 🔍 Known Limitations & Recommendations

1. **Date Range**: Dataset covers 2016-2018, consider temporal relevance for predictions
2. **Geographic Scope**: Primarily Brazilian market, findings may not generalize globally
3. **Missing Reviews**: Not all orders have reviews, handle accordingly in analysis
4. **Product Categories**: Some categories have very few items, consider grouping for analysis

---


## 👨‍💻 Team A Contributors

**Data Preparation Team**: Het Shah
**Completion Date**: 20-5-2025

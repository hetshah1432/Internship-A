import pandas as pd
import numpy as np
import warnings
from datetime import datetime
import re
import unicodedata
warnings.filterwarnings('ignore')

class OlistDataPreparation:
    """
    Comprehensive data preparation pipeline for Olist E-commerce dataset
    Team A - Data Acquisition & Preparation
    """
    
    def __init__(self):
        self.datasets = {}
        self.master_dataset = None
        self.data_quality_report = {}
        
    def load_datasets(self, file_paths):
        """
        Load all CSV files from the Olist dataset
        
        Parameters:
        file_paths (dict): Dictionary with dataset names as keys and file paths as values
        Example: {
            'orders': 'olist_orders_dataset.csv',
            'order_items': 'olist_order_items_dataset.csv',
            'customers': 'olist_customers_dataset.csv',
            'products': 'olist_products_dataset.csv',
            'sellers': 'olist_sellers_dataset.csv',
            'payments': 'olist_order_payments_dataset.csv',
            'reviews': 'olist_order_reviews_dataset.csv',
            'geolocation': 'olist_geolocation_dataset.csv',
            'product_translation': 'product_category_name_translation.csv'
        }
        """
        print("=== LOADING DATASETS ===")
        
        for name, path in file_paths.items():
            try:
                self.datasets[name] = pd.read_csv(path)
                print(f"Loaded {name}: {self.datasets[name].shape}")
            except Exception as e:
                print(f"Error loading {name}: {e}")
    
    def assess_data_quality(self):
        """Generate initial data quality assessment"""
        print("\n=== DATA QUALITY ASSESSMENT ===")
        
        for name, df in self.datasets.items():
            missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
            duplicates = df.duplicated().sum()
            
            self.data_quality_report[name] = {
                'shape': df.shape,
                'missing_values': missing_pct[missing_pct > 0].to_dict(),
                'duplicates': duplicates,
                'dtypes': df.dtypes.to_dict()
            }
            
            print(f"\n{name.upper()}:")
            print(f"  Shape: {df.shape}")
            print(f"  Duplicates: {duplicates}")
            if missing_pct[missing_pct > 0].any():
                print(f"  Missing values: {dict(missing_pct[missing_pct > 0])}")
    
    def clean_text_encoding(self, text):
        """Fix encoding issues in text fields"""
        if pd.isna(text):
            return text
        
        # Common Portuguese character fixes
        replacements = {
            'Ã£': 'ã',
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã§': 'ç',
            'Ã': 'à',
            'Ã¢': 'â',
            'Ãª': 'ê',
            'Ã´': 'ô',
            'Ã¼': 'ü'
        }
        
        text_str = str(text)
        for old, new in replacements.items():
            text_str = text_str.replace(old, new)
        
        return text_str
    
    def standardize_dates(self, df, date_columns):
        """Convert date columns to proper datetime format"""
        for col in date_columns:
            if col in df.columns:
                # Handle the ######## issue (likely Excel display problem)
                df[col] = df[col].astype(str)
                df[col] = df[col].replace(['########', 'nan', 'NaN'], pd.NaT)
                
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    print(f"Warning: Could not parse dates in {col}")
        
        return df
    
    def clean_geolocation(self):
        """Clean geolocation dataset"""
        print("\n=== CLEANING GEOLOCATION ===")
        
        if 'geolocation' not in self.datasets:
            return
        
        geo = self.datasets['geolocation'].copy()
        
        # Clean city names with encoding issues
        geo['geolocation_city'] = geo['geolocation_city'].apply(self.clean_text_encoding)
        
        # Remove duplicates - keep first occurrence
        before_dedup = len(geo)
        geo = geo.drop_duplicates(subset=['geolocation_zip_code_prefix'], keep='first')
        after_dedup = len(geo)
        
        print(f"Removed {before_dedup - after_dedup} duplicate zip codes")
        
        # Validate coordinates
        geo = geo[
            (geo['geolocation_lat'].between(-90, 90)) & 
            (geo['geolocation_lng'].between(-180, 180))
        ]
        
        self.datasets['geolocation'] = geo
    
    def clean_orders(self):
        """Clean orders dataset"""
        print("\n=== CLEANING ORDERS ===")
        
        if 'orders' not in self.datasets:
            return
        
        orders = self.datasets['orders'].copy()
        
        # Standardize date columns
        date_cols = [
            'order_purchase_timestamp',
            'order_approved_at', 
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]
        
        orders = self.standardize_dates(orders, date_cols)
        
        # Remove duplicates
        before_dedup = len(orders)
        orders = orders.drop_duplicates(subset=['order_id'])
        after_dedup = len(orders)
        
        if before_dedup != after_dedup:
            print(f"Removed {before_dedup - after_dedup} duplicate orders")
        
        # Validate order status
        valid_statuses = ['delivered', 'shipped', 'processing', 'canceled', 'invoiced', 'created']
        orders = orders[orders['order_status'].isin(valid_statuses)]
        
        self.datasets['orders'] = orders
    
    def clean_order_items(self):
        """Clean order items dataset"""
        print("\n=== CLEANING ORDER ITEMS ===")
        
        if 'order_items' not in self.datasets:
            return
        
        items = self.datasets['order_items'].copy()
        
        items = self.standardize_dates(items, ['shipping_limit_date'])
        
        # Remove negative prices and freight values
        items = items[
            (items['price'] >= 0) & 
            (items['freight_value'] >= 0)
        ]
        
        # Remove duplicates
        before_dedup = len(items)
        items = items.drop_duplicates()
        after_dedup = len(items)
        
        if before_dedup != after_dedup:
            print(f"Removed {before_dedup - after_dedup} duplicate order items")
        
        self.datasets['order_items'] = items
    
    def clean_customers(self):
        """Clean customers dataset"""
        print("\n=== CLEANING CUSTOMERS ===")
        
        if 'customers' not in self.datasets:
            return
        
        customers = self.datasets['customers'].copy()
        
        customers['customer_city'] = customers['customer_city'].apply(self.clean_text_encoding)
        
        # Remove duplicates (keep first unique customer)
        before_dedup = len(customers)
        customers = customers.drop_duplicates(subset=['customer_unique_id'], keep='first')
        after_dedup = len(customers)
        
        if before_dedup != after_dedup:
            print(f"Removed {before_dedup - after_dedup} duplicate customers")
        
        self.datasets['customers'] = customers
    
    def clean_sellers(self):
        """Clean sellers dataset"""
        print("\n=== CLEANING SELLERS ===")
        
        if 'sellers' not in self.datasets:
            return
        
        sellers = self.datasets['sellers'].copy()
        
        # Clean city names
        sellers['seller_city'] = sellers['seller_city'].apply(self.clean_text_encoding)
        
        # Remove duplicates
        before_dedup = len(sellers)
        sellers = sellers.drop_duplicates(subset=['seller_id'])
        after_dedup = len(sellers)
        
        if before_dedup != after_dedup:
            print(f"Removed {before_dedup - after_dedup} duplicate sellers")
        
        self.datasets['sellers'] = sellers
    
    def clean_products(self):
        """Clean products dataset"""
        print("\n=== CLEANING PRODUCTS ===")
        
        if 'products' not in self.datasets:
            return
        
        products = self.datasets['products'].copy()
        
        # Remove duplicates
        before_dedup = len(products)
        products = products.drop_duplicates(subset=['product_id'])
        after_dedup = len(products)
        
        if before_dedup != after_dedup:
            print(f"Removed {before_dedup - after_dedup} duplicate products")
        
        # Add English category names if translation available
        if 'product_translation' in self.datasets:
            translation = self.datasets['product_translation']
            products = products.merge(
                translation,
                on='product_category_name',
                how='left'
            )
        
        # Fill missing dimensions with median values by category
        numeric_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
        
        for col in numeric_cols:
            if col in products.columns:
                products[col] = products.groupby('product_category_name')[col].transform(
                    lambda x: x.fillna(x.median())
                )
        
        self.datasets['products'] = products
    
    def clean_payments(self):
        """Clean payments dataset"""
        print("\n=== CLEANING PAYMENTS ===")
        
        if 'payments' not in self.datasets:
            return
        
        payments = self.datasets['payments'].copy()
        
        # Remove negative payment values
        payments = payments[payments['payment_value'] >= 0]
        
        # Standardize payment types
        payments['payment_type'] = payments['payment_type'].str.lower().str.strip()
        
        self.datasets['payments'] = payments
    
    def clean_reviews(self):
        """Clean reviews dataset"""
        print("\n=== CLEANING REVIEWS ===")
        
        if 'reviews' not in self.datasets:
            return
        
        reviews = self.datasets['reviews'].copy()
        
        # Standardize dates
        date_cols = ['review_creation_date', 'review_answer_timestamp']
        reviews = self.standardize_dates(reviews, date_cols)
        
        # Clean text fields
        text_cols = ['review_comment_title', 'review_comment_message']
        for col in text_cols:
            if col in reviews.columns:
                reviews[col] = reviews[col].apply(self.clean_text_encoding)
        
        # Validate review scores (should be 1-5)
        reviews = reviews[reviews['review_score'].between(1, 5)]
        
        # Remove duplicates
        before_dedup = len(reviews)
        reviews = reviews.drop_duplicates(subset=['review_id'])
        after_dedup = len(reviews)
        
        if before_dedup != after_dedup:
            print(f"Removed {before_dedup - after_dedup} duplicate reviews")
        
        self.datasets['reviews'] = reviews
    
    def create_master_dataset(self):
        """Merge all datasets into a comprehensive master dataset"""
        print("\n=== CREATING MASTER DATASET ===")
        
        # Start with orders as the base
        if 'orders' not in self.datasets:
            print("Error: Orders dataset not found!")
            return
        
        master = self.datasets['orders'].copy()
        print(f"Starting with orders: {master.shape}")
        
        # Add customer information
        if 'customers' in self.datasets:
            master = master.merge(
                self.datasets['customers'],
                on='customer_id',
                how='left'
            )
            print(f"After adding customers: {master.shape}")
        
        # Add order items (this will create multiple rows per order)
        if 'order_items' in self.datasets:
            master = master.merge(
                self.datasets['order_items'],
                on='order_id',
                how='left'
            )
            print(f"After adding order items: {master.shape}")
        
        # Add product information
        if 'products' in self.datasets:
            master = master.merge(
                self.datasets['products'],
                on='product_id',
                how='left'
            )
            print(f"After adding products: {master.shape}")
        
        # Add seller information
        if 'sellers' in self.datasets:
            master = master.merge(
                self.datasets['sellers'],
                on='seller_id',
                how='left'
            )
            print(f"After adding sellers: {master.shape}")
        
        # Add payment information (aggregate by order)
        if 'payments' in self.datasets:
            payments_agg = self.datasets['payments'].groupby('order_id').agg({
                'payment_type': lambda x: ', '.join(x.unique()),
                'payment_installments': 'max',
                'payment_value': 'sum'
            }).reset_index()
            
            master = master.merge(
                payments_agg,
                on='order_id',
                how='left'
            )
            print(f"After adding payments: {master.shape}")
        
        # Add review information
        if 'reviews' in self.datasets:
            reviews_agg = self.datasets['reviews'].groupby('order_id').agg({
                'review_score': 'mean',
                'review_creation_date': 'first',
                'review_comment_message': 'first'
            }).reset_index()
            
            master = master.merge(
                reviews_agg,
                on='order_id',
                how='left'
            )
            print(f"After adding reviews: {master.shape}")
        
        # Add geolocation for customers
        if 'geolocation' in self.datasets:
            geo_customers = self.datasets['geolocation'].copy()
            geo_customers = geo_customers.rename(columns={
                'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
                'geolocation_lat': 'customer_lat',
                'geolocation_lng': 'customer_lng',
                'geolocation_city': 'customer_geo_city',
                'geolocation_state': 'customer_geo_state'
            })
            
            master = master.merge(
                geo_customers,
                on='customer_zip_code_prefix',
                how='left'
            )
            print(f"After adding customer geolocation: {master.shape}")
        
        # Create additional useful columns
        master['order_item_total'] = master['price'] + master['freight_value']
        
        # Calculate delivery time if possible
        if 'order_purchase_timestamp' in master.columns and 'order_delivered_customer_date' in master.columns:
            master['delivery_days'] = (
                master['order_delivered_customer_date'] - master['order_purchase_timestamp']
            ).dt.days
        
        self.master_dataset = master
        print(f"\nFinal master dataset shape: {master.shape}")
        
        return master
    
    def export_datasets(self, output_dir='cleaned_data'):
        """Export cleaned datasets"""
        import os
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n=== EXPORTING CLEANED DATASETS to {output_dir}/ ===")
        
        # Export individual cleaned datasets
        for name, df in self.datasets.items():
            filename = f"{output_dir}/cleaned_{name}.csv"
            df.to_csv(filename, index=False)
            print(f"Exported {filename}")
        
        # Export master dataset
        if self.master_dataset is not None:
            master_filename = f"{output_dir}/master_dataset.csv"
            self.master_dataset.to_csv(master_filename, index=False)
            print(f"Exported {master_filename}")
    
    def run_full_pipeline(self, file_paths):
        """Run the complete data preparation pipeline"""
        print("OLIST DATA PREPARATION PIPELINE - TEAM A")
        print("="*50)
        
        self.load_datasets(file_paths)
        
        self.assess_data_quality()
    
        self.clean_geolocation()
        self.clean_orders()
        self.clean_order_items()
        self.clean_customers()
        self.clean_sellers()
        self.clean_products()
        self.clean_payments()
        self.clean_reviews()
        
        master = self.create_master_dataset()
        
        print("\n=== FINAL SUMMARY ===")
        for name, df in self.datasets.items():
            print(f"{name}: {df.shape[0]:,} rows, {df.shape[1]} columns")
        
        if self.master_dataset is not None:
            print(f"Master Dataset: {self.master_dataset.shape[0]:,} rows, {self.master_dataset.shape[1]} columns")
        
        return self.datasets, self.master_dataset

if __name__ == "__main__":
    pipeline = OlistDataPreparation()
    
    file_paths = {
        'orders': 'C://Users//91704//Downloads//OlistDataset//olist_orders_dataset.csv',
        'order_items': 'C://Users//91704//Downloads//OlistDataset//olist_order_items_dataset.csv',
        'customers': 'C://Users//91704//Downloads//OlistDataset//olist_customers_dataset.csv',
        'products': 'C://Users//91704//Downloads//OlistDataset//olist_products_dataset.csv',
        'sellers': 'C://Users//91704//Downloads//OlistDataset//olist_sellers_dataset.csv',
        'payments': 'C://Users//91704//Downloads//OlistDataset//olist_order_payments_dataset.csv',
        'reviews': 'C://Users//91704//Downloads//OlistDataset//olist_order_reviews_dataset.csv',
        'geolocation': 'C://Users//91704//Downloads//OlistDataset//olist_geolocation_dataset.csv',
        'product_translation': 'C://Users//91704//Downloads//OlistDataset//product_category_name_translation.csv'
    }
    
    cleaned_datasets, master_dataset = pipeline.run_full_pipeline(file_paths)
    pipeline.export_datasets('C://Users//91704//Downloads//OlistDataset//Exported_final')
    
    print("\n Data preparation complete!")
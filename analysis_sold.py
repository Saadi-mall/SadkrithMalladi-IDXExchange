import pandas as pd
import matplotlib.pyplot as plt
import os
import ssl
import urllib.request

sold202401 = pd.read_csv('CRMLSSold202401.csv')
sold202402 = pd.read_csv('CRMLSSold202402.csv')
sold202403 = pd.read_csv('CRMLSSold202403.csv')
sold202404 = pd.read_csv('CRMLSSold202404.csv')
sold202405 = pd.read_csv('CRMLSSold202405.csv')
sold202406 = pd.read_csv('CRMLSSold202406.csv')
sold202407 = pd.read_csv('CRMLSSold202407.csv')
sold202408 = pd.read_csv('CRMLSSold202408.csv')
sold202409 = pd.read_csv('CRMLSSold202409.csv')
sold202410 = pd.read_csv('CRMLSSold202410.csv')
sold202411 = pd.read_csv('CRMLSSold202411.csv')
sold202412 = pd.read_csv('CRMLSSold202412.csv')
sold202501 = pd.read_csv('CRMLSSold202501.csv')
sold202502 = pd.read_csv('CRMLSSold202502.csv')
sold202503 = pd.read_csv('CRMLSSold202503.csv')
sold202504 = pd.read_csv('CRMLSSold202504.csv')
sold202505 = pd.read_csv('CRMLSSold202505.csv')
sold202506 = pd.read_csv('CRMLSSold202506.csv')
sold202507 = pd.read_csv('CRMLSSold202507.csv')
sold202508 = pd.read_csv('CRMLSSold202508.csv')
sold202509 = pd.read_csv('CRMLSSold202509.csv')
sold202510 = pd.read_csv('CRMLSSold202510.csv')
sold202511 = pd.read_csv('CRMLSSold202511.csv')
sold202512 = pd.read_csv('CRMLSSold202512.csv')
sold202601 = pd.read_csv('CRMLSSold202601.csv')
sold202602 = pd.read_csv('CRMLSSold202602.csv')
sold202603 = pd.read_csv('CRMLSSold202603.csv')

sold = pd.concat([
    sold202401, sold202402, sold202403, sold202404, sold202405, sold202406,
    sold202407, sold202408, sold202409, sold202410, sold202411, sold202412,
    sold202501, sold202502, sold202503, sold202504, sold202505, sold202506,
    sold202507, sold202508, sold202509, sold202510, sold202511, sold202512,
    sold202601, sold202602, sold202603
], ignore_index=True)

print(f"Rows before Residential filter: {len(sold)}")
sold = sold[sold['PropertyType'] == 'Residential']
print(f"Rows after Residential filter: {len(sold)}")

sold.to_csv('sold_combined.csv', index=False)
print("Saved to sold_combined.csv")

# ── Convert dates ──────────────────────────────────────────
for col in ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']:
    sold[col] = pd.to_datetime(sold[col], errors='coerce')

# ── Ensure numeric types ───────────────────────────────────
for col in ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
            'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']:
    sold[col] = pd.to_numeric(sold[col], errors='coerce')

# ── Drop >90% missing columns ──────────────────────────────
missing = pd.DataFrame({
    'missing_count': sold.isnull().sum(),
    'missing_pct': (sold.isnull().sum() / len(sold) * 100).round(2)
}).sort_values('missing_pct', ascending=False)
print(f"\nMissing values:\n{missing}")

drop_candidates = missing[missing['missing_pct'] > 90].index.tolist()
print(f"\nColumns >90% missing (drop candidates): {drop_candidates}")
sold = sold.drop(columns=drop_candidates, errors='ignore')

# ── Flag and remove invalid numeric records ────────────────
print(f"\nInvalid ClosePrice: {(sold['ClosePrice'] <= 0).sum()}")
print(f"Invalid LivingArea: {(sold['LivingArea'] <= 0).sum()}")
print(f"Invalid DaysOnMarket: {(sold['DaysOnMarket'] < 0).sum()}")
print(f"Invalid Bedrooms: {(sold['BedroomsTotal'] < 0).sum()}")
print(f"Invalid Bathrooms: {(sold['BathroomsTotalInteger'] < 0).sum()}")

sold = sold[
    (sold['ClosePrice'] > 0) &
    (sold['LivingArea'] > 0) &
    (sold['DaysOnMarket'] >= 0) &
    (sold['BedroomsTotal'] >= 0) &
    (sold['BathroomsTotalInteger'] >= 0)
]
print(f"\nRows after removing invalid records: {len(sold)}")

# ── Date consistency flags ─────────────────────────────────
sold['listing_after_close_flag'] = sold['ListingContractDate'] > sold['CloseDate']
sold['purchase_after_close_flag'] = sold['PurchaseContractDate'] > sold['CloseDate']
sold['negative_timeline_flag'] = sold['ListingContractDate'] > sold['PurchaseContractDate']

print(f"\nlisting_after_close_flag: {sold['listing_after_close_flag'].sum()}")
print(f"purchase_after_close_flag: {sold['purchase_after_close_flag'].sum()}")
print(f"negative_timeline_flag: {sold['negative_timeline_flag'].sum()}")

# ── Geographic flags ───────────────────────────────────────
sold['missing_coords_flag'] = sold['Latitude'].isnull() | sold['Longitude'].isnull()
sold['zero_coords_flag'] = (sold['Latitude'] == 0) | (sold['Longitude'] == 0)
sold['positive_longitude_flag'] = sold['Longitude'] > 0
sold['out_of_state_flag'] = (
    (sold['Latitude'] < 32.5) | (sold['Latitude'] > 42.0) |
    (sold['Longitude'] < -124.5) | (sold['Longitude'] > -114.0)
)

print(f"\nMissing coords: {sold['missing_coords_flag'].sum()}")
print(f"Zero coords: {sold['zero_coords_flag'].sum()}")
print(f"Positive longitude: {sold['positive_longitude_flag'].sum()}")
print(f"Out of state: {sold['out_of_state_flag'].sum()}")

# ── Mortgage rate enrichment ───────────────────────────────
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
ssl_context = ssl._create_unverified_context()
with urllib.request.urlopen(url, context=ssl_context) as response:
    mortgage = pd.read_csv(response)
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index()

sold['year_month'] = sold['CloseDate'].dt.to_period('M')
sold = sold.merge(mortgage_monthly, on='year_month', how='left')
print(f"\nNull rate values after merge: {sold['rate_30yr_fixed'].isnull().sum()}")

# ── Feature engineering ────────────────────────────────────
sold['price_ratio'] = sold['ClosePrice'] / sold['ListPrice']
sold['close_to_original_list_ratio'] = sold['ClosePrice'] / sold['OriginalListPrice']
sold['price_per_sqft'] = sold['ClosePrice'] / sold['LivingArea']
sold['close_year'] = sold['CloseDate'].dt.year
sold['close_month'] = sold['CloseDate'].dt.month
sold['close_yrmo'] = sold['CloseDate'].dt.to_period('M').astype(str)
sold['listing_to_contract_days'] = (sold['PurchaseContractDate'] - sold['ListingContractDate']).dt.days
sold['contract_to_close_days'] = (sold['CloseDate'] - sold['PurchaseContractDate']).dt.days

# ── EDA plots (after cleaning) ─────────────────────────────
os.makedirs('eda_output_sold', exist_ok=True)

numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                  'DaysOnMarket', 'YearBuilt']

print(f"\nPercentile summaries:")
print(sold[numeric_fields].describe(percentiles=[.05, .25, .5, .75, .95]))

for field in numeric_fields:
    p05 = sold[field].quantile(0.05)
    p95 = sold[field].quantile(0.95)
    trimmed = sold[field][(sold[field] >= p05) & (sold[field] <= p95)].dropna()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    trimmed.plot(kind='hist', bins=50, ax=ax1, title=f'{field} Histogram (5th-95th pct)')
    trimmed.plot(kind='box', ax=ax2, title=f'{field} Boxplot (5th-95th pct)')
    plt.tight_layout()
    plt.savefig(f'eda_output_sold/{field}.png')
    plt.close()

print(f"\nMedian ClosePrice: ${sold['ClosePrice'].median():,.0f}")
print(f"Mean ClosePrice: ${sold['ClosePrice'].mean():,.0f}")

sold['AboveList'] = sold['ClosePrice'] > sold['ListPrice']
above = sold['AboveList'].sum()
below = (~sold['AboveList']).sum()
print(f"\nSold above list: {above} ({above/len(sold)*100:.1f}%)")
print(f"Sold below list: {below} ({below/len(sold)*100:.1f}%)")

bad_dates = sold[sold['CloseDate'] < sold['ListingContractDate']]
print(f"\nRecords where CloseDate < ListingContractDate: {len(bad_dates)}")

print(f"\nMedian ClosePrice by County:\n{sold.groupby('CountyOrParish')['ClosePrice'].median().sort_values(ascending=False).head(10)}")

# ── Segment summaries ──────────────────────────────────────
print("\nSegment summary by CountyOrParish:")
print(sold.groupby('CountyOrParish').agg(
    median_close_price=('ClosePrice', 'median'),
    median_ppsf=('price_per_sqft', 'median'),
    median_dom=('DaysOnMarket', 'median'),
    median_price_ratio=('price_ratio', 'median'),
    transaction_count=('ClosePrice', 'count')
).sort_values('median_close_price', ascending=False).head(15).to_string())

print("\nSegment summary by PropertySubType:")
print(sold.groupby('PropertySubType').agg(
    median_close_price=('ClosePrice', 'median'),
    median_ppsf=('price_per_sqft', 'median'),
    median_dom=('DaysOnMarket', 'median'),
    median_price_ratio=('price_ratio', 'median'),
    transaction_count=('ClosePrice', 'count')
).sort_values('transaction_count', ascending=False).head(15).to_string())

print("\nSegment summary by ListOfficeName (top 15 by volume):")
print(sold.groupby('ListOfficeName').agg(
    median_close_price=('ClosePrice', 'median'),
    median_ppsf=('price_per_sqft', 'median'),
    median_dom=('DaysOnMarket', 'median'),
    transaction_count=('ClosePrice', 'count')
).sort_values('transaction_count', ascending=False).head(15).to_string())

sold.to_csv('sold_enriched.csv', index=False)
print("\nSaved to sold_enriched.csv")
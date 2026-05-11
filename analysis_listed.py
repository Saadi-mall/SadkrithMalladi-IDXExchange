import pandas as pd
import matplotlib.pyplot as plt
import os
import ssl
import urllib.request

listed202402 = pd.read_csv('CRMLSListing202402.csv')
listed202403 = pd.read_csv('CRMLSListing202403.csv')
listed202404 = pd.read_csv('CRMLSListing202404.csv')
listed202405 = pd.read_csv('CRMLSListing202405.csv')
listed202406 = pd.read_csv('CRMLSListing202406.csv')
listed202407 = pd.read_csv('CRMLSListing202407.csv')
listed202408 = pd.read_csv('CRMLSListing202408.csv')
listed202409 = pd.read_csv('CRMLSListing202409.csv')
listed202410 = pd.read_csv('CRMLSListing202410.csv')
listed202411 = pd.read_csv('CRMLSListing202411.csv')
listed202412 = pd.read_csv('CRMLSListing202412.csv')
listed202501 = pd.read_csv('CRMLSListing202501.csv')
listed202502 = pd.read_csv('CRMLSListing202502.csv')
listed202503 = pd.read_csv('CRMLSListing202503.csv')
listed202504 = pd.read_csv('CRMLSListing202504.csv')
listed202505 = pd.read_csv('CRMLSListing202505.csv')
listed202506 = pd.read_csv('CRMLSListing202506.csv')
listed202507 = pd.read_csv('CRMLSListing202507.csv')
listed202508 = pd.read_csv('CRMLSListing202508.csv')
listed202509 = pd.read_csv('CRMLSListing202509.csv')
listed202510 = pd.read_csv('CRMLSListing202510.csv')
listed202511 = pd.read_csv('CRMLSListing202511.csv')
listed202512 = pd.read_csv('CRMLSListing202512.csv')
listed202601 = pd.read_csv('CRMLSListing202601.csv')
listed202602 = pd.read_csv('CRMLSListing202602.csv')
listed202603 = pd.read_csv('CRMLSListing202603.csv')

listed = pd.concat([
    listed202402, listed202403, listed202404, listed202405, listed202406,
    listed202407, listed202408, listed202409, listed202410, listed202411, listed202412,
    listed202501, listed202502, listed202503, listed202504, listed202505, listed202506,
    listed202507, listed202508, listed202509, listed202510, listed202511, listed202512,
    listed202601, listed202602, listed202603
], ignore_index=True)

print(f"Rows before Residential filter: {len(listed)}")
listed = listed[listed['PropertyType'] == 'Residential']
print(f"Rows after Residential filter: {len(listed)}")

listed.to_csv('listed_combined.csv', index=False)
print("Saved to listed_combined.csv")

# ── Convert dates ──────────────────────────────────────────
for col in ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']:
    listed[col] = pd.to_datetime(listed[col], errors='coerce')

# ── Ensure numeric types ───────────────────────────────────
for col in ['ListPrice', 'OriginalListPrice', 'LivingArea', 'LotSizeAcres',
            'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']:
    listed[col] = pd.to_numeric(listed[col], errors='coerce')

# ── Drop >90% missing columns ──────────────────────────────
missing = pd.DataFrame({
    'missing_count': listed.isnull().sum(),
    'missing_pct': (listed.isnull().sum() / len(listed) * 100).round(2)
}).sort_values('missing_pct', ascending=False)
print(f"\nMissing values:\n{missing}")

drop_candidates = missing[missing['missing_pct'] > 90].index.tolist()
print(f"\nColumns >90% missing (drop candidates): {drop_candidates}")
listed = listed.drop(columns=drop_candidates, errors='ignore')

# ── Flag and remove invalid numeric records ────────────────
print(f"\nInvalid ListPrice: {(listed['ListPrice'] <= 0).sum()}")
print(f"Invalid LivingArea: {(listed['LivingArea'] <= 0).sum()}")
print(f"Invalid DaysOnMarket: {(listed['DaysOnMarket'] < 0).sum()}")
print(f"Invalid Bedrooms: {(listed['BedroomsTotal'] < 0).sum()}")
print(f"Invalid Bathrooms: {(listed['BathroomsTotalInteger'] < 0).sum()}")

listed = listed[
    (listed['ListPrice'] > 0) &
    (listed['LivingArea'] > 0) &
    (listed['DaysOnMarket'] >= 0) &
    (listed['BedroomsTotal'] >= 0) &
    (listed['BathroomsTotalInteger'] >= 0)
]
print(f"\nRows after removing invalid records: {len(listed)}")

# ── Date consistency flags ─────────────────────────────────
listed['listing_after_close_flag'] = listed['ListingContractDate'] > listed['CloseDate']
listed['purchase_after_close_flag'] = listed['PurchaseContractDate'] > listed['CloseDate']
listed['negative_timeline_flag'] = listed['ListingContractDate'] > listed['PurchaseContractDate']

print(f"\nlisting_after_close_flag: {listed['listing_after_close_flag'].sum()}")
print(f"purchase_after_close_flag: {listed['purchase_after_close_flag'].sum()}")
print(f"negative_timeline_flag: {listed['negative_timeline_flag'].sum()}")

# ── Geographic flags ───────────────────────────────────────
listed['missing_coords_flag'] = listed['Latitude'].isnull() | listed['Longitude'].isnull()
listed['zero_coords_flag'] = (listed['Latitude'] == 0) | (listed['Longitude'] == 0)
listed['positive_longitude_flag'] = listed['Longitude'] > 0
listed['out_of_state_flag'] = (
    (listed['Latitude'] < 32.5) | (listed['Latitude'] > 42.0) |
    (listed['Longitude'] < -124.5) | (listed['Longitude'] > -114.0)
)

print(f"\nMissing coords: {listed['missing_coords_flag'].sum()}")
print(f"Zero coords: {listed['zero_coords_flag'].sum()}")
print(f"Positive longitude: {listed['positive_longitude_flag'].sum()}")
print(f"Out of state: {listed['out_of_state_flag'].sum()}")

# ── Mortgage rate enrichment ───────────────────────────────
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
ssl_context = ssl._create_unverified_context()
with urllib.request.urlopen(url, context=ssl_context) as response:
    mortgage = pd.read_csv(response)
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index()

listed['year_month'] = listed['ListingContractDate'].dt.to_period('M')
listed = listed.merge(mortgage_monthly, on='year_month', how='left')
print(f"\nNull rate values after merge: {listed['rate_30yr_fixed'].isnull().sum()}")

# ── Feature engineering ────────────────────────────────────
listed['price_ratio'] = listed['ListPrice'] / listed['OriginalListPrice']
listed['price_per_sqft'] = listed['ListPrice'] / listed['LivingArea']
listed['list_year'] = listed['ListingContractDate'].dt.year
listed['list_month'] = listed['ListingContractDate'].dt.month
listed['list_yrmo'] = listed['ListingContractDate'].dt.to_period('M').astype(str)
listed['listing_to_contract_days'] = (listed['PurchaseContractDate'] - listed['ListingContractDate']).dt.days
listed['contract_to_close_days'] = (listed['CloseDate'] - listed['PurchaseContractDate']).dt.days

# ── EDA plots (after cleaning) ─────────────────────────────
os.makedirs('eda_output_listed', exist_ok=True)

numeric_fields = ['ListPrice', 'OriginalListPrice', 'LivingArea', 'LotSizeAcres',
                  'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']

print(f"\nPercentile summaries:")
print(listed[numeric_fields].describe(percentiles=[.05, .25, .5, .75, .95]))

for field in numeric_fields:
    p05 = listed[field].quantile(0.05)
    p95 = listed[field].quantile(0.95)
    trimmed = listed[field][(listed[field] >= p05) & (listed[field] <= p95)].dropna()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    trimmed.plot(kind='hist', bins=50, ax=ax1, title=f'{field} Histogram (5th-95th pct)')
    trimmed.plot(kind='box', ax=ax2, title=f'{field} Boxplot (5th-95th pct)')
    plt.tight_layout()
    plt.savefig(f'eda_output_listed/{field}.png')
    plt.close()

print(f"\nMedian ListPrice: ${listed['ListPrice'].median():,.0f}")
print(f"Mean ListPrice: ${listed['ListPrice'].mean():,.0f}")

listed['PriceCut'] = listed['ListPrice'] < listed['OriginalListPrice']
cuts = listed['PriceCut'].sum()
print(f"\nListings with price cut: {cuts} ({cuts/len(listed)*100:.1f}%)")

bad_dates = listed[listed['CloseDate'] < listed['ListingContractDate']]
print(f"\nRecords where CloseDate < ListingContractDate: {len(bad_dates)}")

print(f"\nMedian ListPrice by County:\n{listed.groupby('CountyOrParish')['ListPrice'].median().sort_values(ascending=False).head(10)}")

# ── Segment summaries ──────────────────────────────────────
print("\nSegment summary by CountyOrParish:")
print(listed.groupby('CountyOrParish').agg(
    median_list_price=('ListPrice', 'median'),
    median_ppsf=('price_per_sqft', 'median'),
    median_dom=('DaysOnMarket', 'median'),
    median_price_ratio=('price_ratio', 'median'),
    listing_count=('ListPrice', 'count')
).sort_values('median_list_price', ascending=False).head(15).to_string())

print("\nSegment summary by PropertySubType:")
print(listed.groupby('PropertySubType').agg(
    median_list_price=('ListPrice', 'median'),
    median_ppsf=('price_per_sqft', 'median'),
    median_dom=('DaysOnMarket', 'median'),
    listing_count=('ListPrice', 'count')
).sort_values('listing_count', ascending=False).head(15).to_string())

print("\nSegment summary by ListOfficeName (top 15 by volume):")
print(listed.groupby('ListOfficeName').agg(
    median_list_price=('ListPrice', 'median'),
    median_ppsf=('price_per_sqft', 'median'),
    median_dom=('DaysOnMarket', 'median'),
    listing_count=('ListPrice', 'count')
).sort_values('listing_count', ascending=False).head(15).to_string())

listed.to_csv('listed_enriched.csv', index=False)
print("\nSaved to listed_enriched.csv")
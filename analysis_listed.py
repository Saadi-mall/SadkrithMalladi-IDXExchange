import pandas as pd
import matplotlib.pyplot as plt
import os

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

# ── EDA ────────────────────────────────────────────────────
os.makedirs('eda_output_listed', exist_ok=True)

print(f"\nShape: {listed.shape}")
print(f"\nColumn dtypes:\n{listed.dtypes}")

missing = pd.DataFrame({
    'missing_count': listed.isnull().sum(),
    'missing_pct': (listed.isnull().sum() / len(listed) * 100).round(2)
}).sort_values('missing_pct', ascending=False)
print(f"\nMissing values:\n{missing}")

drop_candidates = missing[missing['missing_pct'] > 90].index.tolist()
print(f"\nColumns >90% missing (drop candidates): {drop_candidates}")

print(f"\nPropertyType breakdown:\n{listed['PropertyType'].value_counts()}")

numeric_fields = ['ListPrice', 'OriginalListPrice', 'LivingArea', 'LotSizeAcres',
                  'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']

print(f"\nPercentile summaries:")
print(listed[numeric_fields].describe(percentiles=[.05, .25, .5, .75, .95]))

for field in numeric_fields:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    listed[field].dropna().plot(kind='hist', bins=50, ax=ax1, title=f'{field} Histogram')
    listed[field].dropna().plot(kind='box', ax=ax2, title=f'{field} Boxplot')
    plt.tight_layout()
    plt.savefig(f'eda_output_listed/{field}.png')
    plt.close()
    print(f"Saved {field}.png")

print(f"\nMedian ListPrice: ${listed['ListPrice'].median():,.0f}")
print(f"Mean ListPrice: ${listed['ListPrice'].mean():,.0f}")

listed['PriceCut'] = listed['ListPrice'] < listed['OriginalListPrice']
cuts = listed['PriceCut'].sum()
print(f"\nListings with price cut: {cuts} ({cuts/len(listed)*100:.1f}%)")

print(f"\nDays on Market:\n{listed['DaysOnMarket'].describe()}")

listed['ListingContractDate'] = pd.to_datetime(listed['ListingContractDate'], errors='coerce')
listed['CloseDate'] = pd.to_datetime(listed['CloseDate'], errors='coerce')
bad_dates = listed[listed['CloseDate'] < listed['ListingContractDate']]
print(f"\nRecords where CloseDate < ListingContractDate: {len(bad_dates)}")

print(f"\nMedian ListPrice by County:\n{listed.groupby('CountyOrParish')['ListPrice'].median().sort_values(ascending=False).head(10)}")
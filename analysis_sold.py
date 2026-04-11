import pandas as pd
import matplotlib.pyplot as plt
import os

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

# ── EDA ────────────────────────────────────────────────────
os.makedirs('eda_output_sold', exist_ok=True)

print(f"\nShape: {sold.shape}")
print(f"\nColumn dtypes:\n{sold.dtypes}")

missing = pd.DataFrame({
    'missing_count': sold.isnull().sum(),
    'missing_pct': (sold.isnull().sum() / len(sold) * 100).round(2)
}).sort_values('missing_pct', ascending=False)
print(f"\nMissing values:\n{missing}")

drop_candidates = missing[missing['missing_pct'] > 90].index.tolist()
print(f"\nColumns >90% missing (drop candidates): {drop_candidates}")

print(f"\nPropertyType breakdown:\n{sold['PropertyType'].value_counts()}")

numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                  'DaysOnMarket', 'YearBuilt']

print(f"\nPercentile summaries:")
print(sold[numeric_fields].describe(percentiles=[.05, .25, .5, .75, .95]))

for field in numeric_fields:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    sold[field].dropna().plot(kind='hist', bins=50, ax=ax1, title=f'{field} Histogram')
    sold[field].dropna().plot(kind='box', ax=ax2, title=f'{field} Boxplot')
    plt.tight_layout()
    plt.savefig(f'eda_output_sold/{field}.png')
    plt.close()
    print(f"Saved {field}.png")

print(f"\nMedian ClosePrice: ${sold['ClosePrice'].median():,.0f}")
print(f"Mean ClosePrice: ${sold['ClosePrice'].mean():,.0f}")

sold['AboveList'] = sold['ClosePrice'] > sold['ListPrice']
above = sold['AboveList'].sum()
below = (~sold['AboveList']).sum()
print(f"\nSold above list: {above} ({above/len(sold)*100:.1f}%)")
print(f"Sold below list: {below} ({below/len(sold)*100:.1f}%)")

print(f"\nDays on Market:\n{sold['DaysOnMarket'].describe()}")

sold['CloseDate'] = pd.to_datetime(sold['CloseDate'], errors='coerce')
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'], errors='coerce')
bad_dates = sold[sold['CloseDate'] < sold['ListingContractDate']]
print(f"\nRecords where CloseDate < ListingContractDate: {len(bad_dates)}")

print(f"\nMedian ClosePrice by County:\n{sold.groupby('CountyOrParish')['ClosePrice'].median().sort_values(ascending=False).head(10)}")
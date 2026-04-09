import pandas as pd

# Load all monthly sold CSVs
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
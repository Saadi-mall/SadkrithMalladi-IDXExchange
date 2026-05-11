import csv
import requests
from datetime import datetime

auth_endpoint = 'https://idxexchange.com/internal-api/trestle_token.php?key=IDXEXCHANGE2026_CHANGE_THIS'
response = requests.get(auth_endpoint, timeout=30)
response.raise_for_status()
token = response.json().get('access_token')

if not token:
    print("Error retrieving token")
    exit()

headers = {'Authorization': f'Bearer {token}'}

months = [
    (2024, 1), (2024, 2), (2024, 3), (2024, 4), (2024, 5), (2024, 6),
    (2024, 7), (2024, 8), (2024, 9), (2024, 10), (2024, 11), (2024, 12),
    (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6),
    (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
    (2026, 1), (2026, 2), (2026, 3)
]

fieldnames = ['BuyerAgentAOR','ListAgentAOR','Flooring','ViewYN','WaterfrontYN','BasementYN',
'PoolPrivateYN','OriginalListPrice','ListingKey','CloseDate','ClosePrice','ListAgentFirstName',
'ListAgentLastName','Latitude','Longitude','UnparsedAddress','PropertyType','LivingArea',
'ListPrice','DaysOnMarket','ListOfficeName','BuyerOfficeName','CoListOfficeName',
'ListAgentFullName','CoListAgentFirstName','CoListAgentLastName','BuyerAgentMlsId',
'BuyerAgentFirstName','BuyerAgentLastName','FireplacesTotal','AssociationFeeFrequency',
'AboveGradeFinishedArea','ListingKeyNumeric','MLSAreaMajor','TaxAnnualAmount','CountyOrParish',
'MlsStatus','ElementarySchool','AttachedGarageYN','ParkingTotal','BuilderName','PropertySubType',
'LotSizeAcres','SubdivisionName','BuyerOfficeAOR','YearBuilt','StreetNumberNumeric','ListingId',
'BathroomsTotalInteger','City','TaxYear','BuildingAreaTotal','BedroomsTotal',
'ContractStatusChangeDate','ElementarySchoolDistrict','CoBuyerAgentFirstName',
'PurchaseContractDate','ListingContractDate','BelowGradeFinishedArea','BusinessType',
'StateOrProvince','CoveredSpaces','MiddleOrJuniorSchool','FireplaceYN','Stories','HighSchool',
'Levels','LotSizeDimensions','LotSizeArea','MainLevelBedrooms','NewConstructionYN','GarageSpaces',
'HighSchoolDistrict','PostalCode','AssociationFee','LotSizeSquareFeet',
'MiddleOrJuniorSchoolDistrict','OriginatingSystemName','OriginatingSystemSubName']

for year, month in months:
    start = datetime(year, month, 1).isoformat(timespec='milliseconds') + 'Z'
    if month == 12:
        end = datetime(year + 1, 1, 1).isoformat(timespec='milliseconds') + 'Z'
    else:
        end = datetime(year, month + 1, 1).isoformat(timespec='milliseconds') + 'Z'

    url = 'https://api-trestle.corelogic.com/trestle/odata/Property'
    params = {
        '$select': ','.join(fieldnames),
        '$filter': f"MlsStatus eq 'Closed' and CloseDate ge {start} and CloseDate lt {end}",
        '$top': 1000
    }

    csv_file = f'CRMLSSold{year}{str(month).zfill(2)}.csv'
    total_records = 0

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                observations = data.get('value', [])
                for obs in observations:
                    writer.writerow({f: obs.get(f, '') for f in fieldnames})
                    total_records += 1
                if '@odata.nextLink' in data:
                    url = data['@odata.nextLink']
                    params = None
                else:
                    break
            else:
                print(f"Error {response.status_code} for {csv_file}: {response.text}")
                break

    print(f"{csv_file}: {total_records} records")
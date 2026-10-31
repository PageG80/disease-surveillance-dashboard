import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

def generate_surveillance_data():
    print("Generating 12-week epidemiological and inventory dataset...")

    sub_counties = [
        'Kibera', 'Westlands', 'Embakasi', 'Kasarani', 
        'Langata', 'Dagoretti', 'Starehe', 'Makadara'
    ]
    
    diseases = ['Cholera', 'Malaria', 'Typhoid']
    
    coordinates = {
        'Kibera': (-1.3131, 36.7844),
        'Westlands': (-1.2676, 36.8108),
        'Embakasi': (-1.2833, 36.9000),
        'Kasarani': (-1.2217, 36.8904),
        'Langata': (-1.3653, 36.7073),
        'Dagoretti': (-1.2921, 36.7456),
        'Starehe': (-1.2786, 36.8383),
        'Makadara': (-1.3000, 36.8667)
    }

    start_date = datetime.now() - timedelta(weeks=12)
    
    data = []
    record_id = 1

    for week in range(1, 13):
        week_date = start_date + timedelta(weeks=week)
        
        for county in sub_counties:
            for disease in diseases:
                base_cases = np.random.poisson(lam=15)
                if county == 'Kibera' and disease == 'Cholera' and week >= 9:
                    cases = int(base_cases * np.random.uniform(2.5, 4.0)) 
                elif county == 'Embakasi' and disease == 'Malaria' and week >= 8:
                    cases = int(base_cases * np.random.uniform(2.0, 3.2))
                else:
                    cases = int(base_cases * np.random.uniform(0.8, 1.4))

                historical_avg = base_cases * 1.1
                is_outbreak = cases >= (historical_avg * 1.5) 
                drug_stock_left = np.random.randint(50, 500)
                if is_outbreak:
                    drug_stock_left = max(5, drug_stock_left - int(cases * 1.2))

                lat, lon = coordinates[county]

                data.append({
                    'report_id': f"REP-{1000 + record_id}",
                    'week_number': week,
                    'report_date': week_date.strftime('%Y-%m-%d'),
                    'sub_county': county,
                    'disease': disease,
                    'cases_reported': cases,
                    'historical_average': round(historical_avg, 1),
                    'outbreak_alert': 1 if is_outbreak else 0,
                    'drug_stock_left': drug_stock_left,
                    'latitude': lat,
                    'longitude': lon
                })
                record_id += 1

    df = pd.DataFrame(data)
    return df

def save_to_sqlite(df, db_path='data/surveillance.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql('outbreak_reports', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Successfully saved epidemiological database to {db_path} with {len(df)} records.")

if __name__ == '__main__':
    df = generate_surveillance_data()
    save_to_sqlite(df)
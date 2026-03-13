"""
data_cleaning.py
Cleans raw survey CSV and produces analysis-ready dataset.
Run standalone: python data_cleaning.py
Or import: from data_cleaning import load_and_clean
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


# ── Mappings ────────────────────────────────────────────────
GENDER_MAP = {
    'Male': 'Male', 'male': 'Male', 'MALE': 'Male', 'M': 'Male',
    'Female': 'Female', 'female': 'Female', 'F': 'Female',
    'Prefer not to say': 'Prefer not to say'
}

NATIONALITY_MAP = {
    'South Asian': 'South Asian', 'south asian': 'South Asian',
    'Arab': 'Arab', 'ARAB': 'Arab',
    'Western Expat': 'Western Expat', 'western': 'Western Expat',
    'East Asian': 'East Asian', 'asian': 'East Asian',
    'African': 'African', 'Other': 'Other'
}

INCOME_ORDER = ['Below 3,000', '3,000-10,000', '10,001-20,000', '20,001-35,000', '35,001-50,000', 'Above 50,000']
INCOME_MIDPOINTS = {
    'Below 3,000': 2000, '3,000-10,000': 6500, '10,001-20,000': 15000,
    '20,001-35,000': 27500, '35,001-50,000': 42500, 'Above 50,000': 60000
}

AGE_MIDPOINTS = {'18-24': 21, '25-34': 29.5, '35-44': 39.5, '45-54': 49.5, '55-65': 60}

SPEND_ORDER = ['Under 50', '50-200', '201-500', '501-1,500', '1,501-3,000', '3,000+']
SPEND_MIDPOINTS = {
    'Under 50': 30, '50-200': 125, '201-500': 350,
    '501-1,500': 1000, '1,501-3,000': 2250, '3,000+': 4000
}

FREQ_ORDER = ['Once a year or less', '2-4 times a year', '5-10 times a year', 'More than 10 times a year']
FREQ_MIDPOINTS = {
    'Once a year or less': 1, '2-4 times a year': 3,
    '5-10 times a year': 7, 'More than 10 times a year': 12
}

FAN_TYPE_WEIGHT = {
    'Casual viewer': 1, 'Passionate fan': 2,
    'Hardcore collector': 4, 'Investment buyer': 3
}

PLATFORM_BINARY = {
    'Definitely yes': 1, 'Probably yes': 1,
    'Not sure': 0, 'Probably no': 0, 'Definitely no': 0
}


def load_and_clean(path="data_raw.csv"):
    """Load raw survey CSV and return cleaned DataFrame plus a log of cleaning steps."""
    log = []
    df = pd.read_csv(path)
    log.append(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    # ── 1. Remove duplicates ────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset=df.columns[1:], keep='first').reset_index(drop=True)
    removed = before - len(df)
    log.append(f"Removed {removed} duplicate rows → {len(df)} rows remaining")

    # ── 2. Fix typos / standardize text ─────────────────────
    df['Q2_Gender'] = df['Q2_Gender'].map(GENDER_MAP).fillna(df['Q2_Gender'])
    df['Q3_Nationality_Cluster'] = df['Q3_Nationality_Cluster'].map(NATIONALITY_MAP).fillna(df['Q3_Nationality_Cluster'])
    log.append("Standardized gender and nationality text entries")

    # ── 3. Handle missing values ────────────────────────────
    missing_before = df.isnull().sum()
    missing_cols = missing_before[missing_before > 0]
    for col, count in missing_cols.items():
        log.append(f"  Missing in {col}: {count} ({count/len(df)*100:.1f}%)")

    # Q1_Age_Group — fill with mode
    df['Q1_Age_Group'] = df['Q1_Age_Group'].fillna(df['Q1_Age_Group'].mode()[0])

    # Q4_Monthly_Income — fill with mode within nationality cluster
    df['Q4_Monthly_Income'] = df.groupby('Q3_Nationality_Cluster')['Q4_Monthly_Income'].transform(
        lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 'Unknown')
    )

    # Q9_Jerseys_Owned — NaN is legitimate (answered No to Q8), leave as-is
    # Q16_Willingness_to_Spend — fill with mode within fan type
    df['Q16_Willingness_to_Spend'] = df.groupby('Q7_Fan_Type')['Q16_Willingness_to_Spend'].transform(
        lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 'Unknown')
    )

    # Q21 — fill with "Not sure" (neutral)
    df['Q21_Would_Use_Platform'] = df['Q21_Would_Use_Platform'].fillna('Not sure')

    # Q25 — fill with "Not provided"
    df['Q25_Feature_Ranking'] = df['Q25_Feature_Ranking'].fillna('Not provided')

    log.append("Imputed missing values (mode-based, context-aware)")

    # ── 4. Create numeric encodings ─────────────────────────
    df['Age_Numeric'] = df['Q1_Age_Group'].map(AGE_MIDPOINTS)
    df['Income_Numeric'] = df['Q4_Monthly_Income'].map(INCOME_MIDPOINTS)
    df['Spend_Numeric'] = df['Q16_Willingness_to_Spend'].map(SPEND_MIDPOINTS)
    df['Freq_Numeric'] = df['Q17_Purchase_Frequency'].map(FREQ_MIDPOINTS)
    df['Fan_Type_Weight'] = df['Q7_Fan_Type'].map(FAN_TYPE_WEIGHT)

    # ── 5. Derived features ─────────────────────────────────
    df['Collector_Score'] = df['Freq_Numeric'] * df['Fan_Type_Weight']
    df['Value_Sensitivity'] = df['Q14_Rarity_Importance'] * df['Q13_Player_Popularity_Importance']
    df['Auth_Rarity_Index'] = df['Q11_Authentication_Importance'] * df['Q14_Rarity_Importance']
    log.append("Created derived features: Collector_Score, Value_Sensitivity, Auth_Rarity_Index")

    # ── 6. Binary target variable ───────────────────────────
    df['Platform_Adoption'] = df['Q21_Would_Use_Platform'].map(PLATFORM_BINARY)
    log.append("Created binary target: Platform_Adoption (Definitely/Probably yes = 1, else = 0)")

    # ── 7. Flag outliers ────────────────────────────────────
    df['Outlier_Flag'] = 0

    # Young + low income + high spend
    mask1 = (
        (df['Q1_Age_Group'] == '18-24') &
        (df['Q4_Monthly_Income'] == 'Below 3,000') &
        (df['Q16_Willingness_to_Spend'] == '3,000+')
    )
    df.loc[mask1, 'Outlier_Flag'] = 1

    # Casual + 26+ jerseys
    mask2 = (df['Q7_Fan_Type'] == 'Casual viewer') & (df['Q9_Jerseys_Owned'] == '26+')
    df.loc[mask2, 'Outlier_Flag'] = 1

    # No jerseys + high frequency
    mask3 = (df['Q8_Own_Jerseys'] == 'No') & (df['Q17_Purchase_Frequency'] == 'More than 10 times a year')
    df.loc[mask3, 'Outlier_Flag'] = 1

    outlier_count = df['Outlier_Flag'].sum()
    log.append(f"Flagged {outlier_count} outlier rows")

    # ── 8. Parse trust factors into individual columns ──────
    all_trust = [
        'Third-party authentication certificates', 'Blockchain verification',
        'Seller ratings and reviews', 'Money-back guarantee', 'AI-powered authenticity checks'
    ]
    for factor in all_trust:
        col_name = 'Trust_' + factor.split()[0]
        df[col_name] = df['Q22_Trust_Factors'].str.contains(factor, na=False).astype(int)
    log.append("Parsed Q22 multi-select into 5 binary trust columns")

    # ── 9. Parse Q25 ranking → extract top-ranked feature ───
    df['Top_Feature'] = df['Q25_Feature_Ranking'].apply(
        lambda x: x.split(' > ')[0].strip() if isinstance(x, str) and ' > ' in x else 'Not provided'
    )
    log.append("Extracted top-ranked feature from Q25")

    # ── 10. Reassign clean Response_ID ──────────────────────
    df['Response_ID'] = range(1, len(df) + 1)
    log.append(f"Final dataset: {len(df)} rows, {len(df.columns)} columns")

    return df, log


if __name__ == "__main__":
    df, log = load_and_clean("data_raw.csv")
    print("\n".join(log))
    df.to_csv("data_cleaned.csv", index=False)
    print(f"\nSaved cleaned data → data_cleaned.csv")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

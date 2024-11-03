import pandas as pd

class ExperianParser:
    def clean_phone(self, phone):
        if pd.isna(phone) or phone == '':
            return ''
        # Remove any non-numeric characters
        clean = ''.join(filter(str.isdigit, str(phone)))
        # Keep only last 10 digits if longer
        return clean[-10:] if len(clean) >= 10 else ''

    def parse(self, df):
        # Clean up column names and handle duplicates
        df.columns = df.columns.str.strip()
        parsed_df = pd.DataFrame()
        
        # Handle address first
        street_number = df['Primary Street ID (House number)'].fillna('')
        street_name = df['Street Name/Apartment'].fillna('')
        parsed_df['Address'] = street_number.astype(str) + ' ' + street_name.astype(str)
        
        # Map basic fields
        field_mapping = {
            'First Name': 'First_Name',
            'Surname': 'Last_Name',
            'City': 'City',
            'State': 'State',
            'Zip Code': 'Zipcode',
            'FICO_V30A_PSCRN_SCORE_VALUE': 'credit_score',
            'Total balance on open first mortgage trades reported in the last 3 months': 'current_balance',
            'Estimated interest rate on open with balance first mortgage loans with the largest current balance reported in the last 6 months': 'current_rate'
        }
        
        for orig_col, new_col in field_mapping.items():
            if orig_col in df.columns:
                parsed_df[new_col] = df[orig_col]
        
        # Handle phone numbers - check both original and duplicate columns
        phone_mappings = [
            ('Telephone # 1.1', 'Phone_Number'),  # Try the duplicate column first
            ('Telephone # 1', 'Phone_Number'),    # Then the original
            ('Telephone # 2.1', 'Phone_Number_2'),
            ('Telephone # 2', 'Phone_Number_2'),
            ('Telephone # 3.1', 'Phone_Number_3'),
            ('Telephone # 3', 'Phone_Number_3')
        ]
        
        # Add debug logging for phone numbers
        for index, row in df.iterrows():
            found_phone = False
            print(f"\nChecking phone numbers for record {index + 1}:")
            
            for source_field, target_field in phone_mappings:
                if source_field in df.columns:
                    phone_value = self.clean_phone(row[source_field])
                    if phone_value:
                        found_phone = True
                        print(f"  Found valid phone {phone_value} in {source_field}")
            
            if not found_phone:
                print(f"  WARNING: No valid phone numbers found for record {index + 1}")
                print(f"  Raw phone values:")
                for source_field, _ in phone_mappings:
                    if source_field in df.columns:
                        print(f"    {source_field}: {row[source_field]}")

        # Process phone numbers for the DataFrame
        for source_field, target_field in phone_mappings:
            if source_field in df.columns and target_field not in parsed_df:
                phone_values = df[source_field].apply(self.clean_phone)
                if phone_values.any():  # Only set if we found any valid numbers
                    parsed_df[target_field] = phone_values
                    print(f"Added phone numbers from {source_field} to {target_field}")
        
        return parsed_df

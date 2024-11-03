import pandas as pd

class TransUnionParser:
    def parse(self, df):
        """Parse TransUnion CSV format"""
        # Clean up column names
        df.columns = df.columns.str.strip()
        
        # Extract relevant fields
        parsed_df = pd.DataFrame()
        
        # Direct field mappings with exact field names
        field_mapping = {
            'First_Name': 'First_Name',
            'Last_Name': 'Last_Name',
            'Address': 'Address',
            'City': 'City',
            'State': 'State',
            'Zipcode': 'Zipcode',
            'Phone_Number': 'Phone_Number',
            'FICO04 Score': 'credit_score',
            'Current Balance of Most Recent Mortgage': 'current_balance',
            'Monthly Payment Amount of Most Recent Mortgage': 'mortgage_payment',
            'Open Date of Most Recent Mortgage': 'mortgage_open_date',
            'Perm_ID': 'lead_id',
            'Trigger_Date': 'lead_source'
        }
        
        for orig_col, new_col in field_mapping.items():
            if orig_col in df.columns:
                parsed_df[new_col] = df[orig_col]
                
        return parsed_df

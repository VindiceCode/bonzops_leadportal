import pandas as pd

class LeadSourceParser:
    def parse(self, df):
        """Parse LeadSource CSV format"""
        # Clean up column names
        df.columns = df.columns.str.strip()
        
        # Extract relevant fields
        parsed_df = pd.DataFrame()
        
        # Map fields
        field_mapping = {
            'First Name': 'First_Name',
            'Last Name': 'Last_Name',
            'Address': 'Address',
            'City': 'City',
            'State': 'State',
            'ZIP': 'Zipcode',
            'Pri. Phone': 'Phone_Number',
            'Sec. Phone': 'Phone_Number_2',
            'Lead ID': 'lead_id',
            'Lead Type': 'lead_source',
            'Email': 'Email',
            # New field mappings
            'Est. Home Value': 'property_value',
            'Credit Grade': 'credit_score',
            'ADD_CASH': 'additional_cash',
            'Cash Out': 'cash_out',
            'Loan Type': 'loan_type',  # Ensuring loan_type is properly mapped
            'Loan Purpose': 'loan_purpose',
            'Prop. Desc': 'property_description',
            'BAL_ONE': 'current_balance',
            'MTG_ONE_INT': 'current_rate',
            'MTG_TWO': 'second_mortgage',
            'BAL_TWO': 'second_balance',
            'MTG_TWO_INT': 'second_rate',
            'Found Home': 'found_home',
            'DOWN_PMT': 'down_payment',
            'Property Purpose': 'property_purpose',
            'LTV': 'ltv',
            'bid_loan_val': 'bid_loan_value',
            'VA Eligible': 'va_eligible'
        }
        
        for orig_col, new_col in field_mapping.items():
            if orig_col in df.columns:
                parsed_df[new_col] = df[orig_col]
                
        return parsed_df

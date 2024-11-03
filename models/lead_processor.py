import pandas as pd
from utils.experian_parser import ExperianParser
from utils.transunion_parser import TransUnionParser
from utils.leadsource_parser import LeadSourceParser

class LeadProcessor:
    def __init__(self):
        self.experian_parser = ExperianParser()
        self.transunion_parser = TransUnionParser()
        self.leadsource_parser = LeadSourceParser()

    def process_file(self, file, source_type):
        df = pd.read_csv(file)
        
        if source_type == "experian":
            return self.experian_parser.parse(df)
        elif source_type == "transunion":
            return self.transunion_parser.parse(df)
        elif source_type == "leadsource":
            return self.leadsource_parser.parse(df)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _format_phone(self, phone):
        if pd.isna(phone) or phone == '':
            return ''
        # Remove any non-numeric characters
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        # Keep only last 10 digits if longer
        if len(clean_phone) > 10:
            clean_phone = clean_phone[-10:]
        # Check if it's exactly 10 digits and not all zeros
        if len(clean_phone) == 10 and not all(d == '0' for d in clean_phone):
            return clean_phone
        return ''

    def _convert_to_boolean(self, value):
        if pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('yes', 'true', '1', 'y', 't')
        return False

    def normalize_data(self, df):
        # Standardize column names and formats
        normalized = pd.DataFrame()
        
        # Map common fields
        field_mapping = {
            'First_Name': 'first_name',
            'Last_Name': 'last_name',
            'Email': 'email',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Zipcode': 'zip',
            'Phone_Number': 'phone',
            'Phone_Number_2': 'phone2',
            'Phone_Number_3': 'phone3',
            'credit_score': 'credit_score',
            'current_balance': 'mortgage_balance',
            'current_rate': 'mortgage_rate',
            # New field mappings
            'property_value': 'property_value',
            'additional_cash': 'additional_cash',
            'cash_out': 'cash_out',
            'loan_type': 'loan_type',
            'loan_purpose': 'loan_purpose',
            'property_description': 'property_description',
            'second_mortgage': 'second_mortgage',
            'second_balance': 'second_balance',
            'second_rate': 'second_rate',
            'found_home': 'found_home',
            'down_payment': 'down_payment',
            'property_purpose': 'property_purpose',
            'ltv': 'ltv',
            'bid_loan_value': 'bid_loan_value',
            'va_eligible': 'va_eligible'
        }
        
        # Define field types for special handling
        numeric_fields = [
            'mortgage_balance', 'mortgage_rate', 'credit_score',
            'property_value', 'additional_cash', 'second_balance',
            'second_rate', 'down_payment', 'ltv', 'bid_loan_value'
        ]
        boolean_fields = ['cash_out', 'found_home', 'va_eligible']
        
        for orig_col, new_col in field_mapping.items():
            if orig_col in df.columns:
                # Get the value and handle null values
                normalized[new_col] = df[orig_col].fillna('')
                
                # Apply name case formatting for name fields
                if new_col in ['first_name', 'last_name']:
                    normalized[new_col] = normalized[new_col].astype(str).str.strip().str.title()
                
                # Format numeric fields
                elif new_col in numeric_fields:
                    normalized[new_col] = pd.to_numeric(normalized[new_col], errors='coerce').fillna(0)
                
                # Handle boolean fields
                elif new_col in boolean_fields:
                    normalized[new_col] = normalized[new_col].apply(self._convert_to_boolean)
                
                # Special handling for loan_type
                elif new_col == 'loan_type':
                    normalized[new_col] = normalized[new_col].fillna('').astype(str).str.strip().str.upper()
                
                # Handle all phone numbers with improved formatting
                elif new_col in ['phone', 'phone2', 'phone3']:
                    normalized[new_col] = df[orig_col].apply(self._format_phone)
                
                # Clean and validate email
                elif new_col == 'email':
                    normalized[new_col] = normalized[new_col].fillna('').astype(str).str.strip().str.lower()
                
                # Clean address fields
                elif new_col in ['address', 'city', 'property_description', 'property_purpose']:
                    normalized[new_col] = normalized[new_col].fillna('').astype(str)
                    normalized[new_col] = normalized[new_col].str.strip().str.title()
                
                # Format state codes to uppercase
                elif new_col == 'state':
                    normalized[new_col] = normalized[new_col].fillna('').astype(str)
                    normalized[new_col] = normalized[new_col].str.strip().str.upper()
                
                # Clean zip codes
                elif new_col == 'zip':
                    normalized[new_col] = normalized[new_col].fillna('').astype(str)
                    normalized[new_col] = normalized[new_col].str.strip()
                    # Take first 5 digits only if present
                    normalized[new_col] = normalized[new_col].str[:5]
        
        return normalized

# Liberty 1 Lending ETL System

## Overview
A Streamlit-based ETL system that processes mortgage leads from multiple sources (Experian, TransUnion, LeadSource) into a normalized format and sends to Bonzo via webhook.

## Features
- Multi-source lead processing (Experian, TransUnion, LeadSource)
- Data normalization and standardization
- Real-time webhook integration with Bonzo
- Error tracking and failed record exports
- PostgreSQL logging and analytics
- Professional UI with Liberty 1 Lending branding

## Source-Specific Implementations

### TransUnion Parser
- First_Name → contact.first_name
- Last_Name → contact.last_name
- Phone_Number → contact.primary_phone
- FICO04 Score → loan.credit_score
- Current Balance of Most Recent Mortgage → loan.current_balance
- Monthly Payment Amount → loan.monthly_payment
- Open Date → loan.start_date

### Experian Parser
- First Name → contact.first_name
- Surname → contact.last_name
- Telephone # 1 → contact.primary_phone
- Telephone # 2 → contact.alt_phone_1
- Telephone # 3 → contact.alt_phone_2
- FICO_V30A_PSCRN_SCORE_VALUE → loan.credit_score
- Street number + Street name → property.street_address

### LeadSource Parser
- First Name → contact.first_name
- Last Name → contact.last_name
- Pri. Phone → contact.primary_phone
- Sec. Phone → contact.alt_phone_1
- Est. Home Value → property.value
- Credit Grade → loan.credit_score
- ADD_CASH → loan.additional_cash
- Cash Out → loan.cash_out
- Loan Type → loan.program
- Loan Purpose → loan.loan_purpose
- BAL_ONE → loan.current_balance
- MTG_ONE_INT → loan.current_rate
- MTG_TWO → loan.second_mortgage
- BAL_TWO → loan.second_balance
- MTG_TWO_INT → loan.second_rate
- Found Home → loan.found_home
- DOWN_PMT → loan.down_payment
- Property Purpose → loan.property_purpose
- LTV → loan.ltv
- bid_loan_val → loan.bid_loan_value
- VA Eligible → loan.va_eligible

## Webhook Integration

### Payload Structure
```json
{
    "contact": {
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "primary_phone": "string",
        "alt_phone_1": "string",
        "alt_phone_2": "string"
    },
    "property": {
        "street_address": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "value": "number"
    },
    "loan": {
        "credit_score": "number",
        "current_balance": "number",
        "current_rate": "number",
        "second_mortgage": "boolean",
        "second_balance": "number",
        "second_rate": "number",
        "additional_cash": "number",
        "cash_out": "boolean",
        "found_home": "boolean",
        "down_payment": "number",
        "ltv": "number"
    },
    "lead": {
        "source": "string",
        "original_id": "string"
    }
}
```

## Data Processing Rules
1. Phone numbers are cleaned to 10 digits
2. State codes normalized to uppercase
3. Names converted to title case
4. Addresses standardized and combined
5. Credit scores converted to integers
6. Boolean fields properly typed (cash_out, found_home, etc.)
7. Currency values converted to floats
8. Required fields validation (email OR phone)

## Error Handling
- Failed records are tracked and exportable
- Each record shows specific validation error
- Database logging of all webhook responses
- Source-specific parsing error handling

## Database Structure
See POSTGRES_GUIDE.md for detailed database implementation

## Deployment
Deploy as a web service on Replit:
1. Use 'Web Service' deployment type
2. Set run command: streamlit run main.py
3. Configure environment variables:
   - PGHOST
   - PGDATABASE
   - PGUSER
   - PGPASSWORD
   - PGPORT

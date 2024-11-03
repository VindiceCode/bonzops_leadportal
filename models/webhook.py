import requests
import json
from config import BONZO_WEBHOOK_URL

class WebhookError(Exception):
    """Custom exception for webhook-related errors"""
    pass

class WebhookSender:
    def __init__(self, database):
        self.db = database

    def prepare_payload(self, lead_data):
        """Convert normalized lead data to Bonzo webhook format"""
        try:
            # Get primary phone, or use first available alternate if primary is missing
            primary_phone = lead_data.get('phone')
            if not primary_phone:
                primary_phone = lead_data.get('phone2') or lead_data.get('phone3')
            
            # Determine which numbers to use for alternates
            alt_phones = []
            for phone_field in ['phone', 'phone2', 'phone3']:
                phone = lead_data.get(phone_field)
                if phone and phone != primary_phone:
                    alt_phones.append(phone)
            
            # Validate required fields
            if not lead_data.get('email') and not primary_phone:
                raise WebhookError("Either email or phone is required")
            
            return {
                "contact": {
                    "first_name": lead_data.get('first_name'),
                    "last_name": lead_data.get('last_name'),
                    "email": lead_data.get('email'),
                    "primary_phone": primary_phone,
                    "alt_phone_1": alt_phones[0] if len(alt_phones) > 0 else None,
                    "alt_phone_2": alt_phones[1] if len(alt_phones) > 1 else None
                },
                "property": {
                    "street_address": lead_data.get('address'),
                    "city": lead_data.get('city'),
                    "state": lead_data.get('state'),
                    "zip": lead_data.get('zip'),
                    "value": lead_data.get('property_value'),
                    "description": lead_data.get('property_description'),
                    "purpose": lead_data.get('property_purpose')
                },
                "loan": {
                    "credit_score": lead_data.get('credit_score'),
                    "current_balance": lead_data.get('mortgage_balance'),
                    "current_rate": lead_data.get('mortgage_rate'),
                    "second_mortgage": lead_data.get('second_mortgage'),
                    "second_balance": lead_data.get('second_balance'),
                    "second_rate": lead_data.get('second_rate'),
                    "additional_cash": lead_data.get('additional_cash'),
                    "cash_out": lead_data.get('cash_out'),
                    "loan_purpose": lead_data.get('loan_purpose'),
                    "found_home": lead_data.get('found_home'),
                    "down_payment": lead_data.get('down_payment'),
                    "ltv": lead_data.get('ltv'),
                    "bid_loan_value": lead_data.get('bid_loan_value'),
                    "va_eligible": lead_data.get('va_eligible')
                },
                "lead": {
                    "source": lead_data.get('lead_source'),
                    "original_id": lead_data.get('lead_id')
                }
            }
        except Exception as e:
            raise WebhookError(f"Error preparing payload: {str(e)}")

    def send(self, lead_data):
        """Send lead data to Bonzo webhook"""
        try:
            payload = self.prepare_payload(lead_data)
            
            response = requests.post(
                BONZO_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Check for specific HTTP error codes
            if response.status_code == 400:
                error_msg = "Invalid payload format"
            elif response.status_code == 401:
                error_msg = "Authentication failed"
            elif response.status_code == 403:
                error_msg = "Access forbidden"
            elif response.status_code == 404:
                error_msg = "Webhook endpoint not found"
            elif response.status_code == 429:
                error_msg = "Rate limit exceeded"
            elif response.status_code >= 500:
                error_msg = "Bonzo server error"
            else:
                error_msg = response.text
            
            self.db.log_webhook_response(
                lead_data.get('lead_id'),
                json.dumps(payload),
                response.status_code,
                error_msg if response.status_code != 200 else response.text
            )
            
            if response.status_code != 200:
                raise WebhookError(f"HTTP {response.status_code}: {error_msg}")
            
            return True
            
        except requests.Timeout:
            error_msg = "Request timed out after 10 seconds"
            self.db.log_webhook_response(
                lead_data.get('lead_id'),
                json.dumps(payload),
                408,
                error_msg
            )
            raise WebhookError(error_msg)
            
        except requests.ConnectionError:
            error_msg = "Failed to connect to Bonzo server"
            self.db.log_webhook_response(
                lead_data.get('lead_id'),
                json.dumps(payload),
                503,
                error_msg
            )
            raise WebhookError(error_msg)
            
        except WebhookError:
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.db.log_webhook_response(
                lead_data.get('lead_id'),
                json.dumps(payload) if 'payload' in locals() else "",
                500,
                error_msg
            )
            raise WebhookError(error_msg)

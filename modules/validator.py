import re
from datetime import datetime
from config.invoice_config import InvoiceConfig

class DataValidator:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_vat_number(vat_number):
        """Validate UAE VAT number format"""
        pattern = r'^\d{15}$'
        return bool(re.match(pattern, vat_number))

    @staticmethod
    def validate_invoice_number(invoice_number):
        """Validate invoice number format (VREB followed by numbers)"""
        pattern = r'^VREB\d{4}$'
        return bool(re.match(pattern, invoice_number))

    @staticmethod
    def validate_amount(amount):
        """Validate amount is positive number"""
        try:
            return float(amount) > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_date_format(date_str):
        """Validate date format (DD/MM/YYYY)"""
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_workflow_state(workflow_state_dict):
        """Validate workflow state data"""
        errors = []
        
        print("\n\nDebug - Validating workflow state:", workflow_state_dict)
        # Customer data validation
        customer = workflow_state_dict.get('customer', {})
        
        # Required fields validation
        required_customer_fields = {
            'invoice_number': 'Invoice number',
            'bill_to_party_name': 'Bill to party name',
            'bill_to_party_email': 'Bill to party email',
            'bill_to_party_address_1': 'Bill to party address line 1',
            'bill_to_party_address_2': 'Bill to party address line 2',
            'bill_to_party_trn': 'Bill to party TRN',
            'tenant_name': 'Tenant name'
        }

        for field, display_name in required_customer_fields.items():
            if not customer.get(field):
                errors.append(f"{display_name} is required")

        # Invoice number format validation
        if customer.get('invoice_number'):
            if not DataValidator.validate_invoice_number(customer['invoice_number']):
                errors.append("Invalid invoice number format (should be VREB followed by 4 digits)")

        # Email format validation
        if customer.get('bill_to_party_email'):
            if not DataValidator.validate_email(customer['bill_to_party_email']):
                errors.append("Invalid email format")

        # TRN validation
        if customer.get('bill_to_party_trn'):
            if not DataValidator.validate_vat_number(customer['bill_to_party_trn']):
                errors.append("Invalid TRN format (should be 15 digits)")

        # Invoice data validation
        invoice = workflow_state_dict.get('invoice', {})
        required_invoice_fields = {
            'invoice_date': 'Invoice date',
            'property_name': 'Property name',
            'rental_price': 'Rental price',
            'commission_rate': 'Commission rate',
            'tax_amount': 'Tax amount',
            'total_amount': 'Total amount'
        }

        for field, display_name in required_invoice_fields.items():
            if not invoice.get(field):
                errors.append(f"{display_name} is required")

        # # Amount validations
        # if invoice.get('rental_price'):
        #     if not DataValidator.validate_amount(invoice['rental_price']):
        #         errors.append("Rental price must be a positive number")

        # if invoice.get('commission_rate'):
        #     if not DataValidator.validate_amount(invoice['commission_rate']):
        #         errors.append("Commission rate must be a positive number")

        # # Tax calculation validation
        # if invoice.get('commission_rate') and invoice.get('tax_amount'):
        #     expected_tax = float(invoice['commission_rate']) * InvoiceConfig.VAT_RATE
        #     if abs(float(invoice['tax_amount']) - expected_tax) > 0.01:  # Allow small floating point differences
        #         errors.append("Tax amount does not match the expected value (5% of commission)")

        # # Total amount validation
        # if invoice.get('commission_rate') and invoice.get('tax_amount') and invoice.get('total_amount'):
        #     expected_total = float(invoice['commission_rate']) + float(invoice['tax_amount'])
        #     if abs(float(invoice['total_amount']) - expected_total) > 0.01:
        #         errors.append("Total amount does not match commission plus tax")

        # Date format validation
        if invoice.get('invoice_date'):
            if not DataValidator.validate_date_format(invoice['invoice_date']):
                errors.append("Invalid invoice date format (should be DD/MM/YYYY)")

        return errors if errors else None

    @staticmethod
    def calculate_tax_and_total(commission_rate):
        """Calculate tax and total amount based on commission rate"""
        tax_amount = float(commission_rate) * InvoiceConfig.VAT_RATE
        total_amount = float(commission_rate) + tax_amount
        return {
            'tax_amount': tax_amount,
            'total_amount': total_amount
        }
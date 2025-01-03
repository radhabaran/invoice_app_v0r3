# validator.py
import re
from datetime import datetime

class DataValidator:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


    @staticmethod
    def validate_workflow_state(workflow_state_dict):
        """Validate workflow state data"""
        errors = []
        
        # Customer data validation
        customer = workflow_state_dict.get('customer', {})
        if not customer.get('cust_unique_id'):
            errors.append("Customer ID is required")
        if not customer.get('cust_tax_id'):
            errors.append("Tax ID is required")
        if not customer.get('cust_email'):
            errors.append("Email is required")
        elif not DataValidator.validate_email(customer['cust_email']):
            errors.append("Invalid email format")

        # Invoice data validation
        invoice = workflow_state_dict.get('invoice', {})
        if not invoice.get('billed_amount'):
            errors.append("Billed amount is required")
        else:
            try:
                if float(invoice['billed_amount']) <= 0:
                    errors.append("Billed amount must be positive")
            except ValueError:
                errors.append("Invalid billed amount")

        if not invoice.get('currency'):
            errors.append("Currency is required")

        return errors if errors else None
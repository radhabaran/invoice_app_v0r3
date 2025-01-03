import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import os
from config.invoice_config import InvoiceConfig

class DataManager:
    def __init__(self):
        self.csv_file = InvoiceConfig.INVOICE_DATA_FILE
        self.ensure_data_file()


    def ensure_data_file(self):
        """Create data file if it doesn't exist"""
        if not os.path.exists('data'):
            os.makedirs('data')
        
        if not os.path.exists(self.csv_file):
            columns = [
                'invoice_number',
                'bill_to_party_name',
                'bill_to_party_email',
                'bill_to_party_address_1',
                'bill_to_party_address_2',
                'bill_to_party_trn',
                'tenant_name',
                'invoice_date',
                'property_name',
                'rental_price',
                'commission_rate',
                'tax_amount',
                'total_amount',
                'status',
                'payment_date',
                'terms',
                'vat_rate',
                'created_at',
                'updated_at'
            ]
            # Create initial DataFrame with default values from config
            df = pd.DataFrame(columns=columns)
            df['terms'] = InvoiceConfig.TERMS
            df['vat_rate'] = InvoiceConfig.VAT_RATE
            df.to_csv(self.csv_file, index=False)

        # Create PDF directory if it doesn't exist
        if not os.path.exists(InvoiceConfig.INVOICE_PDF_DIR):
            os.makedirs(InvoiceConfig.INVOICE_PDF_DIR)


    def get_invoice(self, invoice_number: str, workflow_state_class) -> Optional['workflow_state_class']:
        """
        Retrieve invoice information by invoice number
        Returns WorkflowState if found, None if not found
        """
        try:
            df = pd.read_csv(self.csv_file)
            invoice_data = df[df['invoice_number'] == invoice_number]
        
            if invoice_data.empty:
                return None
        
            latest_record = invoice_data.iloc[-1]
        
            return workflow_state_class(
                customer={
                    'invoice_number': latest_record['invoice_number'],
                    'bill_to_party_name': latest_record['bill_to_party_name'],
                    'bill_to_party_email': latest_record['bill_to_party_email'],
                    'bill_to_party_address_1': latest_record['bill_to_party_address_1'],
                    'bill_to_party_address_2': latest_record['bill_to_party_address_2'],
                    'bill_to_party_trn': latest_record['bill_to_party_trn'],
                    'tenant_name': latest_record['tenant_name']
                },
                invoice={
                    'invoice_date': latest_record['invoice_date'],
                    'property_name': latest_record['property_name'],
                    'rental_price': float(latest_record['rental_price']),
                    'commission_rate': float(latest_record['commission_rate']),
                    'tax_amount': float(latest_record['tax_amount']),
                    'total_amount': float(latest_record['total_amount']),
                    'status': latest_record['status'],
                    'payment_date': latest_record['payment_date'],
                    'terms': latest_record.get('terms', InvoiceConfig.TERMS),
                    'vat_rate': float(latest_record.get('vat_rate', InvoiceConfig.VAT_RATE))
                },
                company={
                    'name': InvoiceConfig.COMPANY_NAME,
                    'address': InvoiceConfig.COMPANY_ADDRESS,
                    'city': InvoiceConfig.COMPANY_CITY,
                    'website': InvoiceConfig.COMPANY_WEBSITE,
                    'phone': InvoiceConfig.COMPANY_PHONE,
                    'email': InvoiceConfig.COMPANY_EMAIL,
                    'vat': InvoiceConfig.COMPANY_VAT
                },
                bank={
                    'account_name': InvoiceConfig.BANK_ACCOUNT_NAME,
                    'account_number': InvoiceConfig.BANK_ACCOUNT_NUMBER,
                    'iban': InvoiceConfig.BANK_IBAN,
                    'swift': InvoiceConfig.BANK_SWIFT,
                    'branch': InvoiceConfig.BANK_BRANCH
                }
            )
        except Exception as e:
            raise Exception(f"Error retrieving invoice data: {str(e)}")


    def save_record(self, workflow_state_dict: Dict[str, Any]):
        """Save new record to CSV"""
        try:
            df = pd.read_csv(self.csv_file)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            record = {
                'invoice_number': workflow_state_dict['customer']['invoice_number'],
                'bill_to_party_name': workflow_state_dict['customer']['bill_to_party_name'],
                'bill_to_party_email': workflow_state_dict['customer']['bill_to_party_email'],
                'bill_to_party_address_1': workflow_state_dict['customer']['bill_to_party_address_1'],
                'bill_to_party_address_2': workflow_state_dict['customer']['bill_to_party_address_2'],
                'bill_to_party_trn': workflow_state_dict['customer']['bill_to_party_trn'],
                'tenant_name': workflow_state_dict['customer']['tenant_name'],
                'invoice_date': workflow_state_dict['invoice']['invoice_date'],
                'property_name': workflow_state_dict['invoice']['property_name'],
                'rental_price': workflow_state_dict['invoice']['rental_price'],
                'commission_rate': workflow_state_dict['invoice']['commission_rate'],
                'tax_amount': workflow_state_dict['invoice']['tax_amount'],
                'total_amount': workflow_state_dict['invoice']['total_amount'],
                'status': workflow_state_dict['invoice']['status'],
                'payment_date': workflow_state_dict['invoice'].get('payment_date', ''),
                'terms': InvoiceConfig.TERMS,
                'vat_rate': InvoiceConfig.VAT_RATE,
                'created_at': now,
                'updated_at': now
            }

            if workflow_state_dict['customer']['invoice_number'] in df['invoice_number'].values:
                df.loc[df['invoice_number'] == workflow_state_dict['customer']['invoice_number']] = record
                df.loc[df['invoice_number'] == workflow_state_dict['customer']['invoice_number'], 'updated_at'] = now
            else:
                df.loc[len(df)] = record

            df.to_csv(self.csv_file, index=False)
            return self.create_workflow_state(record)

        except Exception as e:
            raise Exception(f"Error saving record: {str(e)}")


    def create_workflow_state(self, record: Dict[str, Any]) -> Any:
        """Create workflow state from record"""
        return type('WorkflowState', (), {
            'customer': {
                'invoice_number': record['invoice_number'],
                'bill_to_party_name': record['bill_to_party_name'],
                'bill_to_party_email': record['bill_to_party_email'],
                'bill_to_party_address_1': record['bill_to_party_address_1'],
                'bill_to_party_address_2': record['bill_to_party_address_2'],
                'bill_to_party_trn': record['bill_to_party_trn'],
                'tenant_name': record['tenant_name']
            },
            'invoice': {
                'invoice_date': record['invoice_date'],
                'property_name': record['property_name'],
                'rental_price': float(record['rental_price']),
                'commission_rate': float(record['commission_rate']),
                'tax_amount': float(record['tax_amount']),
                'total_amount': float(record['total_amount']),
                'status': record['status'],
                'payment_date': record['payment_date'],
                'terms': record.get('terms', InvoiceConfig.TERMS),
                'vat_rate': float(record.get('vat_rate', InvoiceConfig.VAT_RATE))
            },
            'company': {
                'name': InvoiceConfig.COMPANY_NAME,
                'address': InvoiceConfig.COMPANY_ADDRESS,
                'city': InvoiceConfig.COMPANY_CITY,
                'website': InvoiceConfig.COMPANY_WEBSITE,
                'phone': InvoiceConfig.COMPANY_PHONE,
                'email': InvoiceConfig.COMPANY_EMAIL,
                'vat': InvoiceConfig.COMPANY_VAT
            },
            'bank': {
                'account_name': InvoiceConfig.BANK_ACCOUNT_NAME,
                'account_number': InvoiceConfig.BANK_ACCOUNT_NUMBER,
                'iban': InvoiceConfig.BANK_IBAN,
                'swift': InvoiceConfig.BANK_SWIFT,
                'branch': InvoiceConfig.BANK_BRANCH
            },
            'completed': True
        })


    def get_all_records(self):
        """Retrieve all records"""
        try:
            return pd.read_csv(self.csv_file)
        except Exception as e:
            raise Exception(f"Error retrieving records: {str(e)}")


    def update_invoice_status(self, invoice_number: str, status: str):
        """Update invoice status"""
        try:
            df = pd.read_csv(self.csv_file)
            df.loc[df['invoice_number'] == invoice_number, 'status'] = status
            df.loc[df['invoice_number'] == invoice_number, 'updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.to_csv(self.csv_file, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error updating invoice status: {str(e)}")
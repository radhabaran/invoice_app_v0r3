# invoice_config.py

class InvoiceConfig:
    # Company Details (Static)
    COMPANY_NAME = "VIHAAN REAL ESTATE BROKERAGE"
    COMPANY_ADDRESS = "Office No MO6, Al Jawhara building, Mankhool"
    COMPANY_CITY = "Dubai, UAE"
    COMPANY_WEBSITE = "www.vrebuae.uae"
    COMPANY_PHONE = "+971 567 276363"
    COMPANY_EMAIL = "customerservice@vrebuae.com"
    COMPANY_VAT = "104070763800003"
    
    # Bank Details (Static)
    BANK_ACCOUNT_NAME = "VIHAAN REAL ESTATE BROKERAGE"
    BANK_ACCOUNT_NUMBER = "9758567498"
    BANK_IBAN = "AE220860000009758567498"
    BANK_SWIFT = "WIOBAEADXXX"
    BANK_BRANCH = "Jebel Ali, Dubai"
    
    # Invoice Terms (Static)
    TERMS = "Due on Receipt"
    BALANCE_DUE_TERMS = "Immediate"
    
    # Tax Rate (Static)
    VAT_RATE = 0.05
    VAT_LABEL = "Standard Rate (5%)"
    
    # Footer (Static)
    FOOTER_NOTE = "Thank you for your Business"
    
    # File paths
    INVOICE_DATA_FILE = "data/invoices.csv"
    INVOICE_PDF_DIR = "pdfs/invoices"
    
    # Invoice Headers/Labels (Static)
    HEADERS = {
        'TITLE': 'TAX INVOICE',
        'BALANCE_DUE': 'Balance Due:',
        'BALANCE_DUE_DATE': 'Balance Due Date:',
        'BILL_TO': 'Bill To',
        'TERMS': 'Terms:',
        'TRN': 'TRN:',
        'BANK_DETAILS': 'Bank Details:',
        'TAX_SUMMARY': 'TAX Summary',
        'NOTES': 'Notes'
    }
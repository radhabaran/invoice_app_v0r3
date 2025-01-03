from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config.invoice_config import InvoiceConfig
import os

class InvoiceGenerator:
    def __init__(self):
        self.invoice_dir = InvoiceConfig.INVOICE_PDF_DIR
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)


    def format_currency(self, amount):
        """Format currency with thousands separator and AED"""
        return f"AED {amount:,.2f}/-"


    def generate_invoice(self, workflow_state_dict):
        """Generate PDF invoice"""
        invoice_number = workflow_state_dict['customer']['invoice_number']
        filename = f"{self.invoice_dir}/{invoice_number}.pdf"
        
        # Create canvas
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Company Header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height-50, InvoiceConfig.COMPANY_NAME)
        c.setFont("Helvetica", 9)
        company_address = f"{InvoiceConfig.COMPANY_ADDRESS}, {InvoiceConfig.COMPANY_CITY}"
        c.drawString(50, height-65, company_address)
        contact_info = f"{InvoiceConfig.COMPANY_WEBSITE} {InvoiceConfig.COMPANY_PHONE}"
        c.drawString(50, height-80, contact_info)

        # Invoice Title and Number
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height-110, InvoiceConfig.HEADERS['TITLE'])
        c.setFont("Helvetica", 10)
        c.drawString(50, height-125, f"#{invoice_number}")
        c.drawString(width-200, height-125, f"Invoice Date:{workflow_state_dict['invoice']['invoice_date']}")

        # Company Details Block
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height-155, InvoiceConfig.COMPANY_NAME)
        c.setFont("Helvetica", 9)
        c.drawString(50, height-170, InvoiceConfig.COMPANY_ADDRESS)
        c.drawString(50, height-185, f"{InvoiceConfig.COMPANY_CITY}")
        c.drawString(50, height-200, InvoiceConfig.COMPANY_EMAIL)
        c.drawString(50, height-215, f"VAT No: {InvoiceConfig.COMPANY_VAT}")

        # Balance Due
        c.setFont("Helvetica-Bold", 10)
        balance_due = self.format_currency(workflow_state_dict['invoice']['total_amount'])
        c.drawString(width-200, height-155, f"{InvoiceConfig.HEADERS['BALANCE_DUE']} {balance_due}")

        # Bill To Section
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height-245, InvoiceConfig.HEADERS['BILL_TO'])
        c.setFont("Helvetica", 9)
        c.drawString(50, height-260, workflow_state_dict['customer']['bill_to_party_name'])
        c.drawString(50, height-275, workflow_state_dict['customer']['bill_to_party_address_1'])
        c.drawString(50, height-290, workflow_state_dict['customer']['bill_to_party_address_2'])

        # Terms and TRN
        c.drawString(width-200, height-245, f"{InvoiceConfig.HEADERS['TERMS']} {InvoiceConfig.TERMS}")
        c.drawString(width-200, height-260, f"{InvoiceConfig.HEADERS['TRN']} {workflow_state_dict['customer']['bill_to_party_trn']}")

        # Items Table
        c.setFont("Helvetica-Bold", 9)
        y = height-330
        c.drawString(50, y, "# Items & Description")
        c.drawString(350, y, "QTY")
        c.drawString(400, y, "RATE")
        c.drawString(470, y, "TAX @5%")
        c.drawString(530, y, "Amount")

        # Item Details
        y -= 20
        c.setFont("Helvetica", 9)
        c.drawString(50, y, "1. Rent Commission")
        c.drawString(50, y-15, f"Villa Name: {workflow_state_dict['invoice']['property_name']}")
        c.drawString(50, y-30, f"Client Name: {workflow_state_dict['customer']['tenant_name']}")
        rental_price = self.format_currency(workflow_state_dict['invoice']['rental_price'])
        c.drawString(50, y-45, f"Rental Price: {rental_price}")

        c.drawString(350, y, "1.00")
        commission = workflow_state_dict['invoice']['commission_rate']
        tax = workflow_state_dict['invoice']['tax_amount']
        total = workflow_state_dict['invoice']['total_amount']
        
        c.drawString(400, y, self.format_currency(commission))
        c.drawString(470, y, self.format_currency(tax))
        c.drawString(530, y, self.format_currency(total))

        # Bank Details
        y = height-500
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, InvoiceConfig.HEADERS['BANK_DETAILS'])
        c.setFont("Helvetica", 9)
        c.drawString(50, y-15, f"Account Name: {InvoiceConfig.BANK_ACCOUNT_NAME}")
        c.drawString(50, y-30, f"Account Number: {InvoiceConfig.BANK_ACCOUNT_NUMBER}")
        c.drawString(50, y-45, f"IBAN: {InvoiceConfig.BANK_IBAN}")
        c.drawString(50, y-60, f"Swift Code: {InvoiceConfig.BANK_SWIFT}")
        c.drawString(50, y-75, f"Branch: {InvoiceConfig.BANK_BRANCH}")

        # Tax Summary
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y-105, InvoiceConfig.HEADERS['TAX_SUMMARY'])
        c.setFont("Helvetica", 9)
        c.drawString(50, y-120, "TAX details")
        c.drawString(200, y-120, "Taxable Amount (AED)")
        c.drawString(350, y-120, "TAX Amount (AED)")
        c.drawString(50, y-135, InvoiceConfig.VAT_LABEL)
        c.drawString(200, y-135, self.format_currency(commission))
        c.drawString(350, y-135, self.format_currency(tax))

        # Footer
        c.setFont("Helvetica", 9)
        c.drawString(50, y-165, InvoiceConfig.HEADERS['NOTES'])
        c.drawString(50, y-180, InvoiceConfig.FOOTER_NOTE)

        c.save()
        return filename
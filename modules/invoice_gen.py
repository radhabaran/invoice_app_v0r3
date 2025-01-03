from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config.invoice_config import InvoiceConfig
import os
from datetime import datetime

class InvoiceGenerator:
    def __init__(self):
        self.invoice_dir = InvoiceConfig.INVOICE_PDF_DIR
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)

    def format_currency(self, amount):
        """Format currency with AED prefix, thousands separator and /- suffix"""
        if isinstance(amount, str):
            amount = float(amount.replace(',', ''))
        return f"AED {amount:,.2f}/-"

    def format_number(self, amount):
        """Format number with thousands separator and /- suffix, no currency prefix"""
        if isinstance(amount, str):
            amount = float(amount.replace(',', ''))
        return f"{amount:,.2f}/-"

    def draw_bordered_box(self, c, x, y, width, height, stroke_color=colors.black):
        """Draw a box with specified border"""
        c.setStrokeColor(stroke_color)
        c.setLineWidth(0.5)
        c.rect(x, y, width, height)

    def generate_invoice(self, workflow_state_dict):
        """Generate PDF invoice"""
        invoice_number = workflow_state_dict['customer']['invoice_number']
        filename = f"{self.invoice_dir}/{invoice_number}.pdf"
        
        # Create canvas with A4 size
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Adjusted margins
        left_margin = 20 * mm
        right_margin = width - (20 * mm)
        top_margin = height - (20 * mm)
        
        # Company Logo (Two lines)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, top_margin, "VIHAAN")
        c.setFont("Helvetica", 8)
        c.drawString(left_margin, top_margin - 12, "REAL ESTATE BROKERAGE")
        
        # Contact info
        c.setFont("Helvetica", 9)
        address_text = f"{InvoiceConfig.COMPANY_ADDRESS}, {InvoiceConfig.COMPANY_CITY}"
        c.drawString(left_margin, top_margin - 24, address_text)
        contact_info = f"{InvoiceConfig.COMPANY_WEBSITE} {InvoiceConfig.COMPANY_PHONE}"
        c.drawString(left_margin, top_margin - 36, contact_info)

        # TAX INVOICE Section (Centered)
        y_position = top_margin - 60
        c.setFont("Helvetica-Bold", 12)
        text = "TAX INVOICE"
        text_width = c.stringWidth(text, "Helvetica-Bold", 12)
        center_x = (width - text_width) / 2
        c.drawString(center_x, y_position, text)

        # Invoice number and date (Right aligned)
        y_position -= 15
        c.setFont("Helvetica", 9)
        c.drawRightString(right_margin, y_position, f"#{invoice_number}")
        c.drawRightString(right_margin, y_position - 15, 
                       f"Invoice Date:{workflow_state_dict['invoice']['invoice_date']}")

        # Company Details
        y_position -= 35
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin, y_position, InvoiceConfig.COMPANY_NAME)
        
        # Balance Due (with currency)
        balance_due = self.format_currency(workflow_state_dict['invoice']['total_amount'])
        c.drawRightString(right_margin, y_position, f"Balance Due: {balance_due}")
        
        # Company details continued
        c.setFont("Helvetica", 9)
        y_position -= 15
        c.drawString(left_margin, y_position, InvoiceConfig.COMPANY_ADDRESS)
        c.drawString(left_margin, y_position - 15, InvoiceConfig.COMPANY_CITY)
        c.drawString(left_margin, y_position - 30, InvoiceConfig.COMPANY_EMAIL)
        c.drawString(left_margin, y_position - 45, f"VAT No: {InvoiceConfig.COMPANY_VAT}")

        # Bill To Section
        y_position -= 75
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin, y_position, "Bill To")
        
        # Terms, Balance Due Date, and TRN (Right aligned)
        c.setFont("Helvetica", 9)
        y_position_right = y_position
        c.drawRightString(right_margin, y_position_right, "Terms: Due on Receipt")
        c.drawRightString(right_margin, y_position_right - 15, "Balance Due Date: Immediate")
        c.drawRightString(right_margin, y_position_right - 30, 
                         f"TRN: {workflow_state_dict['customer']['bill_to_party_trn']}")

        # Bill To details
        c.setFont("Helvetica", 9)
        y_position -= 15
        c.drawString(left_margin, y_position, workflow_state_dict['customer']['bill_to_party_name'])
        c.drawString(left_margin, y_position - 15, 
                    workflow_state_dict['customer']['bill_to_party_address_1'])
        c.drawString(left_margin, y_position - 30, 
                    workflow_state_dict['customer']['bill_to_party_address_2'])

        # Items Table with box
        y_position -= 60
        table_height = 20
        table_width = right_margin - left_margin
        self.draw_bordered_box(c, left_margin, y_position - table_height, table_width, table_height)
        
        # Table headers
        c.setFont("Helvetica-Bold", 9)
        headers = [
            (left_margin + 5, "# Items & Description"),
            (left_margin + 280, "QTY"),
            (left_margin + 330, "RATE"),
            (left_margin + 400, "TAX @5%"),
            (right_margin - 40, "Amount")
        ]
        
        header_y = y_position - 15
        for x, text in headers:
            if text in ["Amount", "RATE", "TAX @5%"]:
                c.drawRightString(x, header_y, text)
            else:
                c.drawString(x, header_y, text)

        # Item details
        y_position -= 35
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 5, y_position, "1. Rent Commission")
        c.drawString(left_margin + 5, y_position - 15, 
                    f"Villa Name: {workflow_state_dict['invoice']['property_name']}")
        c.drawString(left_margin + 5, y_position - 30, 
                    f"Client Name: {workflow_state_dict['customer']['tenant_name']}")
        c.drawString(left_margin + 5, y_position - 45, 
                    f"Rental Price: {self.format_currency(workflow_state_dict['invoice']['rental_price'])}")

        # Values aligned right (without currency)
        commission = workflow_state_dict['invoice']['commission_rate']
        tax = workflow_state_dict['invoice']['tax_amount']
        total = workflow_state_dict['invoice']['total_amount']

        c.drawString(left_margin + 280, y_position, "1.00")
        c.drawRightString(left_margin + 380, y_position, self.format_number(commission))
        c.drawRightString(left_margin + 450, y_position, self.format_number(tax))
        c.drawRightString(right_margin - 40, y_position, self.format_number(total))

        # SUB Total with horizontal lines (without currency)
        y_position -= 60
        c.setLineWidth(0.5)
        
        # Draw top line
        c.line(left_margin + 350, y_position + 5, right_margin - 40, y_position + 5)
        
        # Draw SUB Total
        c.drawRightString(left_margin + 450, y_position, f"SUB Total: {self.format_number(tax)}")
        c.drawRightString(right_margin - 40, y_position, self.format_number(total))
        
        # Draw bottom line
        c.line(left_margin + 350, y_position - 5, right_margin - 40, y_position - 5)

        # Bank Details
        y_position -= 30
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin, y_position, "Bank Details:")
        c.drawRightString(right_margin - 40, y_position, f"TOTAL: {self.format_currency(total)}")  # with currency

        # Bank details
        c.setFont("Helvetica", 9)
        y_position -= 15
        bank_details = [
            f"Account Name: {InvoiceConfig.BANK_ACCOUNT_NAME}",
            f"Account Number: {InvoiceConfig.BANK_ACCOUNT_NUMBER}",
            f"IBAN: {InvoiceConfig.BANK_IBAN}",
            f"Swift Code: {InvoiceConfig.BANK_SWIFT} Branch: {InvoiceConfig.BANK_BRANCH}"
        ]
        
        for detail in bank_details:
            c.drawString(left_margin, y_position, detail)
            y_position -= 15

        # TAX Summary
        y_position -= 15
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin, y_position, "TAX Summary")
        
        # TAX table
        y_position -= 15
        c.setFont("Helvetica", 9)
        tax_headers = [
            (left_margin, "TAX details"),
            (left_margin + 200, "Taxable Amount (AED)"),
            (left_margin + 350, "TAX Amount (AED)")
        ]
        
        for x, text in tax_headers:
            c.drawString(x, y_position, text)

        # TAX details (without currency)
        y_position -= 15
        c.drawString(left_margin, y_position, "Standard Rate (5%)")
        c.drawRightString(left_margin + 300, y_position, self.format_number(commission))
        c.drawRightString(left_margin + 450, y_position, self.format_number(tax))
        
        y_position -= 15
        c.drawRightString(left_margin + 450, y_position, f"TAX SUB Total: {self.format_number(tax)}")

        # Notes
        y_position -= 30
        c.setFont("Helvetica", 9)
        c.drawString(left_margin, y_position, "Notes")
        c.drawString(left_margin, y_position - 15, "Thank you for your Business")

        c.save()
        return filename
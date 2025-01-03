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
        
        # Company Logo (Two lines only)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, top_margin, "VIHAAN")
        c.setFont("Helvetica", 8)
        c.drawString(left_margin, top_margin - 12, "REAL ESTATE BROKERAGE")

        # TAX INVOICE Section (Centered)
        y_position = top_margin - 40
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
        
        # Terms and Balance Due Date (Right aligned)
        c.setFont("Helvetica", 9)
        y_position_right = y_position
        c.drawRightString(right_margin, y_position_right - 15, "Balance Due Date: Immediate")
        c.drawRightString(right_margin, y_position_right, "Terms: Due on Receipt")
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

        # Items Table Headers
        y_position -= 60
        table_height = 20
        table_width = right_margin - left_margin
        self.draw_bordered_box(c, left_margin, y_position - table_height, table_width, table_height)
        
        # Define column positions with more spacing
        desc_col = left_margin + 5
        qty_col = left_margin + 260
        rate_col = left_margin + 330
        tax_col = left_margin + 410  # Increased spacing
        amount_col = right_margin - 10  # Pushed further right

        # Table headers
        c.setFont("Helvetica-Bold", 9)
        header_y = y_position - 15
        
        # Left aligned headers
        c.drawString(desc_col, header_y, "# Items & Description")
        
        # Right aligned headers
        c.drawRightString(qty_col, header_y, "QTY")
        c.drawRightString(rate_col, header_y, "RATE")
        c.drawRightString(tax_col, header_y, "TAX @5%")
        c.drawRightString(amount_col, header_y, "Amount")

        # Item details
        y_position -= 35
        c.setFont("Helvetica", 9)
        
        # Description column
        c.drawString(desc_col, y_position, "1. Rent Commission")
        c.drawString(desc_col, y_position - 15, 
                    f"Villa Name: {workflow_state_dict['invoice']['property_name']}")
        c.drawString(desc_col, y_position - 30, 
                    f"Client Name: {workflow_state_dict['customer']['tenant_name']}")
        c.drawString(desc_col, y_position - 45, 
                    f"Rental Price: {self.format_currency(workflow_state_dict['invoice']['rental_price'])}")

        # Values in columns (right aligned)
        commission = workflow_state_dict['invoice']['commission_rate']
        tax = workflow_state_dict['invoice']['tax_amount']
        total = workflow_state_dict['invoice']['total_amount']

        c.drawRightString(qty_col, y_position, "1.00")
        c.drawRightString(rate_col, y_position, self.format_number(commission))
        c.drawRightString(tax_col, y_position, self.format_number(tax))
        c.drawRightString(amount_col, y_position, self.format_number(total))

        # SUB Total section with increased spacing between lines
        y_position -= 60
        c.setLineWidth(0.5)
        
        # Draw top line
        c.line(left_margin, y_position + 12, right_margin, y_position + 12)
        
        # SUB Total text and values
        c.drawRightString(rate_col, y_position, "SUB Total:")  # Right-aligned under RATE
        c.drawRightString(tax_col, y_position, self.format_number(tax))
        c.drawRightString(amount_col, y_position, self.format_number(total))
        
        # Draw bottom line
        c.line(left_margin, y_position - 12, right_margin, y_position - 12)

        # Bank Details
        y_position -= 40  # Adjusted for increased spacing
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin, y_position, "Bank Details:")
        c.drawRightString(amount_col, y_position, f"TOTAL: {self.format_currency(total)}")

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

        # TAX table headers
        y_position -= 15
        header_height = 20
        header_width = right_margin - left_margin

        # Draw box around headers
        self.draw_bordered_box(c, left_margin, y_position - header_height, header_width, header_height)

        # Define tax table columns with proper spacing
        tax_detail_col = left_margin + 5
        taxable_amount_col = left_margin + 300
        tax_amount_col = tax_col

        # Draw headers in bold
        c.setFont("Helvetica-Bold", 9)
        header_y = y_position - 15
        c.drawString(tax_detail_col, header_y, "TAX details")
        c.drawString(taxable_amount_col - 100, header_y, "Taxable Amount (AED)")
        c.drawString(tax_amount_col - 40, header_y, "TAX Amount (AED)")

        # TAX details
        y_position -= 35  # Increased spacing after header box
        c.setFont("Helvetica", 9)  # Switch back to regular font
        c.drawString(tax_detail_col, y_position, "Standard Rate (5%)")
        c.drawRightString(taxable_amount_col, y_position, self.format_number(commission))
        c.drawRightString(tax_amount_col, y_position, self.format_number(tax))

        # TAX SUB Total with increased spacing and lines
        y_position -= 30  # Increased spacing before TAX SUB Total

        # Draw top line
        c.setLineWidth(0.5)
        c.line(left_margin, y_position + 12, right_margin, y_position + 12)

        # TAX SUB Total aligned under Taxable Amount
        c.drawString(taxable_amount_col - 100, y_position, "TAX SUB Total:")
        c.drawRightString(tax_amount_col, y_position, self.format_number(tax))

        # Draw bottom line
        c.line(left_margin, y_position - 12, right_margin, y_position - 12)

        # Notes
        y_position -= 30
        c.setFont("Helvetica", 9)
        c.drawString(left_margin, y_position, "Notes")
        c.drawString(left_margin, y_position - 15, "Thank you for your Business")

        c.save()
        return filename
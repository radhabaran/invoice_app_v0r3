# app.py

import streamlit as st
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
from modules.data_manager import DataManager
from modules.invoice_gen import InvoiceGenerator
from modules.email_handler import EmailHandler
from modules.workflow import WorkflowManager
from modules.validator import DataValidator
from modules.kyc_manager import KYCManager

class WorkflowState(BaseModel):
    customer: Dict[str, Any]
    invoice: Dict[str, Any]
    validation_status: Optional[Dict[str, Any]] = None
    invoice_creation_status: Optional[Dict[str, Any]] = None
    email_notification_status: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed: bool = False


class InvoiceApp:
    def __init__(self):
        if not hasattr(st.session_state, 'workflow_manager'):
            st.session_state.workflow_manager = self.init_systems()
        
        if not hasattr(st.session_state, 'state'):
            st.session_state.state = WorkflowState(
                customer={
                    'invoice_number': '',
                    'bill_to_party_name': '',
                    'bill_to_party_email': '',
                    'bill_to_party_address_1': '',
                    'bill_to_party_address_2': '',
                    'bill_to_party_trn': '',
                    'tenant_name': ''
                },
                invoice={
                    'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                    'property_name': '',
                    'rental_price': 0.0,
                    'commission_rate': 0.0,
                    'tax_amount': 0.0,
                    'total_amount': 0.0,
                    'status': 'Pending',
                    'payment_date': ''
                }
            )
        
        self.kyc_manager = KYCManager()
        self.workflow_manager = st.session_state.workflow_manager
        self.validator = DataValidator()
        self.state = st.session_state.state


    @staticmethod
    def init_systems():
        try:
            data_manager = DataManager()
            invoice_generator = InvoiceGenerator()
            email_handler = EmailHandler()
            return WorkflowManager(data_manager, invoice_generator, email_handler, WorkflowState)
        except Exception as e:
            st.error(f"System initialization failed: {str(e)}")
            return None


    def update_state(self, invoice_number: str, bill_to_party_name: str, 
                bill_to_party_email: str,
                bill_to_party_address_1: str, bill_to_party_address_2: str,
                bill_to_party_trn: str, tenant_name: str, **kwargs):
        """Update state with new data"""
        now = datetime.now()
    
        self.state.customer.update({
            'invoice_number': invoice_number,
            'bill_to_party_name': bill_to_party_name,
            'bill_to_party_email': bill_to_party_email,
            'bill_to_party_address_1': bill_to_party_address_1,
            'bill_to_party_address_2': bill_to_party_address_2,
            'bill_to_party_trn': bill_to_party_trn,
            'tenant_name': tenant_name
        })
    
        self.state.invoice.update({
            'invoice_date': now.strftime('%Y-%m-%d'),
            'property_name': kwargs.get('property_name', ''),
            'rental_price': kwargs.get('rental_price', 0.0),
            'commission_rate': kwargs.get('commission_rate', 0.0),
            'tax_amount': kwargs.get('tax_amount', 0.0),
            'total_amount': kwargs.get('total_amount', 0.0),
            'status': 'Pending'
        })


    def search_customer(self, invoice_number: str):
        """Search invoice and update state"""
        try:
            result = self.workflow_manager.data_manager.get_invoice(invoice_number, WorkflowState)
        
            if result:
                self.state.customer.update(result.customer)
                self.state.invoice.update(result.invoice)
                return True
        
            st.warning("Invoice not found")
            return False
    
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return False


    def handle_submit(self, **kwargs):
        """Handle form submission"""
        try:
            # Update customer data
            self.state.customer.update({
                'invoice_number': kwargs['invoice_number'],
                'bill_to_party_name': kwargs['bill_to_party_name'],
                'bill_to_party_email': kwargs['bill_to_party_email'],
                'bill_to_party_address_1': kwargs['bill_to_party_address_1'],
                'bill_to_party_address_2': kwargs['bill_to_party_address_2'],
                'bill_to_party_trn': kwargs['bill_to_party_trn'],
                'tenant_name': kwargs['tenant_name']
            })
        
            # Update invoice data
            self.state.invoice.update({
                'invoice_date': kwargs['invoice_date'],
                'property_name': kwargs['property_name'],
                'rental_price': kwargs['rental_price'],
                'commission_rate': kwargs['commission_rate'],
                'tax_amount': kwargs['tax_amount'],
                'total_amount': kwargs['total_amount'],
                'status': 'Pending',
                'payment_date': kwargs.get('payment_date', '') 
            })
        
            validation_result = self.validator.validate_workflow_state(self.state.dict())
            if validation_result is not None:
                st.error(f"Validation failed: {validation_result}")
                return

            updated_state = self.workflow_manager.data_manager.save_record(self.state.dict())

            if updated_state:
                self.state.customer.update(updated_state.customer)
                self.state.invoice.update(updated_state.invoice)
                self.state.completed = updated_state.completed
                st.success("Record saved successfully")
            else:
                st.error("Failed to save record")
                return

        except Exception as e:
            st.error(f"Submission failed: {str(e)}")


    def handle_generate_invoice(self):
        """Handle invoice generation"""
        print("\n\nDebug - Invoice number at start of generate:", self.state.customer['invoice_number'])

        if not self.state.customer['invoice_number']:
            st.error("Please submit record first")
            return

        result = self.workflow_manager.run_workflow(self.state)
        print("\n\nDebug - Workflow result:", result.dict() if result else "No result")
        if result.error:
            st.error(result.error)
        else:
            self.state = result
            st.success(f"Invoice generated successfully")


    def reset_state(self):
        """Reset the state"""
        new_state = WorkflowState(
            customer={
                'invoice_number': '',
                'bill_to_party_name': '',
                'bill_to_party_email': '',
                'bill_to_party_address_1': '',
                'bill_to_party_address_2': '',
                'bill_to_party_trn': '',
                'tenant_name': ''
            },
            invoice={
                'invoice_date': '',
                'property_name': '',
                'rental_price': 0.0,
                'commission_rate': 0.0,
                'tax_amount': 0.0,
                'total_amount': 0.0,
                'status': 'Pending',
                'payment_date': ''
            }
        )

        # Reset both instance state and session state
        self.state = new_state
        st.session_state.state = new_state

        # Clear the invoice_number input value from session state
        if 'invoice_number' in st.session_state:
            del st.session_state['invoice_number']

        st.rerun()


    def render_main_page(self):
        """Render the main UI"""
        st.title("Invoice & KYC Management System")


        # Create tabs for Invoice and KYC
        tab1, tab2 = st.tabs(["Invoice Management", "KYC Management"])

        with tab1:
            # Your existing invoice management UI code
            self.render_invoice_tab()
        
        with tab2:
            # New KYC tab
            self.kyc_manager.render_kyc_tab(
                self.state.customer.get('cust_unique_id') if self.state.customer else None
            )


    def render_invoice_tab(self):
        # Main container with custom width
        with st.container():
            # In the invoice number row
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                invoice_number = st.text_input("Invoice Number*", 
                    value=self.state.customer['invoice_number'],
                    placeholder="VREB####",
                    key='invoice_number'
                )
            # Search button in its own row
            with col2:
                # Add some vertical spacing to align with the input field
                st.write("")  # This creates a small vertical gap
                if st.button("Search", type="primary", key="search_button",
                    help="Search for invoice records",
                    use_container_width=True):
                    if invoice_number:
                        self.search_customer(invoice_number)

            # Invoice Date and Payment Due Date row
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                invoice_date = st.date_input("Invoice Date", 
                    value=datetime.now(),
                    key='invoice_date')
            with col2:
                # Payment due date is automatically set to invoice date + 30 days
                payment_due_date = st.date_input("Payment Due Date",
                    value=datetime.now() + timedelta(days=30),
                    disabled=True,
                    key='payment_due_date')

            # Bill To Party Details
            col1, col2, col3 = st.columns([0.4, 0.35, 0.25])
            with col1:
                bill_to_party_name = st.text_input("Bill To Party Name*", 
                    value=self.state.customer['bill_to_party_name'],
                    placeholder="Enter bill to party name")
            with col2:
                bill_to_party_email = st.text_input("Bill To Party Email*",  # Add this
                    value=self.state.customer['bill_to_party_email'],
                    placeholder="Enter email address")
            with col3:
                bill_to_party_trn = st.text_input("Bill To Party TRN*", 
                    value=self.state.customer['bill_to_party_trn'],
                    placeholder="Enter TRN number")

            # Bill To Party Address
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                bill_to_party_address_1 = st.text_input("Bill To Party Address Line 1*", 
                    value=self.state.customer['bill_to_party_address_1'],
                    placeholder="Building, Street")
            with col2:
                bill_to_party_address_2 = st.text_input("Bill To Party Address Line 2*", 
                    value=self.state.customer['bill_to_party_address_2'],
                    placeholder="Area, City")

            # Property and Tenant Details
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                property_name = st.text_input("Property Name*", 
                    value=self.state.invoice['property_name'],
                    placeholder="Enter property name")
            with col2:
                tenant_name = st.text_input("Tenant Name*", 
                    value=self.state.customer['tenant_name'],
                    placeholder="Enter tenant name")
                
            # Amount Details
            col1, col2, col3 = st.columns([0.33, 0.33, 0.34])
            with col1:
                rental_price = st.number_input("Rental Price (AED)*", 
                    value=float(self.state.invoice['rental_price']) if self.state.invoice['rental_price'] > 0 else 0.0,
                    step=1000.0)
            with col2:
                commission_rate = st.number_input("Commission Rate (AED)*", 
                    value=float(self.state.invoice['commission_rate']) if self.state.invoice['commission_rate'] > 0 else 0.0,
                    step=1000.0)
            with col3:
                tax_amount = st.number_input("VAT Amount (5%)", 
                    value=commission_rate * 0.05 if commission_rate > 0 else 0.0,
                    disabled=True)
                
            # Total Amount (Calculated)
            total_amount = commission_rate + tax_amount
            st.text_input("Total Amount (AED)", 
                value=f"{total_amount:,.2f}",
                disabled=True)

            # Action buttons with right alignment and blue background
            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
            with col1:
                if st.button("Submit New Record", 
                    type="primary",
                    use_container_width=True,
                    key="submit_button"):
                    try:
                        self.handle_submit(
                            invoice_number=invoice_number,
                            bill_to_party_name=bill_to_party_name,
                            bill_to_party_email=bill_to_party_email,
                            bill_to_party_address_1=bill_to_party_address_1,
                            bill_to_party_address_2=bill_to_party_address_2,
                            bill_to_party_trn=bill_to_party_trn,
                            property_name=property_name,
                            tenant_name=tenant_name,
                            rental_price=rental_price,
                            commission_rate=commission_rate,
                            tax_amount=tax_amount,
                            total_amount=total_amount,
                            invoice_date=invoice_date.strftime('%Y-%m-%d')
                        )
                    except ValueError as e:
                        st.error(f"Invalid input: {str(e)}")
        
            with col2:
                if st.button("Generate & Send Invoice",
                        type="primary",
                        use_container_width=True,
                        key="generate_button"):
                    
                    print("\n\nDebug in Generate & Send Invoice - State before generate invoice:", self.state.dict())
                    self.handle_generate_invoice()
            
            with col3:
                if st.button("🔄 Reset",
                        type="primary",
                        use_container_width=True,
                        key="reset_button"):
                        self.reset_state()

            # Current Record Display
            if self.state.customer['invoice_number']:
                st.markdown("---")
                st.subheader("Current Record")
                with st.container(border=True):
                    st.write(f"Invoice Number: {self.state.customer['invoice_number']}")
                    st.write(f"Bill To: {self.state.customer['bill_to_party_name']}")
                    st.write(f"Property: {self.state.invoice['property_name']}")
                    st.write(f"Total Amount: AED {self.state.invoice['total_amount']:,.2f}")
                    status_color = "red" if self.state.invoice['status'].lower() == "pending" else "green"
                    st.markdown(f"Status: <span style='color: {status_color}'>{self.state.invoice['status']}</span>", unsafe_allow_html=True)

                if self.state.completed:
                    with st.container():
                        st.write("✓ Record saved")
                        if self.state.invoice_creation_status:
                            st.write("✓ Invoice generated")
    def main(self):
        self.render_main_page()


def main():
    
    app = InvoiceApp()
    app.main()

if __name__ == "__main__":
    main()
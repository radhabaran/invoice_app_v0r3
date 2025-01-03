#  config/kyc_application_pdf_config.py

from dataclasses import dataclass, field
from typing import Dict, List
import os

@dataclass
class KYCApplicationPDFConfig:
    # PDF Directory
    DATA_DIR: str = "data"
    KYC_APPLICATION_PDF_DIR: str = os.path.join(DATA_DIR, "KYC_applications")
    
    # PDF Layout Settings
    PAGE_MARGIN: int = 50
    SECTION_SPACING: int = 30
    FIELD_SPACING: int = 15
    
    # Font Settings
    HEADER_FONT: str = "Helvetica-Bold"
    HEADER_SIZE: int = 16
    SECTION_FONT: str = "Helvetica-Bold"
    SECTION_SIZE: int = 12
    FIELD_FONT: str = "Helvetica"
    FIELD_SIZE: int = 10
    
    # Declaration Text
    DECLARATION_TEXT: str = (
        "I Hereby confirm that the above information provided is true and authentic "
        "on the date of this declaration. I shall notify Vihaan Real Estate in case "
        "of any changes in the above mentioned information."
    )

    # PDF Sections and Fields
    PDF_SECTIONS: List[str] = field(default_factory=lambda: [
        'CUSTOMER INFORMATION',
        'Customer Information',
        'Customer Occupation',
        'Customer Profile and Payment',
        'Declaration'
    ])
    
    PDF_FIELDS: Dict[str, List[tuple]] = field(default_factory=lambda: {
        'CUSTOMER INFORMATION': [
            ('Residential Status', 'residential_status'),
            ('Full Name (as per passport)', 'full_name'),
            ('Residential Address', 'residential_address_line1'),
            ('Residential Address', 'residential_address_line2'),
            ('Home Address', 'home_address_line1'),
            ('Home Address', 'home_address_line2'),
            ('Contact Details', 'contact_landline'),
            ('Landline Office', 'contact_office'),
            ('Mobile', 'contact_mobile')
        ],
        'Customer Information': [
            ('Gender', 'gender'),
            ('Nationality', 'nationality'),
            ('Date of Birth', 'date_of_birth'),
            ('Place Of Birth', 'place_of_birth'),
            ('Passport Number', 'passport_number'),
            ('Passport Issue Place', 'passport_issue_place'),
            ('Passport Issue Date', 'passport_issue_date'),
            ('Passport Expiry Date', 'passport_expiry_date'),
            ('Dual Nationality (if any)', 'dual_nationality'),
            ('Dual Passport Number', 'dual_passport_number'),
            ('Issue Date', 'dual_passport_issue_date'),
            ('Expiry Date', 'dual_passport_expiry_date'),
            ('Emirates ID Number', 'emirates_id'),
            ('Emirates ID Expiry Date', 'emirates_id_expiry'),
            ('Visa UID Number', 'visa_uid'),
            ('Visa Expiry Date', 'visa_expiry')
        ],
        'Customer Occupation': [
            ('Occupation', 'occupation'),
            ('Name Of the Sponsor | Business', 'sponsor_business_name'),
            ('Sponsor | Business Address', 'sponsor_business_address'),
            ('Sponsor | Business Contacts Details Landline', 'sponsor_business_landline'),
            ('Mobile', 'sponsor_business_mobile')
        ],
        'Customer Profile and Payment': [
            ('Annual Salary Income |Business Income', 'annual_income'),
            ('Purpose of Investment', 'investment_purpose'),
            ('Source of Fund', 'source_of_funds'),
            ('Payment Method', 'payment_method')
        ]
    })
    
    # PDF Headers
    PDF_TITLE: str = "KYC APPLICATION"
    PDF_SUBTITLE: str = "(To be Filled by Each Purchaser Separately)"
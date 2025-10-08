from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any
import re
from utils.security import mask_tax_id, mask_social_insurance, mask_address


class EmployeeRequest(BaseModel):
    """Request schema for creating an employee."""
    first_name: str = Field(..., min_length=1, max_length=50, description="The first name of the employee.")
    last_name: str = Field(..., min_length=1, max_length=50, description="The last name of the employee.")
    email: EmailStr = Field(..., min_length=1, max_length=50, description="The email of the employee.")
    phone: str = Field(..., min_length=1, max_length=50, description="The phone number of the employee.")
    join_date: date = Field(..., description="The date the employee joined the company.")   

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        """Validate names contain only letters and common characters."""
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", v.strip()):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return v.strip().title()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format - flexible but secure."""
        if not v:  # Allow empty phone numbers
            return v
        
        # Remove all non-digit characters to check length
        digits_only = re.sub(r'\D', '', v.strip())
        
        # Check if it's a valid length (10-15 digits)
        if not (10 <= len(digits_only) <= 15):
            raise ValueError("Phone number must be 10-15 digits")
        
        # Optional: Format US numbers nicely
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        
        return v.strip()
    
    @field_validator('join_date')
    @classmethod
    def validate_join_date(cls, v):
        """Validate join date is a valid date."""
        if not isinstance(v, date):
            raise ValueError("Join date must be a valid date")
        return v

class EmployeeResponse(BaseModel):
    """Response schema for creating an employee."""
    id: int = Field(..., description="The ID of the employee.")
    user_id: int = Field(..., description="The ID of the user who is creating the employee.")
    first_name: str = Field(..., description="The first name of the employee.")
    last_name: str = Field(..., description="The last name of the employee.")
    email: EmailStr = Field(..., description="The email of the employee.")
    phone: str = Field(..., description="The phone number of the employee.")
    join_date: date = Field(..., description="The date the employee joined the company.")
    created_at: datetime = Field(..., description="When the employee record was created.")
    updated_at: datetime = Field(..., description="When the employee record was last updated.")

# Personal Details Schemas
class EmployeePersonalDetailsRequest(BaseModel):
    """Request schema for creating/updating employee personal details."""
    gender: Optional[str] = Field(None, max_length=20, description="Employee's gender.")
    date_of_birth: Optional[date] = Field(None, description="Employee's date of birth.")
    nationality: Optional[str] = Field(None, max_length=100, description="Employee's nationality.")
    health_care_provider: Optional[str] = Field(None, max_length=255, description="Healthcare provider.")
    marital_status: Optional[str] = Field(None, max_length=20, description="Marital status.")
    personal_tax_id: Optional[str] = Field(None, max_length=50, description="Personal tax ID.")
    social_insurance_number: Optional[str] = Field(None, max_length=50, description="Social insurance number.")
    primary_address: Optional[str] = Field(None, max_length=500, description="Primary address.")
    city: Optional[str] = Field(None, max_length=100, description="City.")
    state: Optional[str] = Field(None, max_length=100, description="State.")
    country: Optional[str] = Field(None, max_length=100, description="Country.")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code.")

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is None or v == "":
            return None
        if v not in ['MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY']:
            raise ValueError("Gender must be one of: MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY")
        return v

    @field_validator('marital_status')
    @classmethod
    def validate_marital_status(cls, v):
        if v is None or v == "":
            return None
        if v not in ['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', 'SEPARATED']:
            raise ValueError("Marital status must be one of: SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED")
        return v

class EmployeePersonalDetailsResponse(BaseModel):
    """Response schema for employee personal details (with sensitive data)."""
    id: int = Field(..., description="The ID of the personal details record.")
    employee_id: int = Field(..., description="The ID of the employee.")
    gender: Optional[str] = Field(None, description="Employee's gender.")
    date_of_birth: Optional[date] = Field(None, description="Employee's date of birth.")
    nationality: Optional[str] = Field(None, description="Employee's nationality.")
    health_care_provider: Optional[str] = Field(None, description="Healthcare provider.")
    marital_status: Optional[str] = Field(None, description="Marital status.")
    personal_tax_id: Optional[str] = Field(None, description="Personal tax ID.")
    social_insurance_number: Optional[str] = Field(None, description="Social insurance number.")
    primary_address: Optional[str] = Field(None, description="Primary address.")
    city: Optional[str] = Field(None, description="City.")
    state: Optional[str] = Field(None, description="State.")
    country: Optional[str] = Field(None, description="Country.")
    postal_code: Optional[str] = Field(None, description="Postal code.")
    created_at: datetime = Field(..., description="When the record was created.")
    updated_at: datetime = Field(..., description="When the record was last updated.")


class EmployeePersonalDetailsPublicResponse(BaseModel):
    """Public response schema for employee personal details (sensitive data masked)."""
    id: int = Field(..., description="The ID of the personal details record.")
    employee_id: int = Field(..., description="The ID of the employee.")
    gender: Optional[str] = Field(None, description="Employee's gender.")
    date_of_birth: Optional[date] = Field(None, description="Employee's date of birth.")
    nationality: Optional[str] = Field(None, description="Employee's nationality.")
    health_care_provider: Optional[str] = Field(None, description="Healthcare provider.")
    marital_status: Optional[str] = Field(None, description="Marital status.")
    personal_tax_id: Optional[str] = Field(None, description="Personal tax ID (masked).")
    social_insurance_number: Optional[str] = Field(None, description="Social insurance number (masked).")
    primary_address: Optional[str] = Field(None, description="Primary address (masked).")
    city: Optional[str] = Field(None, description="City.")
    state: Optional[str] = Field(None, description="State.")
    country: Optional[str] = Field(None, description="Country.")
    postal_code: Optional[str] = Field(None, description="Postal code.")
    created_at: datetime = Field(..., description="When the record was created.")
    updated_at: datetime = Field(..., description="When the record was last updated.")

    @classmethod
    def from_full_response(cls, full_response: 'EmployeePersonalDetailsResponse') -> 'EmployeePersonalDetailsPublicResponse':
        """Create a public response from a full response with sensitive data masked."""
        return cls(
            id=full_response.id,
            employee_id=full_response.employee_id,
            gender=full_response.gender,
            date_of_birth=full_response.date_of_birth,
            nationality=full_response.nationality,
            health_care_provider=full_response.health_care_provider,
            marital_status=full_response.marital_status,
            personal_tax_id=mask_tax_id(full_response.personal_tax_id),
            social_insurance_number=mask_social_insurance(full_response.social_insurance_number),
            primary_address=mask_address(full_response.primary_address),
            city=full_response.city,
            state=full_response.state,
            country=full_response.country,
            postal_code=full_response.postal_code,
            created_at=full_response.created_at,
            updated_at=full_response.updated_at
        )

# Job Timeline Schemas
class EmployeeJobTimelineRequest(BaseModel):
    """Request schema for creating/updating employee job timeline."""
    effective_date: date = Field(..., description="Date when this job position became effective.")
    end_date: Optional[date] = Field(None, description="Date when this job position ended.")
    job_title: str = Field(..., max_length=255, description="Job title/position name.")
    position_type: Optional[str] = Field(None, max_length=50, description="Type of position.")
    employment_type: str = Field(..., max_length=50, description="Employment type.")
    line_manager_id: Optional[int] = Field(None, description="Direct manager's employee ID.")
    department: str = Field(..., max_length=100, description="Department name.")
    office: str = Field(..., max_length=100, description="Office location.")
    is_current: bool = Field(True, description="Whether this is the current job position.")

    @field_validator('employment_type')
    @classmethod
    def validate_employment_type(cls, v):
        valid_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'TEMPORARY']
        if v not in valid_types:
            raise ValueError(f"Employment type must be one of: {', '.join(valid_types)}")
        return v

class EmployeeJobTimelineResponse(BaseModel):
    """Response schema for employee job timeline."""
    id: int = Field(..., description="The ID of the job timeline record.")
    employee_id: int = Field(..., description="The ID of the employee.")
    effective_date: date = Field(..., description="Date when this job position became effective.")
    end_date: Optional[date] = Field(None, description="Date when this job position ended.")
    job_title: str = Field(..., description="Job title/position name.")
    position_type: Optional[str] = Field(None, description="Type of position.")
    employment_type: str = Field(..., description="Employment type.")
    line_manager_id: Optional[int] = Field(None, description="Direct manager's employee ID.")
    department: str = Field(..., description="Department name.")
    office: str = Field(..., description="Office location.")
    is_current: bool = Field(..., description="Whether this is the current job position.")
    created_at: datetime = Field(..., description="When the record was created.")
    updated_at: datetime = Field(..., description="When the record was last updated.")

# Bank Info Schemas
class EmployeeBankInfoRequest(BaseModel):
    """Request schema for creating/updating employee bank info."""
    bank_name: str = Field(..., max_length=255, description="Bank name.")
    account_number: str = Field(..., max_length=50, description="Bank account number.")
    routing_number: str = Field(..., max_length=20, description="Bank routing number.")
    account_type: str = Field(..., max_length=50, description="Account type.")
    account_holder_name: str = Field(..., max_length=255, description="Account holder name.")
    account_holder_type: str = Field(..., max_length=50, description="Account holder type.")
    is_primary: bool = Field(True, description="Whether this is the primary account.")
    is_active: bool = Field(True, description="Whether this bank account is active.")

class EmployeeBankInfoResponse(BaseModel):
    """Response schema for employee bank info."""
    id: int = Field(..., description="The ID of the bank info record.")
    employee_id: int = Field(..., description="The ID of the employee.")
    bank_name: str = Field(..., description="Bank name.")
    account_number: str = Field(..., description="Bank account number.")
    routing_number: str = Field(..., description="Bank routing number.")
    account_type: str = Field(..., description="Account type.")
    account_holder_name: str = Field(..., description="Account holder name.")
    account_holder_type: str = Field(..., description="Account holder type.")
    is_primary: bool = Field(..., description="Whether this is the primary account.")
    is_active: bool = Field(..., description="Whether this bank account is active.")
    created_at: datetime = Field(..., description="When the record was created.")
    updated_at: datetime = Field(..., description="When the record was last updated.")

# Dependent Schemas
class EmployeeDependentRequest(BaseModel):
    """Request schema for creating/updating employee dependent."""
    name: str = Field(..., max_length=255, description="Dependent's full name.")
    relationship_type: str = Field(..., max_length=50, description="Relationship to employee.")
    date_of_birth: Optional[date] = Field(None, description="Dependent's date of birth.")
    gender: Optional[str] = Field(None, max_length=20, description="Dependent's gender.")
    nationality: Optional[str] = Field(None, max_length=100, description="Dependent's nationality.")
    primary_address: Optional[str] = Field(None, max_length=500, description="Dependent's address.")
    city: Optional[str] = Field(None, max_length=100, description="City.")
    state: Optional[str] = Field(None, max_length=100, description="State.")
    country: Optional[str] = Field(None, max_length=100, description="Country.")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code.")
    is_active: bool = Field(True, description="Whether this dependent is active.")

    @field_validator('relationship_type')
    @classmethod
    def validate_relationship_type(cls, v):
        valid_types = ['SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER']
        if v not in valid_types:
            raise ValueError(f"Relationship type must be one of: {', '.join(valid_types)}")
        return v

class EmployeeDependentResponse(BaseModel):
    """Response schema for employee dependent."""
    id: int = Field(..., description="The ID of the dependent record.")
    employee_id: int = Field(..., description="The ID of the employee.")
    name: str = Field(..., description="Dependent's full name.")
    relationship_type: str = Field(..., description="Relationship to employee.")
    date_of_birth: Optional[date] = Field(None, description="Dependent's date of birth.")
    gender: Optional[str] = Field(None, description="Dependent's gender.")
    nationality: Optional[str] = Field(None, description="Dependent's nationality.")
    primary_address: Optional[str] = Field(None, description="Dependent's address.")
    city: Optional[str] = Field(None, description="City.")
    state: Optional[str] = Field(None, description="State.")
    country: Optional[str] = Field(None, description="Country.")
    postal_code: Optional[str] = Field(None, description="Postal code.")
    is_active: bool = Field(..., description="Whether this dependent is active.")
    created_at: datetime = Field(..., description="When the record was created.")
    updated_at: datetime = Field(..., description="When the record was last updated.")

# Document Schemas
class EmployeeDocumentRequest(BaseModel):
    """Request schema for creating/updating employee document."""
    document_type: str = Field(..., max_length=50, description="Type of document.")
    file_name: str = Field(..., max_length=255, description="Name of the file.")
    file_path: str = Field(..., max_length=500, description="Path to the file.")
    file_size: int = Field(..., description="Size of the file in bytes.")
    mime_type: str = Field(..., max_length=100, description="MIME type of the file.")
    is_active: bool = Field(True, description="Whether this document is active.")

class EmployeeDocumentResponse(BaseModel):
    """Response schema for employee document."""
    id: int = Field(..., description="The ID of the document record.")
    employee_id: int = Field(..., description="The ID of the employee.")
    document_type: str = Field(..., description="Type of document.")
    file_name: str = Field(..., description="Name of the file.")
    file_path: str = Field(..., description="Path to the file.")
    file_size: int = Field(..., description="Size of the file in bytes.")
    mime_type: str = Field(..., description="MIME type of the file.")
    upload_date: datetime = Field(..., description="When the document was uploaded.")
    uploaded_by_user_id: int = Field(..., description="ID of the user who uploaded the document.")
    is_active: bool = Field(..., description="Whether this document is active.")
    created_at: datetime = Field(..., description="When the record was created.")
    updated_at: datetime = Field(..., description="When the record was last updated.")

# Comprehensive Employee Request/Response
class EmployeeFullRequest(BaseModel):
    """Complete employee request with all related data."""
    # Basic employee info
    first_name: str = Field(..., min_length=1, max_length=50, description="The first name of the employee.")
    last_name: str = Field(..., min_length=1, max_length=50, description="The last name of the employee.")
    email: EmailStr = Field(..., min_length=1, max_length=50, description="The email of the employee.")
    phone: str = Field(..., min_length=1, max_length=50, description="The phone number of the employee.")
    join_date: date = Field(..., description="The date the employee joined the company.")
    
    # Optional related data
    personal_details: Optional[EmployeePersonalDetailsRequest] = Field(None, description="Personal details.")
    bank_info: Optional[EmployeeBankInfoRequest] = Field(None, description="Bank information.")
    job_timeline: List[EmployeeJobTimelineRequest] = Field(default_factory=list, description="Job timeline entries.")
    dependents: List[EmployeeDependentRequest] = Field(default_factory=list, description="Dependents.")
    documents: List[EmployeeDocumentRequest] = Field(default_factory=list, description="Documents.")

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        """Validate names contain only letters and common characters."""
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", v.strip()):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return v.strip().title()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format - flexible but secure."""
        if not v:  # Allow empty phone numbers
            return v
        digits_only = re.sub(r'\D', '', v.strip())
        if not (10 <= len(digits_only) <= 15):
            raise ValueError("Phone number must be 10-15 digits")
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        return v.strip()
    
    @field_validator('join_date')
    @classmethod
    def validate_join_date(cls, v):
        """Validate join date is a valid date."""
        if not isinstance(v, date):
            raise ValueError("Join date must be a valid date")
        return v

class EmployeeFullResponse(BaseModel):
    """Complete employee response with all related data."""
    id: int = Field(..., description="The ID of the employee.")
    user_id: int = Field(..., description="The ID of the user who created the employee.")
    first_name: str = Field(..., description="The first name of the employee.")
    last_name: str = Field(..., description="The last name of the employee.")
    email: EmailStr = Field(..., description="The email of the employee.")
    phone: str = Field(..., description="The phone number of the employee.")
    join_date: date = Field(..., description="The date the employee joined the company.")
    created_at: datetime = Field(..., description="When the employee record was created.")
    updated_at: datetime = Field(..., description="When the employee record was last updated.")
    
    # Related data
    personal_details: Optional[EmployeePersonalDetailsPublicResponse] = Field(None, description="Personal details (sensitive data masked).")
    bank_info: Optional[EmployeeBankInfoResponse] = Field(None, description="Bank information.")
    job_timeline: List[EmployeeJobTimelineResponse] = Field(default_factory=list, description="Job timeline.")
    dependents: List[EmployeeDependentResponse] = Field(default_factory=list, description="Dependents.")
    documents: List[EmployeeDocumentResponse] = Field(default_factory=list, description="Documents.")
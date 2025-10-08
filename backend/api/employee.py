from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_active_user
from models.employee import Employee
from schemas.employee import (
    EmployeeRequest, EmployeeResponse, EmployeeFullResponse, EmployeeFullRequest,
    EmployeePersonalDetailsRequest, EmployeePersonalDetailsResponse, EmployeePersonalDetailsPublicResponse,
    EmployeeJobTimelineRequest, EmployeeJobTimelineResponse,
    EmployeeBankInfoRequest, EmployeeBankInfoResponse, EmployeeBankInfoPublicResponse,
    EmployeeDependentRequest, EmployeeDependentResponse,
    EmployeeDocumentRequest, EmployeeDocumentResponse, EmployeeDocumentPublicResponse
)
from services.employee import EmployeeService
from models.user import User

router = APIRouter(
    prefix="/employee",
)

# ==================== EMPLOYEE CRUD ENDPOINTS ====================

@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee",
    description="Create a new employee with basic information",
    tags=["Employee Management"]
)
async def create_employee(
    employee_data: EmployeeRequest,
    current_user: User = Depends(get_current_active_user),  
    db: AsyncSession = Depends(get_db)
) -> EmployeeResponse:
    """
    Create a new employee with basic information.
    
    - **first_name**: Employee's first name
    - **last_name**: Employee's last name  
    - **email**: Employee's email address (must be unique)
    - **phone**: Employee's phone number
    - **join_date**: Date the employee joined the company
    """
    try:
        return await EmployeeService.create_employee(db, employee_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "",
    response_model=List[EmployeeResponse],
    summary="List Employees",
    description="Get a list of all employees for the current user",
    tags=["Employee Management"]
)
async def list_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[EmployeeResponse]:
    """
    Get a paginated list of all employees for the current user.
    """
    try:
        return await EmployeeService.list_employees(db, current_user, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get Employee",
    description="Get a specific employee by ID",
    tags=["Employee Management"]
)
async def get_employee(
    employee_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeResponse:
    """
    Get a specific employee by ID.
    """
    try:
        employee = await EmployeeService.get_employee(db, employee_id, current_user)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{employee_id}/full",
    response_model=EmployeeFullResponse,
    summary="Get Employee Full Details",
    description="Get complete employee information with all related data",
    tags=["Employee Management"]
)
async def get_employee_full(
    employee_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeFullResponse:
    """
    Get complete employee information including personal details, job timeline, 
    bank info, dependents, and documents.
    """
    try:
        employee = await EmployeeService.get_employee_full(db, employee_id, current_user)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== JOB TIMELINE ENDPOINTS ====================

@router.post(
    "/{employee_id}/job",
    response_model=EmployeeJobTimelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Job Timeline Entry",
    description="Add a job timeline entry for an employee",
    tags=["Employee Job Timeline"]
)
async def create_job_timeline(
    employee_id: int,
    job_data: EmployeeJobTimelineRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeJobTimelineResponse:
    """
    Add a job timeline entry for an employee.
    
    - **effective_date**: Date when this job position became effective
    - **end_date**: Date when this job position ended (optional)
    - **job_title**: Job title/position name
    - **employment_type**: FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP, TEMPORARY
    - **department**: Department name
    - **office**: Office location
    - **is_current**: Whether this is the current job position
    - **line_manager_id**: Direct manager's employee ID (optional)
    """
    try:
        return await EmployeeService.create_job_timeline(db, employee_id, job_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== DEPENDENT ENDPOINTS ====================

@router.post(
    "/{employee_id}/dependent",
    response_model=EmployeeDependentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Dependent",
    description="Add a dependent for an employee",
    tags=["Employee Dependents"]
)
async def create_dependent(
    employee_id: int,
    dependent_data: EmployeeDependentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDependentResponse:
    """
    Add a dependent for an employee.
    
    - **name**: Dependent's full name
    - **relationship_type**: SPOUSE, CHILD, PARENT, SIBLING, OTHER
    - **date_of_birth**: Dependent's date of birth (optional)
    - **gender**: Dependent's gender (optional)
    - **nationality**: Dependent's nationality (optional)
    - **primary_address**: Dependent's address (optional)
    - **city**, **state**, **country**, **postal_code**: Address components (optional)
    - **is_active**: Whether this dependent is active
    """
    try:
        return await EmployeeService.create_dependent(db, employee_id, dependent_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==================== DOCUMENT ENDPOINTS ====================

@router.post(
    "/{employee_id}/document",
    response_model=EmployeeDocumentPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="Upload a document for an employee",
    tags=["Employee Documents"]
)
async def create_document(
    employee_id: int,
    document_data: EmployeeDocumentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDocumentPublicResponse:
    """
    Upload a document for an employee.
    
    - **document_type**: Type of document (e.g., PASSPORT, DRIVER_LICENSE, CONTRACT)
    - **file_name**: Name of the file
    - **file_path**: Path to the file on the server
    - **file_size**: Size of the file in bytes
    - **mime_type**: MIME type of the file
    - **is_active**: Whether this document is active
    """
    try:
        return await EmployeeService.create_document(db, employee_id, document_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==================== FULL EMPLOYEE OPERATIONS ====================

@router.post(
    "/full",
    response_model=EmployeeFullResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Full Employee",
    description="Create a complete employee with all related data in one request",
    tags=["Employee Management"]
)
async def create_employee_full(
    employee_data: EmployeeFullRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeFullResponse:
    """
    Create a complete employee with all related data in one transaction.
    
    This endpoint allows you to create an employee with all their information
    including personal details, bank info, job timeline, dependents, and documents
    in a single API call.
    
    **Basic Employee Info:**
    - **first_name**: Employee's first name
    - **last_name**: Employee's last name  
    - **email**: Employee's email address (must be unique)
    - **phone**: Employee's phone number
    - **join_date**: Date the employee joined the company
    
    **Optional Related Data:**
    - **personal_details**: Personal information (gender, DOB, address, etc.)
    - **bank_info**: Banking information for payroll
    - **job_timeline**: Job history and current position
    - **dependents**: Family members and dependents
    - **documents**: Uploaded documents and files
    """
    try:
        return await EmployeeService.create_employee_full(db, employee_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/{employee_id}/full",
    response_model=EmployeeFullResponse,
    summary="Update Full Employee",
    description="Update a complete employee with all related data in one request",
    tags=["Employee Management"]
)
async def update_employee_full(
    employee_id: int,
    employee_data: EmployeeFullRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeFullResponse:
    """
    Update a complete employee with all related data in one transaction.
    
    This endpoint allows you to update an employee with all their information
    including personal details, bank info, job timeline, dependents, and documents
    in a single API call. All existing related data will be replaced with the new data.
    
    **Basic Employee Info:**
    - **first_name**: Employee's first name
    - **last_name**: Employee's last name  
    - **email**: Employee's email address (must be unique)
    - **phone**: Employee's phone number
    - **join_date**: Date the employee joined the company
    
    **Related Data (will replace existing):**
    - **personal_details**: Personal information (gender, DOB, address, etc.)
    - **bank_info**: Banking information for payroll
    - **job_timeline**: Job history and current position
    - **dependents**: Family members and dependents
    - **documents**: Uploaded documents and files
    
    **Note:** This operation will delete all existing related data and create new records.
    """
    try:
        return await EmployeeService.update_employee_full(db, employee_id, employee_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==================== EMPLOYEE PERSONAL DETAILS ENDPOINTS ====================

@router.post(
    "/{employee_id}/personal",
    response_model=EmployeePersonalDetailsPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee Personal Details",
    description="Create personal details for a specific employee",
    tags=["Employee Personal Details"]
)
async def create_employee_personal_details(
    employee_id: int,
    personal_data: EmployeePersonalDetailsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeePersonalDetailsPublicResponse:
    """
    Create personal details for an employee.
    
    This endpoint creates personal information for a specific employee including
    sensitive data like tax ID and social insurance number. Only the employee's
    owner can create personal details.
    
    **Personal Information:**
    - **gender**: Employee's gender (MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY)
    - **date_of_birth**: Employee's date of birth
    - **nationality**: Employee's nationality
    - **health_care_provider**: Healthcare provider name
    - **marital_status**: Marital status (SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED)
    - **personal_tax_id**: Personal tax identification number
    - **social_insurance_number**: Social insurance number
    - **primary_address**: Street address
    - **city**: City name
    - **state**: State or province
    - **country**: Country name
    - **postal_code**: Postal/ZIP code
    
    **Security Note:** Sensitive fields (tax_id, social_insurance, address) are masked in responses.
    """
    try:
        return await EmployeeService.create_personal_details(db, employee_id, personal_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{employee_id}/personal",
    response_model=EmployeePersonalDetailsPublicResponse,
    summary="Get Employee Personal Details",
    description="Retrieve personal details for a specific employee",
    tags=["Employee Personal Details"]
)
async def get_employee_personal_details(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeePersonalDetailsPublicResponse:
    """
    Get personal details for an employee.
    
    This endpoint retrieves personal information for a specific employee.
    Only the employee's owner can access personal details.
    
    **Response includes:**
    - All personal information fields
    - Sensitive data is masked for security
    - Timestamps for audit trail
    
    **Security Note:** Sensitive fields are automatically masked in the response.
    """
    try:
        personal_details = await EmployeeService.get_personal_details(db, employee_id, current_user)
        if not personal_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal details not found for this employee"
            )
        return personal_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/{employee_id}/personal",
    response_model=EmployeePersonalDetailsPublicResponse,
    summary="Update Employee Personal Details",
    description="Replace all personal details for a specific employee",
    tags=["Employee Personal Details"]
)
async def update_employee_personal_details(
    employee_id: int,
    personal_data: EmployeePersonalDetailsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeePersonalDetailsPublicResponse:
    """
    Update personal details for an employee (full replacement).
    
    This endpoint completely replaces all personal information for a specific employee.
    All existing personal details will be overwritten with the new data.
    
    **Update Behavior:**
    - Replaces ALL existing personal details
    - Creates new record if none exists
    - Validates all provided fields
    - Maintains data integrity constraints
    
    **Personal Information Fields:**
    - All fields from the create endpoint
    - Sensitive data is masked in response
    - Timestamps are automatically updated
    
    **Security Note:** Sensitive fields are masked in the response for security.
    """
    try:
        return await EmployeeService.update_personal_details(db, employee_id, personal_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch(
    "/{employee_id}/personal",
    response_model=EmployeePersonalDetailsPublicResponse,
    summary="Partially Update Employee Personal Details",
    description="Update specific fields in employee personal details",
    tags=["Employee Personal Details"]
)
async def partial_update_employee_personal_details(
    employee_id: int,
    personal_data: EmployeePersonalDetailsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeePersonalDetailsPublicResponse:
    """
    Partially update personal details for an employee.
    
    This endpoint allows you to update only specific fields in the employee's
    personal details without affecting other fields. Only provided fields will be updated.
    
    **Partial Update Behavior:**
    - Only updates provided fields
    - Leaves other fields unchanged
    - Validates only provided fields
    - Maintains existing data for omitted fields
    
    **Use Cases:**
    - Update only address information
    - Change marital status
    - Update healthcare provider
    - Modify specific sensitive data
    
    **Security Note:** Sensitive fields are masked in the response for security.
    """
    try:
        return await EmployeeService.partial_update_personal_details(db, employee_id, personal_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/{employee_id}/personal",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee Personal Details",
    description="Remove personal details for a specific employee",
    tags=["Employee Personal Details"]
)
async def delete_employee_personal_details(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete personal details for an employee.
    
    This endpoint permanently removes all personal information for a specific employee.
    This action cannot be undone and will delete all personal data.
    
    **Deletion Behavior:**
    - Permanently removes personal details record
    - Cannot be undone
    - Returns 204 No Content on success
    - Returns 404 if no personal details exist
    
    **Security Considerations:**
    - Only employee owner can delete personal details
    - Sensitive data is permanently removed
    - Audit trail may be maintained in logs
    
    **Use Cases:**
    - Employee leaving the company
    - Data privacy compliance
    - Cleanup of test data
    """
    try:
        success = await EmployeeService.delete_personal_details(db, employee_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal details not found for this employee"
            )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==================== EMPLOYEE BANK INFO ENDPOINTS ====================

@router.post(
    "/{employee_id}/bank",
    response_model=EmployeeBankInfoPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee Bank Information",
    description="Create bank information for a specific employee",
    tags=["Employee Bank Information"]
)
async def create_employee_bank_info(
    employee_id: int,
    bank_data: EmployeeBankInfoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeBankInfoPublicResponse:
    """
    Create bank information for an employee.
    
    This endpoint creates banking details for a specific employee including
    sensitive data like account numbers and routing numbers. Only the employee's
    owner can create bank information.
    
    **Bank Information:**
    - **bank_name**: Name of the financial institution
    - **account_number**: Bank account number (sensitive data)
    - **routing_number**: Bank routing number (sensitive data)
    - **account_type**: Type of account (CHECKING, SAVINGS, etc.)
    - **account_holder_name**: Name on the account
    - **account_holder_type**: Type of account holder (INDIVIDUAL, JOINT, etc.)
    - **is_primary**: Whether this is the primary bank account
    - **is_active**: Whether this bank account is currently active
    
    **Security Note:** Sensitive fields (account_number, routing_number) are masked in responses.
    """
    try:
        return await EmployeeService.create_bank_info(db, employee_id, bank_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{employee_id}/bank",
    response_model=EmployeeBankInfoPublicResponse,
    summary="Get Employee Bank Information",
    description="Retrieve bank information for a specific employee",
    tags=["Employee Bank Information"]
)
async def get_employee_bank_info(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeBankInfoPublicResponse:
    """
    Get bank information for an employee.
    
    This endpoint retrieves banking details for a specific employee.
    Only the employee's owner can access bank information.
    
    **Response includes:**
    - All bank information fields
    - Sensitive data is masked for security
    - Timestamps for audit trail
    
    **Security Note:** Sensitive fields are automatically masked in the response.
    """
    try:
        bank_info = await EmployeeService.get_bank_info(db, employee_id, current_user)
        if not bank_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank information not found for this employee"
            )
        return bank_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/{employee_id}/bank",
    response_model=EmployeeBankInfoPublicResponse,
    summary="Update Employee Bank Information",
    description="Replace all bank information for a specific employee",
    tags=["Employee Bank Information"]
)
async def update_employee_bank_info(
    employee_id: int,
    bank_data: EmployeeBankInfoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeBankInfoPublicResponse:
    """
    Update bank information for an employee (full replacement).
    
    This endpoint completely replaces all banking details for a specific employee.
    All existing bank information will be overwritten with the new data.
    
    **Update Behavior:**
    - Replaces ALL existing bank information
    - Creates new record if none exists
    - Validates all provided fields
    - Maintains data integrity constraints
    
    **Bank Information Fields:**
    - All fields from the create endpoint
    - Sensitive data is masked in response
    - Timestamps are automatically updated
    
    **Security Note:** Sensitive fields are masked in the response for security.
    """
    try:
        return await EmployeeService.update_bank_info(db, employee_id, bank_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch(
    "/{employee_id}/bank",
    response_model=EmployeeBankInfoPublicResponse,
    summary="Partially Update Employee Bank Information",
    description="Update specific fields in employee bank information",
    tags=["Employee Bank Information"]
)
async def partial_update_employee_bank_info(
    employee_id: int,
    bank_data: EmployeeBankInfoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeBankInfoPublicResponse:
    """
    Partially update bank information for an employee.
    
    This endpoint allows you to update only specific fields in the employee's
    bank information without affecting other fields. Only provided fields will be updated.
    
    **Partial Update Behavior:**
    - Only updates provided fields
    - Leaves other fields unchanged
    - Validates only provided fields
    - Maintains existing data for omitted fields
    
    **Use Cases:**
    - Update only account number
    - Change primary account status
    - Update account holder information
    - Modify account type
    
    **Security Note:** Sensitive fields are masked in the response for security.
    """
    try:
        return await EmployeeService.partial_update_bank_info(db, employee_id, bank_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/{employee_id}/bank",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee Bank Information",
    description="Remove bank information for a specific employee",
    tags=["Employee Bank Information"]
)
async def delete_employee_bank_info(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete bank information for an employee.
    
    This endpoint permanently removes all banking details for a specific employee.
    This action cannot be undone and will delete all bank data.
    
    **Deletion Behavior:**
    - Permanently removes bank information record
    - Cannot be undone
    - Returns 204 No Content on success
    - Returns 404 if no bank information exists
    
    **Security Considerations:**
    - Only employee owner can delete bank information
    - Sensitive data is permanently removed
    - Audit trail may be maintained in logs
    
    **Use Cases:**
    - Employee leaving the company
    - Data privacy compliance
    - Cleanup of test data
    - Account closure
    """
    try:
        success = await EmployeeService.delete_bank_info(db, employee_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank information not found for this employee"
            )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==================== EMPLOYEE DOCUMENTS ENDPOINTS ====================

@router.post(
    "/{employee_id}/documents",
    response_model=EmployeeDocumentPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee Document",
    description="Create a document record for a specific employee",
    tags=["Employee Documents"]
)
async def create_employee_document(
    employee_id: int,
    document_data: EmployeeDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeDocumentPublicResponse:
    """
    Create a document record for an employee.
    
    This endpoint creates a document record for a specific employee including
    file metadata and upload information. Only the employee's owner can create documents.
    
    **Document Information:**
    - **document_type**: Type of document (CONTRACT, ID, CERTIFICATE, etc.)
    - **file_name**: Original name of the uploaded file
    - **file_path**: Server path to the stored file (sensitive data)
    - **file_size**: Size of the file in bytes
    - **mime_type**: MIME type of the file (e.g., application/pdf, image/jpeg)
    - **is_active**: Whether this document is currently active
    
    **Security Note:** Sensitive fields (file_path) are masked in responses.
    """
    try:
        return await EmployeeService.create_document(db, employee_id, document_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{employee_id}/documents",
    response_model=List[EmployeeDocumentPublicResponse],
    summary="Get Employee Documents",
    description="Retrieve all documents for a specific employee",
    tags=["Employee Documents"]
)
async def get_employee_documents(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[EmployeeDocumentPublicResponse]:
    """
    Get all documents for an employee.
    
    This endpoint retrieves all document records for a specific employee.
    Only the employee's owner can access documents.
    
    **Response includes:**
    - All document information fields
    - Sensitive data is masked for security
    - Timestamps for audit trail
    - List of all documents for the employee
    
    **Security Note:** Sensitive fields are automatically masked in the response.
    """
    try:
        documents = await EmployeeService.get_documents(db, employee_id, current_user)
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{employee_id}/documents/{document_id}",
    response_model=EmployeeDocumentPublicResponse,
    summary="Get Employee Document by ID",
    description="Retrieve a specific document for an employee",
    tags=["Employee Documents"]
)
async def get_employee_document(
    employee_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeDocumentPublicResponse:
    """
    Get a specific document for an employee.
    
    This endpoint retrieves a specific document record for an employee.
    Only the employee's owner can access the document.
    
    **Response includes:**
    - All document information fields
    - Sensitive data is masked for security
    - Timestamps for audit trail
    
    **Security Note:** Sensitive fields are automatically masked in the response.
    """
    try:
        document = await EmployeeService.get_document(db, employee_id, document_id, current_user)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found for this employee"
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/{employee_id}/documents/{document_id}",
    response_model=EmployeeDocumentPublicResponse,
    summary="Update Employee Document",
    description="Replace all document information for a specific document",
    tags=["Employee Documents"]
)
async def update_employee_document(
    employee_id: int,
    document_id: int,
    document_data: EmployeeDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeDocumentPublicResponse:
    """
    Update document information for an employee (full replacement).
    
    This endpoint completely replaces all document information for a specific document.
    All existing document data will be overwritten with the new data.
    
    **Update Behavior:**
    - Replaces ALL existing document information
    - Validates all provided fields
    - Maintains data integrity constraints
    - Updates timestamps automatically
    
    **Document Information Fields:**
    - All fields from the create endpoint
    - Sensitive data is masked in response
    - Timestamps are automatically updated
    
    **Security Note:** Sensitive fields are masked in the response for security.
    """
    try:
        return await EmployeeService.update_document(db, employee_id, document_id, document_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch(
    "/{employee_id}/documents/{document_id}",
    response_model=EmployeeDocumentPublicResponse,
    summary="Partially Update Employee Document",
    description="Update specific fields in employee document",
    tags=["Employee Documents"]
)
async def partial_update_employee_document(
    employee_id: int,
    document_id: int,
    document_data: EmployeeDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> EmployeeDocumentPublicResponse:
    """
    Partially update document information for an employee.
    
    This endpoint allows you to update only specific fields in the document
    without affecting other fields. Only provided fields will be updated.
    
    **Partial Update Behavior:**
    - Only updates provided fields
    - Leaves other fields unchanged
    - Validates only provided fields
    - Maintains existing data for omitted fields
    
    **Use Cases:**
    - Update only document type
    - Change file name
    - Update active status
    - Modify MIME type
    
    **Security Note:** Sensitive fields are masked in the response for security.
    """
    try:
        return await EmployeeService.partial_update_document(db, employee_id, document_id, document_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/{employee_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee Document",
    description="Remove a specific document for an employee",
    tags=["Employee Documents"]
)
async def delete_employee_document(
    employee_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a specific document for an employee.
    
    This endpoint permanently removes a specific document record for an employee.
    This action cannot be undone and will delete the document data.
    
    **Deletion Behavior:**
    - Permanently removes document record
    - Cannot be undone
    - Returns 204 No Content on success
    - Returns 404 if document not found
    
    **Security Considerations:**
    - Only employee owner can delete documents
    - Sensitive data is permanently removed
    - Audit trail may be maintained in logs
    
    **Use Cases:**
    - Document no longer needed
    - Data privacy compliance
    - Cleanup of test data
    - Document replacement
    """
    try:
        success = await EmployeeService.delete_document(db, employee_id, document_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found for this employee"
            )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

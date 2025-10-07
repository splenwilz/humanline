from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_active_user
from models.employee import Employee
from schemas.employee import (
    EmployeeRequest, EmployeeResponse, EmployeeFullResponse, EmployeeFullRequest,
    EmployeePersonalDetailsRequest, EmployeePersonalDetailsResponse,
    EmployeeJobTimelineRequest, EmployeeJobTimelineResponse,
    EmployeeBankInfoRequest, EmployeeBankInfoResponse,
    EmployeeDependentRequest, EmployeeDependentResponse,
    EmployeeDocumentRequest, EmployeeDocumentResponse
)
from services.employee import EmployeeService
from models.user import User

router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
)

# ==================== EMPLOYEE CRUD ENDPOINTS ====================

@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee",
    description="Create a new employee with basic information"
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
    description="Get a list of all employees for the current user"
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
    description="Get a specific employee by ID"
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
    description="Get complete employee information with all related data"
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

# ==================== PERSONAL DETAILS ENDPOINTS ====================

@router.post(
    "/{employee_id}/personal",
    response_model=EmployeePersonalDetailsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Personal Details",
    description="Add personal details for an employee"
)
async def create_personal_details(
    employee_id: int,
    personal_data: EmployeePersonalDetailsRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeePersonalDetailsResponse:
    """
    Add personal details for an employee.
    
    - **gender**: MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY
    - **date_of_birth**: Employee's date of birth
    - **nationality**: Employee's nationality
    - **marital_status**: SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED
    - **personal_tax_id**: Personal tax identification number
    - **social_insurance_number**: Social insurance number
    - **primary_address**: Primary residential address
    - **city**, **state**, **country**, **postal_code**: Address components
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

# ==================== JOB TIMELINE ENDPOINTS ====================

@router.post(
    "/{employee_id}/job",
    response_model=EmployeeJobTimelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Job Timeline Entry",
    description="Add a job timeline entry for an employee"
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

# ==================== BANK INFO ENDPOINTS ====================

@router.post(
    "/{employee_id}/bank",
    response_model=EmployeeBankInfoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Bank Information",
    description="Add banking information for an employee"
)
async def create_bank_info(
    employee_id: int,
    bank_data: EmployeeBankInfoRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeBankInfoResponse:
    """
    Add banking information for an employee.
    
    - **bank_name**: Name of the bank
    - **account_number**: Bank account number
    - **routing_number**: Bank routing number
    - **account_type**: Type of account (e.g., CHECKING, SAVINGS)
    - **account_holder_name**: Name on the account
    - **account_holder_type**: Type of account holder
    - **is_primary**: Whether this is the primary account for payroll
    - **is_active**: Whether this bank account is active
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

# ==================== DEPENDENT ENDPOINTS ====================

@router.post(
    "/{employee_id}/dependent",
    response_model=EmployeeDependentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Dependent",
    description="Add a dependent for an employee"
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
    response_model=EmployeeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="Upload a document for an employee"
)
async def create_document(
    employee_id: int,
    document_data: EmployeeDocumentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDocumentResponse:
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
    description="Create a complete employee with all related data in one request"
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
    description="Update a complete employee with all related data in one request"
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
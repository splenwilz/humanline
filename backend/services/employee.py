from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone

from schemas.employee import (
    EmployeeRequest, EmployeeResponse, EmployeeFullResponse, EmployeeFullRequest,
    EmployeePersonalDetailsRequest, EmployeePersonalDetailsResponse,
    EmployeeJobTimelineRequest, EmployeeJobTimelineResponse,
    EmployeeBankInfoRequest, EmployeeBankInfoResponse,
    EmployeeDependentRequest, EmployeeDependentResponse,
    EmployeeDocumentRequest, EmployeeDocumentResponse
)
from models.employee import (
    Employee, EmployeePersonalDetails, EmployeeJobTimeline,
    EmployeeBankInfo, EmployeeDependent, EmployeeDocument
)
from models.user import User

class EmployeeService:
    """Service class for employee operations."""

    # ==================== EMPLOYEE CRUD ====================
    
    @staticmethod
    async def create_employee(db: AsyncSession, employee_data: EmployeeRequest, current_user: User) -> EmployeeResponse:
        """Create a new employee."""
        try:
            employee = Employee(
                user_id=current_user.id,  # Use the authenticated user's ID
                first_name=employee_data.first_name,
                last_name=employee_data.last_name,
                email=employee_data.email,
                phone=employee_data.phone,
                join_date=employee_data.join_date
            )
            db.add(employee)
            await db.commit()
            await db.refresh(employee)
            return EmployeeResponse(
                id=employee.id,
                user_id=employee.user_id,
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                phone=employee.phone,
                join_date=employee.join_date,
                created_at=employee.created_at,
                updated_at=employee.updated_at
            )
        except IntegrityError as e:
            await db.rollback()
            error_msg = str(e.orig).lower()
            if 'unique constraint' in error_msg and 'email' in error_msg:
                raise ValueError("Email already exists")
            else:
                raise ValueError("Employee creation failed")
        except Exception as e:
            raise e

    @staticmethod
    async def get_employee(db: AsyncSession, employee_id: int, current_user: User) -> Optional[EmployeeResponse]:
        """Get an employee by ID."""
        result = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        employee = result.scalar_one_or_none()
        if not employee:
            return None
        
        return EmployeeResponse(
            id=employee.id,
            user_id=employee.user_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
            join_date=employee.join_date,
            created_at=employee.created_at,
            updated_at=employee.updated_at
        )

    @staticmethod
    async def get_employee_full(db: AsyncSession, employee_id: int, current_user: User) -> Optional[EmployeeFullResponse]:
        """Get an employee with all related data."""
        result = await db.execute(
            select(Employee)
            .options(
                selectinload(Employee.personal_details),
                selectinload(Employee.bank_info),
                selectinload(Employee.job_timeline),
                selectinload(Employee.dependents),
                selectinload(Employee.documents)
            )
            .where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        employee = result.scalar_one_or_none()
        if not employee:
            return None
        
        # Convert related data to response schemas
        personal_details = None
        if employee.personal_details:
            personal_details = EmployeePersonalDetailsResponse(
                id=employee.personal_details.id,
                employee_id=employee.personal_details.employee_id,
                gender=employee.personal_details.gender,
                date_of_birth=employee.personal_details.date_of_birth,
                nationality=employee.personal_details.nationality,
                health_care_provider=employee.personal_details.health_care_provider,
                marital_status=employee.personal_details.marital_status,
                personal_tax_id=employee.personal_details.personal_tax_id,
                social_insurance_number=employee.personal_details.social_insurance_number,
                primary_address=employee.personal_details.primary_address,
                city=employee.personal_details.city,
                state=employee.personal_details.state,
                country=employee.personal_details.country,
                postal_code=employee.personal_details.postal_code,
                created_at=employee.personal_details.created_at,
                updated_at=employee.personal_details.updated_at
            )
        
        bank_info = None
        if employee.bank_info:
            bank_info = EmployeeBankInfoResponse(
                id=employee.bank_info.id,
                employee_id=employee.bank_info.employee_id,
                bank_name=employee.bank_info.bank_name,
                account_number=employee.bank_info.account_number,
                routing_number=employee.bank_info.routing_number,
                account_type=employee.bank_info.account_type,
                account_holder_name=employee.bank_info.account_holder_name,
                account_holder_type=employee.bank_info.account_holder_type,
                is_primary=employee.bank_info.is_primary,
                is_active=employee.bank_info.is_active,
                created_at=employee.bank_info.created_at,
                updated_at=employee.bank_info.updated_at
            )
        
        job_timeline = [
            EmployeeJobTimelineResponse(
                id=job.id,
                employee_id=job.employee_id,
                effective_date=job.effective_date,
                end_date=job.end_date,
                job_title=job.job_title,
                position_type=job.position_type,
                employment_type=job.employment_type,
                line_manager_id=job.line_manager_id,
                department=job.department,
                office=job.office,
                is_current=job.is_current,
                created_at=job.created_at,
                updated_at=job.updated_at
            ) for job in employee.job_timeline
        ]
        
        dependents = [
            EmployeeDependentResponse(
                id=dep.id,
                employee_id=dep.employee_id,
                name=dep.name,
                relationship_type=dep.relationship_type,
                date_of_birth=dep.date_of_birth,
                gender=dep.gender,
                nationality=dep.nationality,
                primary_address=dep.primary_address,
                city=dep.city,
                state=dep.state,
                country=dep.country,
                postal_code=dep.postal_code,
                is_active=dep.is_active,
                created_at=dep.created_at,
                updated_at=dep.updated_at
            ) for dep in employee.dependents
        ]
        
        documents = [
            EmployeeDocumentResponse(
                id=doc.id,
                employee_id=doc.employee_id,
                document_type=doc.document_type,
                file_name=doc.file_name,
                file_path=doc.file_path,
                file_size=doc.file_size,
                mime_type=doc.mime_type,
                upload_date=doc.upload_date,
                uploaded_by_user_id=doc.uploaded_by_user_id,
                is_active=doc.is_active,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ) for doc in employee.documents
        ]
        
        return EmployeeFullResponse(
            id=employee.id,
            user_id=employee.user_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
            join_date=employee.join_date,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            personal_details=personal_details,
            bank_info=bank_info,
            job_timeline=job_timeline,
            dependents=dependents,
            documents=documents
        )

    @staticmethod
    async def list_employees(db: AsyncSession, current_user: User, skip: int = 0, limit: int = 100) -> List[EmployeeResponse]:
        """List all employees for the current user."""
        result = await db.execute(
            select(Employee)
            .where(Employee.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        employees = result.scalars().all()
        
        return [
            EmployeeResponse(
                id=emp.id,
                user_id=emp.user_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                phone=emp.phone,
                join_date=emp.join_date,
                created_at=emp.created_at,
                updated_at=emp.updated_at
            ) for emp in employees
        ]

    # ==================== PERSONAL DETAILS ====================
    
    @staticmethod
    async def create_personal_details(
        db: AsyncSession, 
        employee_id: int, 
        personal_data: EmployeePersonalDetailsRequest, 
        current_user: User
    ) -> EmployeePersonalDetailsResponse:
        """Create personal details for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            personal_details = EmployeePersonalDetails(
                employee_id=employee_id,
                gender=personal_data.gender,
                date_of_birth=personal_data.date_of_birth,
                nationality=personal_data.nationality,
                health_care_provider=personal_data.health_care_provider,
                marital_status=personal_data.marital_status,
                personal_tax_id=personal_data.personal_tax_id,
                social_insurance_number=personal_data.social_insurance_number,
                primary_address=personal_data.primary_address,
                city=personal_data.city,
                state=personal_data.state,
                country=personal_data.country,
                postal_code=personal_data.postal_code
            )
            db.add(personal_details)
            await db.commit()
            await db.refresh(personal_details)
            
            return EmployeePersonalDetailsResponse(
                id=personal_details.id,
                employee_id=personal_details.employee_id,
                gender=personal_details.gender,
                date_of_birth=personal_details.date_of_birth,
                nationality=personal_details.nationality,
                health_care_provider=personal_details.health_care_provider,
                marital_status=personal_details.marital_status,
                personal_tax_id=personal_details.personal_tax_id,
                social_insurance_number=personal_details.social_insurance_number,
                primary_address=personal_details.primary_address,
                city=personal_details.city,
                state=personal_details.state,
                country=personal_details.country,
                postal_code=personal_details.postal_code,
                created_at=personal_details.created_at,
                updated_at=personal_details.updated_at
            )
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Personal details already exist for this employee")
        except Exception as e:
            raise e

    # ==================== JOB TIMELINE ====================
    
    @staticmethod
    async def create_job_timeline(
        db: AsyncSession, 
        employee_id: int, 
        job_data: EmployeeJobTimelineRequest, 
        current_user: User
    ) -> EmployeeJobTimelineResponse:
        """Create a job timeline entry for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # If this is the current job, deactivate other current jobs
            if job_data.is_current:
                await db.execute(
                    select(EmployeeJobTimeline)
                    .where(
                        and_(
                            EmployeeJobTimeline.employee_id == employee_id,
                            EmployeeJobTimeline.is_current == True
                        )
                    )
                )
                # Update existing current jobs to False
                existing_jobs = await db.execute(
                    select(EmployeeJobTimeline).where(
                        and_(
                            EmployeeJobTimeline.employee_id == employee_id,
                            EmployeeJobTimeline.is_current == True
                        )
                    )
                )
                for job in existing_jobs.scalars():
                    job.is_current = False
            
            job_timeline = EmployeeJobTimeline(
                employee_id=employee_id,
                effective_date=job_data.effective_date,
                end_date=job_data.end_date,
                job_title=job_data.job_title,
                position_type=job_data.position_type,
                employment_type=job_data.employment_type,
                line_manager_id=job_data.line_manager_id,
                department=job_data.department,
                office=job_data.office,
                is_current=job_data.is_current
            )
            db.add(job_timeline)
            await db.commit()
            await db.refresh(job_timeline)
            
            return EmployeeJobTimelineResponse(
                id=job_timeline.id,
                employee_id=job_timeline.employee_id,
                effective_date=job_timeline.effective_date,
                end_date=job_timeline.end_date,
                job_title=job_timeline.job_title,
                position_type=job_timeline.position_type,
                employment_type=job_timeline.employment_type,
                line_manager_id=job_timeline.line_manager_id,
                department=job_timeline.department,
                office=job_timeline.office,
                is_current=job_timeline.is_current,
                created_at=job_timeline.created_at,
                updated_at=job_timeline.updated_at
            )
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== BANK INFO ====================
    
    @staticmethod
    async def create_bank_info(
        db: AsyncSession, 
        employee_id: int, 
        bank_data: EmployeeBankInfoRequest, 
        current_user: User
    ) -> EmployeeBankInfoResponse:
        """Create bank info for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            bank_info = EmployeeBankInfo(
                employee_id=employee_id,
                bank_name=bank_data.bank_name,
                account_number=bank_data.account_number,
                routing_number=bank_data.routing_number,
                account_type=bank_data.account_type,
                account_holder_name=bank_data.account_holder_name,
                account_holder_type=bank_data.account_holder_type,
                is_primary=bank_data.is_primary,
                is_active=bank_data.is_active
            )
            db.add(bank_info)
            await db.commit()
            await db.refresh(bank_info)
            
            return EmployeeBankInfoResponse(
                id=bank_info.id,
                employee_id=bank_info.employee_id,
                bank_name=bank_info.bank_name,
                account_number=bank_info.account_number,
                routing_number=bank_info.routing_number,
                account_type=bank_info.account_type,
                account_holder_name=bank_info.account_holder_name,
                account_holder_type=bank_info.account_holder_type,
                is_primary=bank_info.is_primary,
                is_active=bank_info.is_active,
                created_at=bank_info.created_at,
                updated_at=bank_info.updated_at
            )
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Bank info already exists for this employee")
        except Exception as e:
            raise e

    # ==================== DEPENDENTS ====================
    
    @staticmethod
    async def create_dependent(
        db: AsyncSession, 
        employee_id: int, 
        dependent_data: EmployeeDependentRequest, 
        current_user: User
    ) -> EmployeeDependentResponse:
        """Create a dependent for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            dependent = EmployeeDependent(
                employee_id=employee_id,
                name=dependent_data.name,
                relationship_type=dependent_data.relationship_type,
                date_of_birth=dependent_data.date_of_birth,
                gender=dependent_data.gender,
                nationality=dependent_data.nationality,
                primary_address=dependent_data.primary_address,
                city=dependent_data.city,
                state=dependent_data.state,
                country=dependent_data.country,
                postal_code=dependent_data.postal_code,
                is_active=dependent_data.is_active
            )
            db.add(dependent)
            await db.commit()
            await db.refresh(dependent)
            
            return EmployeeDependentResponse(
                id=dependent.id,
                employee_id=dependent.employee_id,
                name=dependent.name,
                relationship_type=dependent.relationship_type,
                date_of_birth=dependent.date_of_birth,
                gender=dependent.gender,
                nationality=dependent.nationality,
                primary_address=dependent.primary_address,
                city=dependent.city,
                state=dependent.state,
                country=dependent.country,
                postal_code=dependent.postal_code,
                is_active=dependent.is_active,
                created_at=dependent.created_at,
                updated_at=dependent.updated_at
            )
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== DOCUMENTS ====================
    
    @staticmethod
    async def create_document(
        db: AsyncSession, 
        employee_id: int, 
        document_data: EmployeeDocumentRequest, 
        current_user: User
    ) -> EmployeeDocumentResponse:
        """Create a document for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            document = EmployeeDocument(
                employee_id=employee_id,
                document_type=document_data.document_type,
                file_name=document_data.file_name,
                file_path=document_data.file_path,
                file_size=document_data.file_size,
                mime_type=document_data.mime_type,
                uploaded_by_user_id=current_user.id,
                is_active=document_data.is_active
            )
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            return EmployeeDocumentResponse(
                id=document.id,
                employee_id=document.employee_id,
                document_type=document.document_type,
                file_name=document.file_name,
                file_path=document.file_path,
                file_size=document.file_size,
                mime_type=document.mime_type,
                upload_date=document.upload_date,
                uploaded_by_user_id=document.uploaded_by_user_id,
                is_active=document.is_active,
                created_at=document.created_at,
                updated_at=document.updated_at
            )
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== FULL EMPLOYEE OPERATIONS ====================
    
    @staticmethod
    async def create_employee_full(
        db: AsyncSession, 
        employee_data: EmployeeFullRequest, 
        current_user: User
    ) -> EmployeeFullResponse:
        """Create a complete employee with all related data in one transaction."""
        try:
            # Create basic employee first
            employee = Employee(
                user_id=current_user.id,
                first_name=employee_data.first_name,
                last_name=employee_data.last_name,
                email=employee_data.email,
                phone=employee_data.phone,
                join_date=employee_data.join_date
            )
            db.add(employee)
            await db.flush()  # Generate ID without committing
            await db.refresh(employee)
            
            # Create related data if provided
            personal_details = None
            if employee_data.personal_details:
                personal_details = EmployeePersonalDetails(
                    employee_id=employee.id,
                    gender=employee_data.personal_details.gender,
                    date_of_birth=employee_data.personal_details.date_of_birth,
                    nationality=employee_data.personal_details.nationality,
                    health_care_provider=employee_data.personal_details.health_care_provider,
                    marital_status=employee_data.personal_details.marital_status,
                    personal_tax_id=employee_data.personal_details.personal_tax_id,
                    social_insurance_number=employee_data.personal_details.social_insurance_number,
                    primary_address=employee_data.personal_details.primary_address,
                    city=employee_data.personal_details.city,
                    state=employee_data.personal_details.state,
                    country=employee_data.personal_details.country,
                    postal_code=employee_data.personal_details.postal_code
                )
                db.add(personal_details)
            
            bank_info = None
            if employee_data.bank_info:
                bank_info = EmployeeBankInfo(
                    employee_id=employee.id,
                    bank_name=employee_data.bank_info.bank_name,
                    account_number=employee_data.bank_info.account_number,
                    routing_number=employee_data.bank_info.routing_number,
                    account_type=employee_data.bank_info.account_type,
                    account_holder_name=employee_data.bank_info.account_holder_name,
                    account_holder_type=employee_data.bank_info.account_holder_type,
                    is_primary=employee_data.bank_info.is_primary,
                    is_active=employee_data.bank_info.is_active
                )
                db.add(bank_info)
            
            # Create job timeline entries
            job_timeline = []
            for job_data in employee_data.job_timeline:
                job_entry = EmployeeJobTimeline(
                    employee_id=employee.id,
                    effective_date=job_data.effective_date,
                    end_date=job_data.end_date,
                    job_title=job_data.job_title,
                    position_type=job_data.position_type,
                    employment_type=job_data.employment_type,
                    line_manager_id=job_data.line_manager_id,
                    department=job_data.department,
                    office=job_data.office,
                    is_current=job_data.is_current
                )
                db.add(job_entry)
                job_timeline.append(job_entry)
            
            # Create dependents
            dependents = []
            for dep_data in employee_data.dependents:
                dependent = EmployeeDependent(
                    employee_id=employee.id,
                    name=dep_data.name,
                    relationship_type=dep_data.relationship_type,
                    date_of_birth=dep_data.date_of_birth,
                    gender=dep_data.gender,
                    nationality=dep_data.nationality,
                    primary_address=dep_data.primary_address,
                    city=dep_data.city,
                    state=dep_data.state,
                    country=dep_data.country,
                    postal_code=dep_data.postal_code,
                    is_active=dep_data.is_active
                )
                db.add(dependent)
                dependents.append(dependent)
            
            # Create documents
            documents = []
            for doc_data in employee_data.documents:
                document = EmployeeDocument(
                    employee_id=employee.id,
                    document_type=doc_data.document_type,
                    file_name=doc_data.file_name,
                    file_path=doc_data.file_path,
                    file_size=doc_data.file_size,
                    mime_type=doc_data.mime_type,
                    uploaded_by_user_id=current_user.id,
                    is_active=doc_data.is_active
                )
                db.add(document)
                documents.append(document)
            
            await db.commit()
            
            # Refresh all objects to get IDs and timestamps
            await db.refresh(employee)
            if personal_details:
                await db.refresh(personal_details)
            if bank_info:
                await db.refresh(bank_info)
            for job in job_timeline:
                await db.refresh(job)
            for dep in dependents:
                await db.refresh(dep)
            for doc in documents:
                await db.refresh(doc)
            
            # Build response
            personal_details_response = None
            if personal_details:
                personal_details_response = EmployeePersonalDetailsResponse(
                    id=personal_details.id,
                    employee_id=personal_details.employee_id,
                    gender=personal_details.gender,
                    date_of_birth=personal_details.date_of_birth,
                    nationality=personal_details.nationality,
                    health_care_provider=personal_details.health_care_provider,
                    marital_status=personal_details.marital_status,
                    personal_tax_id=personal_details.personal_tax_id,
                    social_insurance_number=personal_details.social_insurance_number,
                    primary_address=personal_details.primary_address,
                    city=personal_details.city,
                    state=personal_details.state,
                    country=personal_details.country,
                    postal_code=personal_details.postal_code,
                    created_at=personal_details.created_at,
                    updated_at=personal_details.updated_at
                )
            
            bank_info_response = None
            if bank_info:
                bank_info_response = EmployeeBankInfoResponse(
                    id=bank_info.id,
                    employee_id=bank_info.employee_id,
                    bank_name=bank_info.bank_name,
                    account_number=bank_info.account_number,
                    routing_number=bank_info.routing_number,
                    account_type=bank_info.account_type,
                    account_holder_name=bank_info.account_holder_name,
                    account_holder_type=bank_info.account_holder_type,
                    is_primary=bank_info.is_primary,
                    is_active=bank_info.is_active,
                    created_at=bank_info.created_at,
                    updated_at=bank_info.updated_at
                )
            
            job_timeline_response = [
                EmployeeJobTimelineResponse(
                    id=job.id,
                    employee_id=job.employee_id,
                    effective_date=job.effective_date,
                    end_date=job.end_date,
                    job_title=job.job_title,
                    position_type=job.position_type,
                    employment_type=job.employment_type,
                    line_manager_id=job.line_manager_id,
                    department=job.department,
                    office=job.office,
                    is_current=job.is_current,
                    created_at=job.created_at,
                    updated_at=job.updated_at
                ) for job in job_timeline
            ]
            
            dependents_response = [
                EmployeeDependentResponse(
                    id=dep.id,
                    employee_id=dep.employee_id,
                    name=dep.name,
                    relationship_type=dep.relationship_type,
                    date_of_birth=dep.date_of_birth,
                    gender=dep.gender,
                    nationality=dep.nationality,
                    primary_address=dep.primary_address,
                    city=dep.city,
                    state=dep.state,
                    country=dep.country,
                    postal_code=dep.postal_code,
                    is_active=dep.is_active,
                    created_at=dep.created_at,
                    updated_at=dep.updated_at
                ) for dep in dependents
            ]
            
            documents_response = [
                EmployeeDocumentResponse(
                    id=doc.id,
                    employee_id=doc.employee_id,
                    document_type=doc.document_type,
                    file_name=doc.file_name,
                    file_path=doc.file_path,
                    file_size=doc.file_size,
                    mime_type=doc.mime_type,
                    upload_date=doc.upload_date,
                    uploaded_by_user_id=doc.uploaded_by_user_id,
                    is_active=doc.is_active,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at
                ) for doc in documents
            ]
            
            return EmployeeFullResponse(
                id=employee.id,
                user_id=employee.user_id,
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                phone=employee.phone,
                join_date=employee.join_date,
                created_at=employee.created_at,
                updated_at=employee.updated_at,
                personal_details=personal_details_response,
                bank_info=bank_info_response,
                job_timeline=job_timeline_response,
                dependents=dependents_response,
                documents=documents_response
            )
            
        except IntegrityError as e:
            await db.rollback()
            error_msg = str(e.orig).lower()
            if 'unique constraint' in error_msg and 'email' in error_msg:
                raise ValueError("Email already exists")
            else:
                raise ValueError("Employee creation failed")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_employee_full(
        db: AsyncSession, 
        employee_id: int, 
        employee_data: EmployeeFullRequest, 
        current_user: User
    ) -> EmployeeFullResponse:
        """Update a complete employee with all related data in one transaction."""
        try:
            # Verify employee belongs to current user
            employee = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = employee.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Update basic employee info
            employee.first_name = employee_data.first_name
            employee.last_name = employee_data.last_name
            employee.email = employee_data.email
            employee.phone = employee_data.phone
            employee.join_date = employee_data.join_date
            employee.updated_at = datetime.now(timezone.utc)
            
            # Delete existing related data
            existing_personal = await db.execute(
                select(EmployeePersonalDetails).where(EmployeePersonalDetails.employee_id == employee_id)
            )
            for record in existing_personal.scalars():
                await db.delete(record)
            
            existing_bank = await db.execute(
                select(EmployeeBankInfo).where(EmployeeBankInfo.employee_id == employee_id)
            )
            for record in existing_bank.scalars():
                await db.delete(record)
            
            existing_jobs = await db.execute(
                select(EmployeeJobTimeline).where(EmployeeJobTimeline.employee_id == employee_id)
            )
            for record in existing_jobs.scalars():
                await db.delete(record)
            
            existing_deps = await db.execute(
                select(EmployeeDependent).where(EmployeeDependent.employee_id == employee_id)
            )
            for record in existing_deps.scalars():
                await db.delete(record)
            
            existing_docs = await db.execute(
                select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)
            )
            for record in existing_docs.scalars():
                await db.delete(record)
            
            # Create new related data (same logic as create_employee_full)
            personal_details = None
            if employee_data.personal_details:
                personal_details = EmployeePersonalDetails(
                    employee_id=employee.id,
                    gender=employee_data.personal_details.gender,
                    date_of_birth=employee_data.personal_details.date_of_birth,
                    nationality=employee_data.personal_details.nationality,
                    health_care_provider=employee_data.personal_details.health_care_provider,
                    marital_status=employee_data.personal_details.marital_status,
                    personal_tax_id=employee_data.personal_details.personal_tax_id,
                    social_insurance_number=employee_data.personal_details.social_insurance_number,
                    primary_address=employee_data.personal_details.primary_address,
                    city=employee_data.personal_details.city,
                    state=employee_data.personal_details.state,
                    country=employee_data.personal_details.country,
                    postal_code=employee_data.personal_details.postal_code
                )
                db.add(personal_details)
            
            bank_info = None
            if employee_data.bank_info:
                bank_info = EmployeeBankInfo(
                    employee_id=employee.id,
                    bank_name=employee_data.bank_info.bank_name,
                    account_number=employee_data.bank_info.account_number,
                    routing_number=employee_data.bank_info.routing_number,
                    account_type=employee_data.bank_info.account_type,
                    account_holder_name=employee_data.bank_info.account_holder_name,
                    account_holder_type=employee_data.bank_info.account_holder_type,
                    is_primary=employee_data.bank_info.is_primary,
                    is_active=employee_data.bank_info.is_active
                )
                db.add(bank_info)
            
            # Create job timeline entries
            job_timeline = []
            for job_data in employee_data.job_timeline:
                job_entry = EmployeeJobTimeline(
                    employee_id=employee.id,
                    effective_date=job_data.effective_date,
                    end_date=job_data.end_date,
                    job_title=job_data.job_title,
                    position_type=job_data.position_type,
                    employment_type=job_data.employment_type,
                    line_manager_id=job_data.line_manager_id,
                    department=job_data.department,
                    office=job_data.office,
                    is_current=job_data.is_current
                )
                db.add(job_entry)
                job_timeline.append(job_entry)
            
            # Create dependents
            dependents = []
            for dep_data in employee_data.dependents:
                dependent = EmployeeDependent(
                    employee_id=employee.id,
                    name=dep_data.name,
                    relationship_type=dep_data.relationship_type,
                    date_of_birth=dep_data.date_of_birth,
                    gender=dep_data.gender,
                    nationality=dep_data.nationality,
                    primary_address=dep_data.primary_address,
                    city=dep_data.city,
                    state=dep_data.state,
                    country=dep_data.country,
                    postal_code=dep_data.postal_code,
                    is_active=dep_data.is_active
                )
                db.add(dependent)
                dependents.append(dependent)
            
            # Create documents
            documents = []
            for doc_data in employee_data.documents:
                document = EmployeeDocument(
                    employee_id=employee.id,
                    document_type=doc_data.document_type,
                    file_name=doc_data.file_name,
                    file_path=doc_data.file_path,
                    file_size=doc_data.file_size,
                    mime_type=doc_data.mime_type,
                    uploaded_by_user_id=current_user.id,
                    is_active=doc_data.is_active
                )
                db.add(document)
                documents.append(document)
            
            await db.commit()
            
            # Refresh all objects to get IDs and timestamps
            await db.refresh(employee)
            if personal_details:
                await db.refresh(personal_details)
            if bank_info:
                await db.refresh(bank_info)
            for job in job_timeline:
                await db.refresh(job)
            for dep in dependents:
                await db.refresh(dep)
            for doc in documents:
                await db.refresh(doc)
            
            # Build response (same as create_employee_full)
            personal_details_response = None
            if personal_details:
                personal_details_response = EmployeePersonalDetailsResponse(
                    id=personal_details.id,
                    employee_id=personal_details.employee_id,
                    gender=personal_details.gender,
                    date_of_birth=personal_details.date_of_birth,
                    nationality=personal_details.nationality,
                    health_care_provider=personal_details.health_care_provider,
                    marital_status=personal_details.marital_status,
                    personal_tax_id=personal_details.personal_tax_id,
                    social_insurance_number=personal_details.social_insurance_number,
                    primary_address=personal_details.primary_address,
                    city=personal_details.city,
                    state=personal_details.state,
                    country=personal_details.country,
                    postal_code=personal_details.postal_code,
                    created_at=personal_details.created_at,
                    updated_at=personal_details.updated_at
                )
            
            bank_info_response = None
            if bank_info:
                bank_info_response = EmployeeBankInfoResponse(
                    id=bank_info.id,
                    employee_id=bank_info.employee_id,
                    bank_name=bank_info.bank_name,
                    account_number=bank_info.account_number,
                    routing_number=bank_info.routing_number,
                    account_type=bank_info.account_type,
                    account_holder_name=bank_info.account_holder_name,
                    account_holder_type=bank_info.account_holder_type,
                    is_primary=bank_info.is_primary,
                    is_active=bank_info.is_active,
                    created_at=bank_info.created_at,
                    updated_at=bank_info.updated_at
                )
            
            job_timeline_response = [
                EmployeeJobTimelineResponse(
                    id=job.id,
                    employee_id=job.employee_id,
                    effective_date=job.effective_date,
                    end_date=job.end_date,
                    job_title=job.job_title,
                    position_type=job.position_type,
                    employment_type=job.employment_type,
                    line_manager_id=job.line_manager_id,
                    department=job.department,
                    office=job.office,
                    is_current=job.is_current,
                    created_at=job.created_at,
                    updated_at=job.updated_at
                ) for job in job_timeline
            ]
            
            dependents_response = [
                EmployeeDependentResponse(
                    id=dep.id,
                    employee_id=dep.employee_id,
                    name=dep.name,
                    relationship_type=dep.relationship_type,
                    date_of_birth=dep.date_of_birth,
                    gender=dep.gender,
                    nationality=dep.nationality,
                    primary_address=dep.primary_address,
                    city=dep.city,
                    state=dep.state,
                    country=dep.country,
                    postal_code=dep.postal_code,
                    is_active=dep.is_active,
                    created_at=dep.created_at,
                    updated_at=dep.updated_at
                ) for dep in dependents
            ]
            
            documents_response = [
                EmployeeDocumentResponse(
                    id=doc.id,
                    employee_id=doc.employee_id,
                    document_type=doc.document_type,
                    file_name=doc.file_name,
                    file_path=doc.file_path,
                    file_size=doc.file_size,
                    mime_type=doc.mime_type,
                    upload_date=doc.upload_date,
                    uploaded_by_user_id=doc.uploaded_by_user_id,
                    is_active=doc.is_active,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at
                ) for doc in documents
            ]
            
            return EmployeeFullResponse(
                id=employee.id,
                user_id=employee.user_id,
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                phone=employee.phone,
                join_date=employee.join_date,
                created_at=employee.created_at,
                updated_at=employee.updated_at,
                personal_details=personal_details_response,
                bank_info=bank_info_response,
                job_timeline=job_timeline_response,
                dependents=dependents_response,
                documents=documents_response
            )
            
        except IntegrityError as e:
            await db.rollback()
            error_msg = str(e.orig).lower()
            if 'unique constraint' in error_msg and 'email' in error_msg:
                raise ValueError("Email already exists")
            else:
                raise ValueError("Employee update failed")
        except ValueError as e:
            await db.rollback()
            raise e
        except Exception as e:
            await db.rollback()
            raise e
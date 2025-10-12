from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, delete
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone

from schemas.employee import (
    EmployeeRequest, EmployeeResponse, EmployeeFullResponse, EmployeeFullRequest,
    EmployeePartialUpdateRequest, EmployeePartialFullUpdateRequest,
    EmployeePersonalDetailsRequest, EmployeePersonalDetailsResponse, EmployeePersonalDetailsPublicResponse,
    EmployeeJobTimelineRequest, EmployeeJobTimelineResponse,
    EmployeeContractTimelineRequest, EmployeeContractTimelineResponse,
    EmployeeWorkScheduleRequest, EmployeeWorkScheduleResponse,
    EmployeePayrollRecordRequest, EmployeePayrollRecordResponse, EmployeePayrollItemResponse,
    EmployeeBankInfoRequest, EmployeeBankInfoResponse, EmployeeBankInfoPublicResponse,
    EmployeeDependentRequest, EmployeeDependentResponse,
    EmployeeDocumentRequest, EmployeeDocumentResponse, EmployeeDocumentPublicResponse,
    # New payroll schemas
    EmployeeOneOffPaymentRequest, EmployeeOneOffPaymentResponse,
    EmployeeTimeOffRequest, EmployeeTimeOffResponse,
    EmployeeOvertimeRequest, EmployeeOvertimeResponse,
    EmployeeDeficitRequest, EmployeeDeficitResponse,
    EmployeeAttendanceRequest, EmployeeAttendanceResponse
)
from models.employee import (
    Employee, EmployeePersonalDetails, EmployeeJobTimeline, EmployeeContractTimeline,
    EmployeeWorkSchedule, EmployeePayrollRecord, EmployeePayrollItem,
    EmployeeBankInfo, EmployeeDependent, EmployeeDocument,
    # New payroll models
    EmployeeOneOffPayment, EmployeeTimeOff, EmployeeOvertime, EmployeeDeficit, EmployeeAttendance
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
        """Get an employee by ID with job timeline data."""
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.job_timeline))
            .where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        employee = result.scalar_one_or_none()
        if not employee:
            return None
        
        # Get current job timeline (is_current=True)
        current_job = None
        line_manager_name = None
        
        if employee.job_timeline:
            current_job = next((job for job in employee.job_timeline if job.is_current), None)
            
            # If no current job found, get the most recent one
            if not current_job and employee.job_timeline:
                current_job = max(employee.job_timeline, key=lambda x: x.effective_date)
            
            # Get line manager name if line_manager_id exists
            if current_job and current_job.line_manager_id:
                manager_result = await db.execute(
                    select(Employee).where(
                        and_(
                            Employee.id == current_job.line_manager_id,
                            Employee.user_id == current_user.id
                        )
                    )
                )
                manager = manager_result.scalar_one_or_none()
                if manager:
                    line_manager_name = f"{manager.first_name} {manager.last_name}"
        
        return EmployeeResponse(
            id=employee.id,
            user_id=employee.user_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
            join_date=employee.join_date,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            job_title=current_job.job_title if current_job else None,
            department=current_job.department if current_job else None,
            office=current_job.office if current_job else None,
            line_manager_id=current_job.line_manager_id if current_job else None,
            line_manager_name=line_manager_name,
            employment_status=employee.employment_status or "ACTIVE"  # Use actual status or default
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
                selectinload(Employee.contract_timeline),
                selectinload(Employee.work_schedule),
                selectinload(Employee.payroll_records).selectinload(EmployeePayrollRecord.payroll_items),
                selectinload(Employee.dependents),
                selectinload(Employee.documents),
                # New payroll relationships
                selectinload(Employee.one_off_payments),
                selectinload(Employee.time_off_records),
                selectinload(Employee.overtime_records),
                selectinload(Employee.deficit_records),
                selectinload(Employee.attendance_records)
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
            # Create full response first, then convert to public response with masked data
            full_personal_details = EmployeePersonalDetailsResponse(
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
            personal_details = EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)
        
        bank_info = None
        if employee.bank_info:
            # Create full response first, then convert to public response with masked data
            full_bank_info = EmployeeBankInfoResponse(
                id=employee.bank_info.id,
                employee_id=employee.bank_info.employee_id,
                bank_name=employee.bank_info.bank_name,
                branch=employee.bank_info.branch,
                swift_bic=employee.bank_info.swift_bic,
                account_number=employee.bank_info.account_number,
                routing_number=employee.bank_info.routing_number,
                iban=employee.bank_info.iban,
                account_type=employee.bank_info.account_type,
                account_holder_name=employee.bank_info.account_holder_name,
                account_holder_type=employee.bank_info.account_holder_type,
                is_primary=employee.bank_info.is_primary,
                is_active=employee.bank_info.is_active,
                created_at=employee.bank_info.created_at,
                updated_at=employee.bank_info.updated_at
            )
            bank_info = EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)
        
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
        
        contract_timeline = [
            EmployeeContractTimelineResponse(
                id=contract.id,
                employee_id=contract.employee_id,
                contract_number=contract.contract_number,
                contract_name=contract.contract_name,
                contract_type=contract.contract_type,
                start_date=contract.start_date,
                end_date=contract.end_date,
                is_active=contract.is_active,
                created_at=contract.created_at,
                updated_at=contract.updated_at
            ) for contract in employee.contract_timeline
        ]
        
        work_schedule = [
            EmployeeWorkScheduleResponse(
                id=schedule.id,
                employee_id=schedule.employee_id,
                effective_from=schedule.effective_from,
                effective_to=schedule.effective_to,
                schedule_type=schedule.schedule_type,
                standard_hours_per_day=schedule.standard_hours_per_day,
                total_hours_per_week=schedule.total_hours_per_week,
                monday_hours=schedule.monday_hours,
                tuesday_hours=schedule.tuesday_hours,
                wednesday_hours=schedule.wednesday_hours,
                thursday_hours=schedule.thursday_hours,
                friday_hours=schedule.friday_hours,
                saturday_hours=schedule.saturday_hours,
                sunday_hours=schedule.sunday_hours,
                is_current=schedule.is_current,
                created_at=schedule.created_at,
                updated_at=schedule.updated_at
            ) for schedule in employee.work_schedule
        ]
        
        payroll_records = [
            EmployeePayrollRecordResponse(
                id=record.id,
                employee_id=record.employee_id,
                period_start=record.period_start,
                period_end=record.period_end,
                base_salary=record.base_salary,
                total_compensation=record.total_compensation,
                status=record.status,
                payment_date=record.payment_date,
                payroll_items=[
                    EmployeePayrollItemResponse(
                        id=item.id,
                        payroll_record_id=item.payroll_record_id,
                        category=item.category,
                        item_type=item.item_type,
                        description=item.description,
                        amount=item.amount,
                        currency=item.currency,
                        quantity=item.quantity,
                        rate=item.rate,
                        meta_data=item.meta_data,
                        created_at=item.created_at,
                        updated_at=item.updated_at
                    ) for item in record.payroll_items
                ],
                created_at=record.created_at,
                updated_at=record.updated_at
            ) for record in employee.payroll_records
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
        
        documents = []
        for doc in employee.documents:
            # Create full response first, then convert to public response with masked data
            full_document = EmployeeDocumentResponse(
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
            )
            documents.append(EmployeeDocumentPublicResponse.from_full_response(full_document))
        
        # Process new payroll data
        one_off_payments = [
            EmployeeOneOffPaymentResponse(
                id=payment.id,
                employee_id=payment.employee_id,
                payroll_record_id=payment.payroll_record_id,
                item_name=payment.item_name,
                item_type=payment.item_type,
                amount=payment.amount,
                currency=payment.currency,
                payment_date=payment.payment_date,
                description=payment.description,
                meta_data=payment.meta_data,
                created_at=payment.created_at,
                updated_at=payment.updated_at
            ) for payment in employee.one_off_payments
        ]
        
        time_off_records = [
            EmployeeTimeOffResponse(
                id=record.id,
                employee_id=record.employee_id,
                time_off_type=record.time_off_type,
                days_used=record.days_used,
                days_remaining=record.days_remaining,
                amount=record.amount,
                currency=record.currency,
                period_start=record.period_start,
                period_end=record.period_end,
                description=record.description,
                meta_data=record.meta_data,
                created_at=record.created_at,
                updated_at=record.updated_at
            ) for record in employee.time_off_records
        ]
        
        overtime_records = [
            EmployeeOvertimeResponse(
                id=record.id,
                employee_id=record.employee_id,
                payroll_record_id=record.payroll_record_id,
                overtime_date=record.overtime_date,
                hours=record.hours,
                rate=record.rate,
                amount=record.amount,
                currency=record.currency,
                overtime_type=record.overtime_type,
                description=record.description,
                meta_data=record.meta_data,
                created_at=record.created_at,
                updated_at=record.updated_at
            ) for record in employee.overtime_records
        ]
        
        deficit_records = [
            EmployeeDeficitResponse(
                id=record.id,
                employee_id=record.employee_id,
                payroll_record_id=record.payroll_record_id,
                deficit_type=record.deficit_type,
                deficit_hours=record.deficit_hours,
                deficit_amount=record.deficit_amount,
                currency=record.currency,
                period_start=record.period_start,
                period_end=record.period_end,
                description=record.description,
                meta_data=record.meta_data,
                created_at=record.created_at,
                updated_at=record.updated_at
            ) for record in employee.deficit_records
        ]
        
        attendance_records = [
            EmployeeAttendanceResponse(
                id=record.id,
                employee_id=record.employee_id,
                payroll_record_id=record.payroll_record_id,
                period=record.period,
                expected_hours=record.expected_hours,
                actual_work_hours=record.actual_work_hours,
                period_start=record.period_start,
                period_end=record.period_end,
                description=record.description,
                meta_data=record.meta_data,
                created_at=record.created_at,
                updated_at=record.updated_at
            ) for record in employee.attendance_records
        ]
        
        return EmployeeFullResponse(
            id=employee.id,
            user_id=employee.user_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
            join_date=employee.join_date,
            employment_status=employee.employment_status or "ACTIVE",
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            personal_details=personal_details,
            bank_info=bank_info,
            job_timeline=job_timeline,
            contract_timeline=contract_timeline,
            work_schedule=work_schedule,
            payroll_records=payroll_records,
            dependents=dependents,
            documents=documents,
            # New payroll fields
            one_off_payments=one_off_payments,
            time_off_records=time_off_records,
            overtime_records=overtime_records,
            deficit_records=deficit_records,
            attendance_records=attendance_records
        )

    @staticmethod
    async def list_employees(db: AsyncSession, current_user: User, skip: int = 0, limit: int = 100) -> List[EmployeeResponse]:
        """List all employees for the current user with job timeline data."""
        # Get employees with their current job timeline
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.job_timeline))
            .where(Employee.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        employees = result.scalars().all()
        
        employee_responses = []
        for emp in employees:
            # Get current job timeline (is_current=True)
            current_job = None
            line_manager_name = None
            
            if emp.job_timeline:
                current_job = next((job for job in emp.job_timeline if job.is_current), None)
                
                # If no current job found, get the most recent one
                if not current_job and emp.job_timeline:
                    current_job = max(emp.job_timeline, key=lambda x: x.effective_date)
                
                # Get line manager name if line_manager_id exists
                if current_job and current_job.line_manager_id:
                    manager_result = await db.execute(
                        select(Employee).where(
                            and_(
                                Employee.id == current_job.line_manager_id,
                                Employee.user_id == current_user.id
                            )
                        )
                    )
                    manager = manager_result.scalar_one_or_none()
                    if manager:
                        line_manager_name = f"{manager.first_name} {manager.last_name}"
            
            employee_responses.append(EmployeeResponse(
                id=emp.id,
                user_id=emp.user_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                phone=emp.phone,
                join_date=emp.join_date,
                created_at=emp.created_at,
                updated_at=emp.updated_at,
                job_title=current_job.job_title if current_job else None,
                department=current_job.department if current_job else None,
                office=current_job.office if current_job else None,
                line_manager_id=current_job.line_manager_id if current_job else None,
                line_manager_name=line_manager_name,
                employment_status=emp.employment_status or "ACTIVE"  # Use actual status or default
            ))
        
        return employee_responses

    @staticmethod
    async def delete_employee(db: AsyncSession, employee_id: int, current_user: User) -> bool:
        """Delete an employee and all related data."""
        try:
            # First, get the employee to ensure it exists and belongs to the user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            
            if not employee:
                return False
            
            # Delete all related data first (cascade delete)
            # Delete personal details
            personal_details_result = await db.execute(
                select(EmployeePersonalDetails).where(EmployeePersonalDetails.employee_id == employee_id)
            )
            personal_details = personal_details_result.scalars().all()
            for detail in personal_details:
                await db.delete(detail)
            
            # Delete bank info
            bank_info_result = await db.execute(
                select(EmployeeBankInfo).where(EmployeeBankInfo.employee_id == employee_id)
            )
            bank_infos = bank_info_result.scalars().all()
            for bank_info in bank_infos:
                await db.delete(bank_info)
            
            # Delete job timeline
            job_timeline_result = await db.execute(
                select(EmployeeJobTimeline).where(EmployeeJobTimeline.employee_id == employee_id)
            )
            job_timelines = job_timeline_result.scalars().all()
            for timeline in job_timelines:
                await db.delete(timeline)
            
            # Delete dependents
            dependents_result = await db.execute(
                select(EmployeeDependent).where(EmployeeDependent.employee_id == employee_id)
            )
            dependents = dependents_result.scalars().all()
            for dependent in dependents:
                await db.delete(dependent)
            
            # Delete documents
            documents_result = await db.execute(
                select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)
            )
            documents = documents_result.scalars().all()
            for document in documents:
                await db.delete(document)
            
            # Finally, delete the employee
            await db.delete(employee)
            await db.commit()
            
            return True
            
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== PERSONAL DETAILS ====================
    
    @staticmethod
    async def create_personal_details(
        db: AsyncSession, 
        employee_id: int, 
        personal_data: EmployeePersonalDetailsRequest, 
        current_user: User
    ) -> EmployeePersonalDetailsPublicResponse:
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
            
            # Create full response first, then convert to public response with masked data
            full_personal_details = EmployeePersonalDetailsResponse(
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
            return EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Personal details already exist for this employee")
        except Exception as e:
            raise e

    @staticmethod
    async def get_personal_details(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> Optional[EmployeePersonalDetailsPublicResponse]:
        """
        Get personal details for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            current_user: Current authenticated user
            
        Returns:
            EmployeePersonalDetailsResponse if found, None otherwise
        """
        # Verify employee belongs to current user and get personal details
        result = await db.execute(
            select(EmployeePersonalDetails)
            .join(Employee)
            .where(
                and_(
                    EmployeePersonalDetails.employee_id == employee_id,
                    Employee.user_id == current_user.id
                )
            )
        )
        personal_details = result.scalar_one_or_none()
        
        if not personal_details:
            return None
        
        # Create full response first, then convert to public response with masked data
        full_personal_details = EmployeePersonalDetailsResponse(
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
        return EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)

    @staticmethod
    async def update_personal_details(
        db: AsyncSession, 
        employee_id: int, 
        personal_data: EmployeePersonalDetailsRequest, 
        current_user: User
    ) -> EmployeePersonalDetailsPublicResponse:
        """
        Update personal details for an employee (full replacement).
        
        Args:
            db: Database session
            employee_id: ID of the employee
            personal_data: New personal details data
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeePersonalDetailsResponse
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing personal details
            result = await db.execute(
                select(EmployeePersonalDetails).where(
                    EmployeePersonalDetails.employee_id == employee_id
                )
            )
            existing_personal = result.scalar_one_or_none()
            
            if existing_personal:
                # Update existing record
                existing_personal.gender = personal_data.gender
                existing_personal.date_of_birth = personal_data.date_of_birth
                existing_personal.nationality = personal_data.nationality
                existing_personal.health_care_provider = personal_data.health_care_provider
                existing_personal.marital_status = personal_data.marital_status
                existing_personal.personal_tax_id = personal_data.personal_tax_id
                existing_personal.social_insurance_number = personal_data.social_insurance_number
                existing_personal.primary_address = personal_data.primary_address
                existing_personal.city = personal_data.city
                existing_personal.state = personal_data.state
                existing_personal.country = personal_data.country
                existing_personal.postal_code = personal_data.postal_code
                existing_personal.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                await db.refresh(existing_personal)
                personal_details = existing_personal
            else:
                # Create new record
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
            
            # Create full response first, then convert to public response with masked data
            full_personal_details = EmployeePersonalDetailsResponse(
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
            return EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)
            
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Personal details update failed")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def partial_update_personal_details(
        db: AsyncSession, 
        employee_id: int, 
        personal_data: EmployeePersonalDetailsRequest, 
        current_user: User
    ) -> EmployeePersonalDetailsPublicResponse:
        """
        Partially update personal details for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            personal_data: Partial personal details data (only provided fields will be updated)
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeePersonalDetailsResponse
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing personal details
            result = await db.execute(
                select(EmployeePersonalDetails).where(
                    EmployeePersonalDetails.employee_id == employee_id
                )
            )
            existing_personal = result.scalar_one_or_none()
            
            if not existing_personal:
                raise ValueError("Personal details not found for this employee")
            
            # Update only provided fields
            update_data = personal_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(existing_personal, field):
                    setattr(existing_personal, field, value)
            
            existing_personal.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(existing_personal)
            
            # Create full response first, then convert to public response with masked data
            full_personal_details = EmployeePersonalDetailsResponse(
                id=existing_personal.id,
                employee_id=existing_personal.employee_id,
                gender=existing_personal.gender,
                date_of_birth=existing_personal.date_of_birth,
                nationality=existing_personal.nationality,
                health_care_provider=existing_personal.health_care_provider,
                marital_status=existing_personal.marital_status,
                personal_tax_id=existing_personal.personal_tax_id,
                social_insurance_number=existing_personal.social_insurance_number,
                primary_address=existing_personal.primary_address,
                city=existing_personal.city,
                state=existing_personal.state,
                country=existing_personal.country,
                postal_code=existing_personal.postal_code,
                created_at=existing_personal.created_at,
                updated_at=existing_personal.updated_at
            )
            return EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)
            
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_personal_details(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> bool:
        """
        Delete personal details for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            current_user: Current authenticated user
            
        Returns:
            True if deleted, False if not found
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            return False  # Employee not found or access denied
        
        try:
            # Get existing personal details
            result = await db.execute(
                select(EmployeePersonalDetails).where(
                    EmployeePersonalDetails.employee_id == employee_id
                )
            )
            existing_personal = result.scalar_one_or_none()
            
            if not existing_personal:
                return False
            
            # Delete the personal details record
            await db.delete(existing_personal)
            await db.commit()
            
            return True
            
        except Exception as e:
            await db.rollback()
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
            # Tenant safety: ensure line_manager_id (if provided) belongs to current_user
            if job_data.line_manager_id is not None:
                mgr = await db.execute(
                    select(Employee).where(
                        and_(Employee.id == job_data.line_manager_id, Employee.user_id == current_user.id)
                    )
                )
                if not mgr.scalar_one_or_none():
                    raise ValueError("line_manager_id not found or access denied")
            
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

    @staticmethod
    async def get_job_timeline(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeJobTimelineResponse]:
        """Get all job timeline entries for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get all job timeline entries
        result = await db.execute(
            select(EmployeeJobTimeline)
            .where(EmployeeJobTimeline.employee_id == employee_id)
            .order_by(EmployeeJobTimeline.effective_date.desc())
        )
        job_timelines = result.scalars().all()
        
        return [
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
            )
            for job in job_timelines
        ]

    @staticmethod
    async def update_job_timeline(
        db: AsyncSession, 
        employee_id: int, 
        job_id: int, 
        job_data: EmployeeJobTimelineRequest, 
        current_user: User
    ) -> EmployeeJobTimelineResponse:
        """Update a job timeline entry for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get the job timeline entry
        result = await db.execute(
            select(EmployeeJobTimeline).where(
                and_(
                    EmployeeJobTimeline.id == job_id,
                    EmployeeJobTimeline.employee_id == employee_id
                )
            )
        )
        job_timeline = result.scalar_one_or_none()
        if not job_timeline:
            raise ValueError("Job timeline entry not found")
        
        try:
            # Tenant safety: ensure line_manager_id (if provided) belongs to current_user
            if job_data.line_manager_id is not None:
                mgr = await db.execute(
                    select(Employee).where(
                        and_(
                            Employee.id == job_data.line_manager_id,
                            Employee.user_id == current_user.id
                        )
                    )
                )
                if not mgr.scalar_one_or_none():
                    raise ValueError("line_manager_id not found or access denied")
            
            # If this is the current job, deactivate other current jobs
            if job_data.is_current:
                existing_jobs = await db.execute(
                    select(EmployeeJobTimeline).where(
                        and_(
                            EmployeeJobTimeline.employee_id == employee_id,
                            EmployeeJobTimeline.is_current == True,
                            EmployeeJobTimeline.id != job_id
                        )
                    )
                )
                for job in existing_jobs.scalars():
                    job.is_current = False
            
            # Update the job timeline entry
            job_timeline.effective_date = job_data.effective_date
            job_timeline.end_date = job_data.end_date
            job_timeline.job_title = job_data.job_title
            job_timeline.position_type = job_data.position_type
            job_timeline.employment_type = job_data.employment_type
            job_timeline.line_manager_id = job_data.line_manager_id
            job_timeline.department = job_data.department
            job_timeline.office = job_data.office
            job_timeline.is_current = job_data.is_current
            job_timeline.updated_at = datetime.now(timezone.utc)
            
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

    @staticmethod
    async def delete_job_timeline(
        db: AsyncSession, 
        employee_id: int, 
        job_id: int, 
        current_user: User
    ):
        """Delete a job timeline entry for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get the job timeline entry
        result = await db.execute(
            select(EmployeeJobTimeline).where(
                and_(
                    EmployeeJobTimeline.id == job_id,
                    EmployeeJobTimeline.employee_id == employee_id
                )
            )
        )
        job_timeline = result.scalar_one_or_none()
        if not job_timeline:
            raise ValueError("Job timeline entry not found")
        
        try:
            await db.delete(job_timeline)
            await db.commit()
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
    ) -> EmployeeBankInfoPublicResponse:
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
            # Validate required fields for bank info create
            required = ["bank_name", "account_number", "routing_number", "account_type", "account_holder_name", "account_holder_type"]
            missing = [f for f in required if getattr(bank_data, f) is None or getattr(bank_data, f) == ""]
            if missing:
                raise ValueError(f"Missing required bank_info fields: {', '.join(missing)}")
            
            bank_info = EmployeeBankInfo(
                employee_id=employee_id,
                bank_name=bank_data.bank_name,
                account_number=bank_data.account_number,
                routing_number=bank_data.routing_number,
                account_type=bank_data.account_type,
                account_holder_name=bank_data.account_holder_name,
                account_holder_type=bank_data.account_holder_type,
                is_primary=True if bank_data.is_primary is None else bank_data.is_primary,
                is_active=True if bank_data.is_active is None else bank_data.is_active
            )
            db.add(bank_info)
            await db.commit()
            await db.refresh(bank_info)
            
            # Create full response first, then convert to public response with masked data
            full_bank_info = EmployeeBankInfoResponse(
                id=bank_info.id,
                employee_id=bank_info.employee_id,
                bank_name=bank_info.bank_name,
                branch=bank_info.branch,
                swift_bic=bank_info.swift_bic,
                account_number=bank_info.account_number,
                routing_number=bank_info.routing_number,
                iban=bank_info.iban,
                account_type=bank_info.account_type,
                account_holder_name=bank_info.account_holder_name,
                account_holder_type=bank_info.account_holder_type,
                is_primary=bank_info.is_primary,
                is_active=bank_info.is_active,
                created_at=bank_info.created_at,
                updated_at=bank_info.updated_at
            )
            return EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Bank info already exists for this employee")
        except Exception as e:
            raise e

    @staticmethod
    async def get_bank_info(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> Optional[EmployeeBankInfoPublicResponse]:
        """
        Get bank information for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            current_user: Current authenticated user
            
        Returns:
            EmployeeBankInfoResponse if found, None otherwise
        """
        # Verify employee belongs to current user and get bank info
        result = await db.execute(
            select(EmployeeBankInfo)
            .join(Employee)
            .where(
                and_(
                    EmployeeBankInfo.employee_id == employee_id,
                    Employee.user_id == current_user.id
                )
            )
        )
        bank_info = result.scalar_one_or_none()
        
        if not bank_info:
            return None
        
        # Create full response first, then convert to public response with masked data
        full_bank_info = EmployeeBankInfoResponse(
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
        return EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)

    @staticmethod
    async def update_bank_info(
        db: AsyncSession, 
        employee_id: int, 
        bank_data: EmployeeBankInfoRequest, 
        current_user: User
    ) -> EmployeeBankInfoPublicResponse:
        """
        Update bank information for an employee (full replacement).
        
        Args:
            db: Database session
            employee_id: ID of the employee
            bank_data: New bank information data
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeeBankInfoResponse
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing bank info
            result = await db.execute(
                select(EmployeeBankInfo).where(
                    EmployeeBankInfo.employee_id == employee_id
                )
            )
            existing_bank = result.scalar_one_or_none()
            
            if existing_bank:
                # Update existing record
                existing_bank.bank_name = bank_data.bank_name
                existing_bank.branch = bank_data.branch
                existing_bank.swift_bic = bank_data.swift_bic
                existing_bank.account_number = bank_data.account_number
                existing_bank.routing_number = bank_data.routing_number
                existing_bank.iban = bank_data.iban
                existing_bank.account_type = bank_data.account_type
                existing_bank.account_holder_name = bank_data.account_holder_name
                existing_bank.account_holder_type = bank_data.account_holder_type
                existing_bank.is_primary = bank_data.is_primary
                existing_bank.is_active = bank_data.is_active
                existing_bank.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                await db.refresh(existing_bank)
                bank_info = existing_bank
            else:
                # Create new record - validate required fields
                required = ["bank_name", "account_number", "routing_number", "account_type", "account_holder_name", "account_holder_type"]
                missing = [f for f in required if getattr(bank_data, f) is None or getattr(bank_data, f) == ""]
                if missing:
                    raise ValueError(f"Missing required bank_info fields: {', '.join(missing)}")
                
                bank_info = EmployeeBankInfo(
                    employee_id=employee_id,
                    bank_name=bank_data.bank_name,
                    branch=bank_data.branch,
                    swift_bic=bank_data.swift_bic,
                    account_number=bank_data.account_number,
                    routing_number=bank_data.routing_number,
                    iban=bank_data.iban,
                    account_type=bank_data.account_type,
                    account_holder_name=bank_data.account_holder_name,
                    account_holder_type=bank_data.account_holder_type,
                    is_primary=True if bank_data.is_primary is None else bank_data.is_primary,
                    is_active=True if bank_data.is_active is None else bank_data.is_active
                )
                db.add(bank_info)
                await db.commit()
                await db.refresh(bank_info)
            
            # Create full response first, then convert to public response with masked data
            full_bank_info = EmployeeBankInfoResponse(
                id=bank_info.id,
                employee_id=bank_info.employee_id,
                bank_name=bank_info.bank_name,
                branch=bank_info.branch,
                swift_bic=bank_info.swift_bic,
                account_number=bank_info.account_number,
                routing_number=bank_info.routing_number,
                iban=bank_info.iban,
                account_type=bank_info.account_type,
                account_holder_name=bank_info.account_holder_name,
                account_holder_type=bank_info.account_holder_type,
                is_primary=bank_info.is_primary,
                is_active=bank_info.is_active,
                created_at=bank_info.created_at,
                updated_at=bank_info.updated_at
            )
            return EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)
            
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Bank information update failed")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def partial_update_bank_info(
        db: AsyncSession, 
        employee_id: int, 
        bank_data: EmployeeBankInfoRequest, 
        current_user: User
    ) -> EmployeeBankInfoPublicResponse:
        """
        Partially update bank information for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            bank_data: Partial bank information data (only provided fields will be updated)
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeeBankInfoResponse
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing bank info
            result = await db.execute(
                select(EmployeeBankInfo).where(
                    EmployeeBankInfo.employee_id == employee_id
                )
            )
            existing_bank = result.scalar_one_or_none()
            
            if not existing_bank:
                raise ValueError("Bank information not found for this employee")
            
            # Update only provided fields
            update_data = bank_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(existing_bank, field):
                    setattr(existing_bank, field, value)
            
            existing_bank.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(existing_bank)
            
            # Create full response first, then convert to public response with masked data
            full_bank_info = EmployeeBankInfoResponse(
                id=existing_bank.id,
                employee_id=existing_bank.employee_id,
                bank_name=existing_bank.bank_name,
                branch=existing_bank.branch,
                swift_bic=existing_bank.swift_bic,
                account_number=existing_bank.account_number,
                routing_number=existing_bank.routing_number,
                iban=existing_bank.iban,
                account_type=existing_bank.account_type,
                account_holder_name=existing_bank.account_holder_name,
                account_holder_type=existing_bank.account_holder_type,
                is_primary=existing_bank.is_primary,
                is_active=existing_bank.is_active,
                created_at=existing_bank.created_at,
                updated_at=existing_bank.updated_at
            )
            return EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)
            
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_bank_info(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> bool:
        """
        Delete bank information for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            current_user: Current authenticated user
            
        Returns:
            True if deleted, False if not found
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing bank info
            result = await db.execute(
                select(EmployeeBankInfo).where(
                    EmployeeBankInfo.employee_id == employee_id
                )
            )
            existing_bank = result.scalar_one_or_none()
            
            if not existing_bank:
                return False
            
            # Delete the bank info record
            await db.delete(existing_bank)
            await db.commit()
            
            return True
            
        except Exception as e:
            await db.rollback()
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

    @staticmethod
    async def get_dependents(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeDependentResponse]:
        """Get all dependents for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get all dependents for the employee
        result = await db.execute(
            select(EmployeeDependent)
            .where(EmployeeDependent.employee_id == employee_id)
            .order_by(EmployeeDependent.created_at.desc())
        )
        dependents = result.scalars().all()
        
        return [
            EmployeeDependentResponse(
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
            ) for dependent in dependents
        ]

    @staticmethod
    async def get_dependent(
        db: AsyncSession, 
        employee_id: int, 
        dependent_id: int, 
        current_user: User
    ) -> Optional[EmployeeDependentResponse]:
        """Get a specific dependent for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get the specific dependent
        result = await db.execute(
            select(EmployeeDependent).where(
                and_(
                    EmployeeDependent.id == dependent_id,
                    EmployeeDependent.employee_id == employee_id
                )
            )
        )
        dependent = result.scalar_one_or_none()
        
        if not dependent:
            return None
        
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

    @staticmethod
    async def update_dependent(
        db: AsyncSession, 
        employee_id: int, 
        dependent_id: int, 
        dependent_data: EmployeeDependentRequest, 
        current_user: User
    ) -> Optional[EmployeeDependentResponse]:
        """Update a dependent for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get the specific dependent
        result = await db.execute(
            select(EmployeeDependent).where(
                and_(
                    EmployeeDependent.id == dependent_id,
                    EmployeeDependent.employee_id == employee_id
                )
            )
        )
        dependent = result.scalar_one_or_none()
        
        if not dependent:
            return None
        
        try:
            # Update the dependent fields
            dependent.name = dependent_data.name
            dependent.relationship_type = dependent_data.relationship_type
            dependent.date_of_birth = dependent_data.date_of_birth
            dependent.gender = dependent_data.gender
            dependent.nationality = dependent_data.nationality
            dependent.primary_address = dependent_data.primary_address
            dependent.city = dependent_data.city
            dependent.state = dependent_data.state
            dependent.country = dependent_data.country
            dependent.postal_code = dependent_data.postal_code
            dependent.is_active = dependent_data.is_active
            dependent.updated_at = datetime.now(timezone.utc)
            
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

    @staticmethod
    async def partial_update_dependent(
        db: AsyncSession, 
        employee_id: int, 
        dependent_id: int, 
        dependent_data: EmployeeDependentRequest, 
        current_user: User
    ) -> Optional[EmployeeDependentResponse]:
        """Partially update a dependent for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get the specific dependent
        result = await db.execute(
            select(EmployeeDependent).where(
                and_(
                    EmployeeDependent.id == dependent_id,
                    EmployeeDependent.employee_id == employee_id
                )
            )
        )
        dependent = result.scalar_one_or_none()
        
        if not dependent:
            return None
        
        try:
            # Update only provided fields
            if dependent_data.name is not None:
                dependent.name = dependent_data.name
            if dependent_data.relationship_type is not None:
                dependent.relationship_type = dependent_data.relationship_type
            if dependent_data.date_of_birth is not None:
                dependent.date_of_birth = dependent_data.date_of_birth
            if dependent_data.gender is not None:
                dependent.gender = dependent_data.gender
            if dependent_data.nationality is not None:
                dependent.nationality = dependent_data.nationality
            if dependent_data.primary_address is not None:
                dependent.primary_address = dependent_data.primary_address
            if dependent_data.city is not None:
                dependent.city = dependent_data.city
            if dependent_data.state is not None:
                dependent.state = dependent_data.state
            if dependent_data.country is not None:
                dependent.country = dependent_data.country
            if dependent_data.postal_code is not None:
                dependent.postal_code = dependent_data.postal_code
            if dependent_data.is_active is not None:
                dependent.is_active = dependent_data.is_active
            
            dependent.updated_at = datetime.now(timezone.utc)
            
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

    @staticmethod
    async def delete_dependent(
        db: AsyncSession, 
        employee_id: int, 
        dependent_id: int, 
        current_user: User
    ) -> bool:
        """Delete a dependent for an employee."""
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        # Get the specific dependent
        result = await db.execute(
            select(EmployeeDependent).where(
                and_(
                    EmployeeDependent.id == dependent_id,
                    EmployeeDependent.employee_id == employee_id
                )
            )
        )
        dependent = result.scalar_one_or_none()
        
        if not dependent:
            return False
        
        try:
            await db.delete(dependent)
            await db.commit()
            return True
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
    ) -> EmployeeDocumentPublicResponse:
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
            # Validate required fields for document create
            required = ["document_type", "file_name", "file_path", "file_size", "mime_type"]
            missing = [f for f in required if getattr(document_data, f) is None or getattr(document_data, f) == ""]
            if missing:
                raise ValueError(f"Missing required document fields: {', '.join(missing)}")
            
            document = EmployeeDocument(
                employee_id=employee_id,
                document_type=document_data.document_type,
                file_name=document_data.file_name,
                file_path=document_data.file_path,
                file_size=document_data.file_size,
                mime_type=document_data.mime_type,
                uploaded_by_user_id=current_user.id,
                is_active=True if document_data.is_active is None else document_data.is_active
            )
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            # Create full response first, then convert to public response with masked data
            full_document = EmployeeDocumentResponse(
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
            return EmployeeDocumentPublicResponse.from_full_response(full_document)
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_documents(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeDocumentPublicResponse]:
        """
        Get all documents for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            current_user: Current authenticated user
            
        Returns:
            List of EmployeeDocumentResponse objects
        """
        # Verify employee belongs to current user and get documents
        result = await db.execute(
            select(EmployeeDocument)
            .join(Employee)
            .where(
                and_(
                    EmployeeDocument.employee_id == employee_id,
                    Employee.user_id == current_user.id
                )
            )
        )
        documents = result.scalars().all()
        
        # Convert to public responses with masked sensitive data
        document_responses = []
        for document in documents:
            full_document = EmployeeDocumentResponse(
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
            document_responses.append(EmployeeDocumentPublicResponse.from_full_response(full_document))
        
        return document_responses

    @staticmethod
    async def get_document(
        db: AsyncSession, 
        employee_id: int, 
        document_id: int,
        current_user: User
    ) -> Optional[EmployeeDocumentPublicResponse]:
        """
        Get a specific document for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            document_id: ID of the document
            current_user: Current authenticated user
            
        Returns:
            EmployeeDocumentResponse if found, None otherwise
        """
        # Verify employee belongs to current user and get specific document
        result = await db.execute(
            select(EmployeeDocument)
            .join(Employee)
            .where(
                and_(
                    EmployeeDocument.employee_id == employee_id,
                    EmployeeDocument.id == document_id,
                    Employee.user_id == current_user.id
                )
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return None
        
        # Create full response first, then convert to public response with masked data
        full_document = EmployeeDocumentResponse(
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
        return EmployeeDocumentPublicResponse.from_full_response(full_document)

    @staticmethod
    async def update_document(
        db: AsyncSession, 
        employee_id: int, 
        document_id: int,
        document_data: EmployeeDocumentRequest, 
        current_user: User
    ) -> EmployeeDocumentPublicResponse:
        """
        Update document information for an employee (full replacement).
        
        Args:
            db: Database session
            employee_id: ID of the employee
            document_id: ID of the document
            document_data: New document data
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeeDocumentResponse
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing document
            result = await db.execute(
                select(EmployeeDocument).where(
                    and_(
                        EmployeeDocument.employee_id == employee_id,
                        EmployeeDocument.id == document_id
                    )
                )
            )
            existing_document = result.scalar_one_or_none()
            
            if not existing_document:
                raise ValueError("Document not found for this employee")
            
            # Update existing record
            existing_document.document_type = document_data.document_type
            existing_document.file_name = document_data.file_name
            existing_document.file_path = document_data.file_path
            existing_document.file_size = document_data.file_size
            existing_document.mime_type = document_data.mime_type
            existing_document.is_active = document_data.is_active
            existing_document.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(existing_document)
            
            # Create full response first, then convert to public response with masked data
            full_document = EmployeeDocumentResponse(
                id=existing_document.id,
                employee_id=existing_document.employee_id,
                document_type=existing_document.document_type,
                file_name=existing_document.file_name,
                file_path=existing_document.file_path,
                file_size=existing_document.file_size,
                mime_type=existing_document.mime_type,
                upload_date=existing_document.upload_date,
                uploaded_by_user_id=existing_document.uploaded_by_user_id,
                is_active=existing_document.is_active,
                created_at=existing_document.created_at,
                updated_at=existing_document.updated_at
            )
            return EmployeeDocumentPublicResponse.from_full_response(full_document)
            
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def partial_update_document(
        db: AsyncSession, 
        employee_id: int, 
        document_id: int,
        document_data: EmployeeDocumentRequest, 
        current_user: User
    ) -> EmployeeDocumentPublicResponse:
        """
        Partially update document information for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            document_id: ID of the document
            document_data: Partial document data (only provided fields will be updated)
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeeDocumentResponse
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing document
            result = await db.execute(
                select(EmployeeDocument).where(
                    and_(
                        EmployeeDocument.employee_id == employee_id,
                        EmployeeDocument.id == document_id
                    )
                )
            )
            existing_document = result.scalar_one_or_none()
            
            if not existing_document:
                raise ValueError("Document not found for this employee")
            
            # Update only provided fields
            update_data = document_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(existing_document, field):
                    setattr(existing_document, field, value)
            
            existing_document.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(existing_document)
            
            # Create full response first, then convert to public response with masked data
            full_document = EmployeeDocumentResponse(
                id=existing_document.id,
                employee_id=existing_document.employee_id,
                document_type=existing_document.document_type,
                file_name=existing_document.file_name,
                file_path=existing_document.file_path,
                file_size=existing_document.file_size,
                mime_type=existing_document.mime_type,
                upload_date=existing_document.upload_date,
                uploaded_by_user_id=existing_document.uploaded_by_user_id,
                is_active=existing_document.is_active,
                created_at=existing_document.created_at,
                updated_at=existing_document.updated_at
            )
            return EmployeeDocumentPublicResponse.from_full_response(full_document)
            
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_document(
        db: AsyncSession, 
        employee_id: int, 
        document_id: int,
        current_user: User
    ) -> bool:
        """
        Delete a specific document for an employee.
        
        Args:
            db: Database session
            employee_id: ID of the employee
            document_id: ID of the document
            current_user: Current authenticated user
            
        Returns:
            True if deleted, False if not found
        """
        # Verify employee belongs to current user
        employee = await db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.user_id == current_user.id)
            )
        )
        if not employee.scalar_one_or_none():
            raise ValueError("Employee not found or access denied")
        
        try:
            # Get existing document
            result = await db.execute(
                select(EmployeeDocument).where(
                    and_(
                        EmployeeDocument.employee_id == employee_id,
                        EmployeeDocument.id == document_id
                    )
                )
            )
            existing_document = result.scalar_one_or_none()
            
            if not existing_document:
                return False
            
            # Delete the document record
            await db.delete(existing_document)
            await db.commit()
            
            return True
            
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
                # Validate required fields for bank info create
                required = ["bank_name", "account_number", "routing_number", "account_type", "account_holder_name", "account_holder_type"]
                missing = [f for f in required if getattr(employee_data.bank_info, f) is None or getattr(employee_data.bank_info, f) == ""]
                if missing:
                    raise ValueError(f"Missing required bank_info fields: {', '.join(missing)}")
                
                bank_info = EmployeeBankInfo(
                    employee_id=employee.id,
                    bank_name=employee_data.bank_info.bank_name,
                    account_number=employee_data.bank_info.account_number,
                    routing_number=employee_data.bank_info.routing_number,
                    account_type=employee_data.bank_info.account_type,
                    account_holder_name=employee_data.bank_info.account_holder_name,
                    account_holder_type=employee_data.bank_info.account_holder_type,
                    is_primary=True if employee_data.bank_info.is_primary is None else employee_data.bank_info.is_primary,
                    is_active=True if employee_data.bank_info.is_active is None else employee_data.bank_info.is_active
                )
                db.add(bank_info)
            
            # Create job timeline entries
            job_timeline = []
            for job_data in employee_data.job_timeline:
                # Tenant safety: ensure line_manager_id (if provided) belongs to current_user
                if job_data.line_manager_id is not None:
                    mgr = await db.execute(
                        select(Employee).where(
                            and_(Employee.id == job_data.line_manager_id, Employee.user_id == current_user.id)
                        )
                    )
                    if not mgr.scalar_one_or_none():
                        raise ValueError("line_manager_id not found or access denied")
                
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
            
            # Create contract timeline entries
            contract_timeline = []
            for contract_data in employee_data.contract_timeline:
                contract_entry = EmployeeContractTimeline(
                    employee_id=employee.id,
                    contract_number=contract_data.contract_number,
                    contract_name=contract_data.contract_name,
                    contract_type=contract_data.contract_type,
                    start_date=contract_data.start_date,
                    end_date=contract_data.end_date,
                    is_active=contract_data.is_active
                )
                db.add(contract_entry)
                contract_timeline.append(contract_entry)
            
            # Note: work_schedule is not part of EmployeeFullRequest schema
            # It will be empty in the response
            work_schedule = []
            
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
                # Validate required fields for document create
                required = ["document_type", "file_name", "file_path", "file_size", "mime_type"]
                missing = [f for f in required if getattr(doc_data, f) is None or getattr(doc_data, f) == ""]
                if missing:
                    raise ValueError(f"Missing required document fields: {', '.join(missing)}")
                
                document = EmployeeDocument(
                    employee_id=employee.id,
                    document_type=doc_data.document_type,
                    file_name=doc_data.file_name,
                    file_path=doc_data.file_path,
                    file_size=doc_data.file_size,
                    mime_type=doc_data.mime_type,
                    upload_date=datetime.now(timezone.utc),
                    uploaded_by_user_id=current_user.id,
                    is_active=True if doc_data.is_active is None else doc_data.is_active
                )
                db.add(document)
                documents.append(document)
            
            await db.commit()
            
            # Build response
            personal_details_response = None
            if personal_details:
                # Create full response first, then convert to public response with masked data
                full_personal_details = EmployeePersonalDetailsResponse(
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
                personal_details_response = EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)
            
            bank_info_response = None
            if bank_info:
                # Create full response first, then convert to public response with masked data
                full_bank_info = EmployeeBankInfoResponse(
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
                bank_info_response = EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)
            
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
            
           
            
            contract_timeline_response = [
                EmployeeContractTimelineResponse(
                    id=contract.id,
                    employee_id=contract.employee_id,
                    contract_number=contract.contract_number,
                    contract_name=contract.contract_name,
                    contract_type=contract.contract_type,
                    start_date=contract.start_date,
                    end_date=contract.end_date,
                    is_active=contract.is_active,
                    created_at=contract.created_at,
                    updated_at=contract.updated_at
                ) for contract in contract_timeline
            ]
            
            work_schedule_response = [
                EmployeeWorkScheduleResponse(
                    id=schedule.id,
                    employee_id=schedule.employee_id,
                    effective_from=schedule.effective_from,
                    effective_to=schedule.effective_to,
                    schedule_type=schedule.schedule_type,
                    standard_hours_per_day=schedule.standard_hours_per_day,
                    total_hours_per_week=schedule.total_hours_per_week,
                    monday_hours=schedule.monday_hours,
                    tuesday_hours=schedule.tuesday_hours,
                    wednesday_hours=schedule.wednesday_hours,
                    thursday_hours=schedule.thursday_hours,
                    friday_hours=schedule.friday_hours,
                    saturday_hours=schedule.saturday_hours,
                    sunday_hours=schedule.sunday_hours,
                    is_current=schedule.is_current,
                    created_at=schedule.created_at,
                    updated_at=schedule.updated_at
                ) for schedule in work_schedule
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
                EmployeeDocumentPublicResponse.from_full_response(
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
                    )
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
                contract_timeline=contract_timeline_response,
                work_schedule=work_schedule_response,
                payroll_records=[],  # Empty for new employees
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
            
            existing_contracts = await db.execute(
                select(EmployeeContractTimeline).where(EmployeeContractTimeline.employee_id == employee_id)
            )
            for record in existing_contracts.scalars():
                await db.delete(record)
            
            existing_schedules = await db.execute(
                select(EmployeeWorkSchedule).where(EmployeeWorkSchedule.employee_id == employee_id)
            )
            for record in existing_schedules.scalars():
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
                # Validate required fields for bank info create
                required = ["bank_name", "account_number", "routing_number", "account_type", "account_holder_name", "account_holder_type"]
                missing = [f for f in required if getattr(employee_data.bank_info, f) is None or getattr(employee_data.bank_info, f) == ""]
                if missing:
                    raise ValueError(f"Missing required bank_info fields: {', '.join(missing)}")
                
                bank_info = EmployeeBankInfo(
                    employee_id=employee.id,
                    bank_name=employee_data.bank_info.bank_name,
                    account_number=employee_data.bank_info.account_number,
                    routing_number=employee_data.bank_info.routing_number,
                    account_type=employee_data.bank_info.account_type,
                    account_holder_name=employee_data.bank_info.account_holder_name,
                    account_holder_type=employee_data.bank_info.account_holder_type,
                    is_primary=True if employee_data.bank_info.is_primary is None else employee_data.bank_info.is_primary,
                    is_active=True if employee_data.bank_info.is_active is None else employee_data.bank_info.is_active
                )
                db.add(bank_info)
            
            # Create job timeline entries
            job_timeline = []
            for job_data in employee_data.job_timeline:
                # Tenant safety: ensure line_manager_id (if provided) belongs to current_user
                if job_data.line_manager_id is not None:
                    mgr = await db.execute(
                        select(Employee).where(
                            and_(Employee.id == job_data.line_manager_id, Employee.user_id == current_user.id)
                        )
                    )
                    if not mgr.scalar_one_or_none():
                        raise ValueError("line_manager_id not found or access denied")
                
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
            
            # Create contract timeline entries
            contract_timeline = []
            for contract_data in employee_data.contract_timeline:
                contract_entry = EmployeeContractTimeline(
                    employee_id=employee.id,
                    contract_number=contract_data.contract_number,
                    contract_name=contract_data.contract_name,
                    contract_type=contract_data.contract_type,
                    start_date=contract_data.start_date,
                    end_date=contract_data.end_date,
                    is_active=contract_data.is_active
                )
                db.add(contract_entry)
                contract_timeline.append(contract_entry)
            
            # Note: work_schedule is not part of EmployeeFullRequest schema
            # It will be empty in the response
            work_schedule = []
            
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
                # Validate required fields for document create
                required = ["document_type", "file_name", "file_path", "file_size", "mime_type"]
                missing = [f for f in required if getattr(doc_data, f) is None or getattr(doc_data, f) == ""]
                if missing:
                    raise ValueError(f"Missing required document fields: {', '.join(missing)}")
                
                document = EmployeeDocument(
                    employee_id=employee.id,
                    document_type=doc_data.document_type,
                    file_name=doc_data.file_name,
                    file_path=doc_data.file_path,
                    file_size=doc_data.file_size,
                    mime_type=doc_data.mime_type,
                    upload_date=datetime.now(timezone.utc),
                    uploaded_by_user_id=current_user.id,
                    is_active=True if doc_data.is_active is None else doc_data.is_active
                )
                db.add(document)
                documents.append(document)
            
            await db.commit()
            
            # Build response using the created objects
            personal_details_response = None
            if personal_details:
                # Create full response first, then convert to public response with masked data
                full_personal_details = EmployeePersonalDetailsResponse(
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
                personal_details_response = EmployeePersonalDetailsPublicResponse.from_full_response(full_personal_details)
            
            bank_info_response = None
            if bank_info:
                # Create full response first, then convert to public response with masked data
                full_bank_info = EmployeeBankInfoResponse(
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
                bank_info_response = EmployeeBankInfoPublicResponse.from_full_response(full_bank_info)
            
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
            
           
            
            contract_timeline_response = [
                EmployeeContractTimelineResponse(
                    id=contract.id,
                    employee_id=contract.employee_id,
                    contract_number=contract.contract_number,
                    contract_name=contract.contract_name,
                    contract_type=contract.contract_type,
                    start_date=contract.start_date,
                    end_date=contract.end_date,
                    is_active=contract.is_active,
                    created_at=contract.created_at,
                    updated_at=contract.updated_at
                ) for contract in contract_timeline
            ]
            
            work_schedule_response = [
                EmployeeWorkScheduleResponse(
                    id=schedule.id,
                    employee_id=schedule.employee_id,
                    effective_from=schedule.effective_from,
                    effective_to=schedule.effective_to,
                    schedule_type=schedule.schedule_type,
                    standard_hours_per_day=schedule.standard_hours_per_day,
                    total_hours_per_week=schedule.total_hours_per_week,
                    monday_hours=schedule.monday_hours,
                    tuesday_hours=schedule.tuesday_hours,
                    wednesday_hours=schedule.wednesday_hours,
                    thursday_hours=schedule.thursday_hours,
                    friday_hours=schedule.friday_hours,
                    saturday_hours=schedule.saturday_hours,
                    sunday_hours=schedule.sunday_hours,
                    is_current=schedule.is_current,
                    created_at=schedule.created_at,
                    updated_at=schedule.updated_at
                ) for schedule in work_schedule
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
                EmployeeDocumentPublicResponse.from_full_response(
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
                    )
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
                contract_timeline=contract_timeline_response,
                work_schedule=work_schedule_response,
                payroll_records=[],  # Empty for new employees
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

    @staticmethod
    async def update_employee(
        db: AsyncSession, 
        employee_id: int, 
        employee_data: EmployeeRequest, 
        current_user: User
    ) -> Optional[EmployeeResponse]:
        """Update an employee's basic information."""
        try:
            # First, get the employee to ensure it exists and belongs to the user
            result = await db.execute(
                select(Employee)
                .where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            
            if not employee:
                return None
            
            # Update the employee fields
            employee.first_name = employee_data.first_name
            employee.last_name = employee_data.last_name
            employee.email = employee_data.email
            employee.phone = employee_data.phone
            employee.join_date = employee_data.join_date
            employee.employment_status = employee_data.employment_status or "ACTIVE"
            employee.updated_at = datetime.now(timezone.utc)
            
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
                raise ValueError("Employee update failed")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def partial_update_employee(
        db: AsyncSession, 
        employee_id: int, 
        employee_data: EmployeePartialUpdateRequest, 
        current_user: User
    ) -> EmployeeResponse:
        """
        Partially update basic employee information.
        
        This method updates only the provided fields in the employee data,
        preserving all existing related data and only updating the basic
        employee fields that are provided.
        
        Args:
            db: Database session
            employee_id: ID of the employee to update
            employee_data: Partial employee data (only provided fields will be updated)
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeeResponse with job timeline data
            
        Raises:
            ValueError: If employee not found or access denied
        """
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Update only provided fields using model_dump(exclude_unset=True)
            update_data = employee_data.model_dump(exclude_unset=True)
            
            # Validate and update each provided field
            for field, value in update_data.items():
                if hasattr(employee, field):
                    # Apply field-specific validation if needed
                    if field == 'email':
                        # Check for email uniqueness
                        existing_email = await db.execute(
                            select(Employee).where(
                                and_(
                                    Employee.email == value,
                                    Employee.id != employee_id,
                                    Employee.user_id == current_user.id
                                )
                            )
                        )
                        if existing_email.scalar_one_or_none():
                            raise ValueError(f"Email '{value}' is already in use by another employee")
                    
                    setattr(employee, field, value)
            
            # Update timestamp
            employee.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(employee)
            
            # Get current job timeline for response
            current_job = None
            line_manager_name = None
            
            job_result = await db.execute(
                select(EmployeeJobTimeline)
                .options(selectinload(EmployeeJobTimeline.employee))
                .where(EmployeeJobTimeline.employee_id == employee_id)
            )
            job_timeline = job_result.scalars().all()
            
            if job_timeline:
                current_job = next((job for job in job_timeline if job.is_current), None)
                
                # If no current job found, get the most recent one
                if not current_job and job_timeline:
                    current_job = max(job_timeline, key=lambda x: x.effective_date)
                
                # Get line manager name if line_manager_id exists
                if current_job and current_job.line_manager_id:
                    manager_result = await db.execute(
                        select(Employee).where(
                            and_(
                                Employee.id == current_job.line_manager_id,
                                Employee.user_id == current_user.id
                            )
                        )
                    )
                    manager = manager_result.scalar_one_or_none()
                    if manager:
                        line_manager_name = f"{manager.first_name} {manager.last_name}"
            
            return EmployeeResponse(
                id=employee.id,
                user_id=employee.user_id,
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                phone=employee.phone,
                join_date=employee.join_date,
                created_at=employee.created_at,
                updated_at=employee.updated_at,
                job_title=current_job.job_title if current_job else None,
                department=current_job.department if current_job else None,
                office=current_job.office if current_job else None,
                line_manager_id=current_job.line_manager_id if current_job else None,
                line_manager_name=line_manager_name,
                employment_status=employee.employment_status or "ACTIVE"  # Use actual status or default
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== CONTRACT TIMELINE CRUD ====================
    
    @staticmethod
    async def create_contract_timeline(
        db: AsyncSession, 
        employee_id: int, 
        contract_data: EmployeeContractTimelineRequest, 
        current_user: User
    ) -> EmployeeContractTimelineResponse:
        """Create a new contract timeline entry for an employee."""
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create contract timeline entry
            contract_timeline = EmployeeContractTimeline(
                employee_id=employee_id,
                contract_number=contract_data.contract_number,
                contract_name=contract_data.contract_name,
                contract_type=contract_data.contract_type,
                start_date=contract_data.start_date,
                end_date=contract_data.end_date,
                is_active=contract_data.is_active
            )
            
            db.add(contract_timeline)
            await db.commit()
            await db.refresh(contract_timeline)
            
            return EmployeeContractTimelineResponse(
                id=contract_timeline.id,
                employee_id=contract_timeline.employee_id,
                contract_number=contract_timeline.contract_number,
                contract_name=contract_timeline.contract_name,
                contract_type=contract_timeline.contract_type,
                start_date=contract_timeline.start_date,
                end_date=contract_timeline.end_date,
                is_active=contract_timeline.is_active,
                created_at=contract_timeline.created_at,
                updated_at=contract_timeline.updated_at
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except IntegrityError as e:
            await db.rollback()
            if "contract_number" in str(e):
                raise ValueError(f"Contract number '{contract_data.contract_number}' already exists")
            raise e
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_contract_timeline(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeContractTimelineResponse]:
        """Get all contract timeline entries for an employee."""
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get contract timeline entries
            result = await db.execute(
                select(EmployeeContractTimeline)
                .where(EmployeeContractTimeline.employee_id == employee_id)
                .order_by(EmployeeContractTimeline.start_date.desc())
            )
            contract_timelines = result.scalars().all()
            
            return [
                EmployeeContractTimelineResponse(
                    id=ct.id,
                    employee_id=ct.employee_id,
                    contract_number=ct.contract_number,
                    contract_name=ct.contract_name,
                    contract_type=ct.contract_type,
                    start_date=ct.start_date,
                    end_date=ct.end_date,
                    is_active=ct.is_active,
                    created_at=ct.created_at,
                    updated_at=ct.updated_at
                )
                for ct in contract_timelines
            ]
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            raise e

    @staticmethod
    async def update_contract_timeline(
        db: AsyncSession, 
        contract_id: int, 
        contract_data: EmployeeContractTimelineRequest, 
        current_user: User
    ) -> EmployeeContractTimelineResponse:
        """Update a contract timeline entry."""
        try:
            # Get contract timeline with employee verification
            result = await db.execute(
                select(EmployeeContractTimeline)
                .join(Employee)
                .where(
                    and_(
                        EmployeeContractTimeline.id == contract_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            contract_timeline = result.scalar_one_or_none()
            if not contract_timeline:
                raise ValueError("Contract timeline not found or access denied")
            
            # Update fields
            contract_timeline.contract_number = contract_data.contract_number
            contract_timeline.contract_name = contract_data.contract_name
            contract_timeline.contract_type = contract_data.contract_type
            contract_timeline.start_date = contract_data.start_date
            contract_timeline.end_date = contract_data.end_date
            contract_timeline.is_active = contract_data.is_active
            contract_timeline.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(contract_timeline)
            
            return EmployeeContractTimelineResponse(
                id=contract_timeline.id,
                employee_id=contract_timeline.employee_id,
                contract_number=contract_timeline.contract_number,
                contract_name=contract_timeline.contract_name,
                contract_type=contract_timeline.contract_type,
                start_date=contract_timeline.start_date,
                end_date=contract_timeline.end_date,
                is_active=contract_timeline.is_active,
                created_at=contract_timeline.created_at,
                updated_at=contract_timeline.updated_at
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except IntegrityError as e:
            await db.rollback()
            if "contract_number" in str(e):
                raise ValueError(f"Contract number '{contract_data.contract_number}' already exists")
            raise e
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_contract_timeline(
        db: AsyncSession, 
        contract_id: int, 
        current_user: User
    ) -> None:
        """Delete a contract timeline entry."""
        try:
            # Get contract timeline with employee verification
            result = await db.execute(
                select(EmployeeContractTimeline)
                .join(Employee)
                .where(
                    and_(
                        EmployeeContractTimeline.id == contract_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            contract_timeline = result.scalar_one_or_none()
            if not contract_timeline:
                raise ValueError("Contract timeline not found or access denied")
            
            await db.delete(contract_timeline)
            await db.commit()
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # Work Schedule Methods
    @staticmethod
    async def create_work_schedule(
        db: AsyncSession, 
        employee_id: int, 
        work_schedule_data: EmployeeWorkScheduleRequest, 
        current_user: User
    ) -> EmployeeWorkScheduleResponse:
        """Create a work schedule entry for an employee."""
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create work schedule entry
            work_schedule = EmployeeWorkSchedule(
                employee_id=employee_id,
                effective_from=work_schedule_data.effective_from,
                effective_to=work_schedule_data.effective_to,
                schedule_type=work_schedule_data.schedule_type,
                standard_hours_per_day=work_schedule_data.standard_hours_per_day,
                total_hours_per_week=work_schedule_data.total_hours_per_week,
                monday_hours=work_schedule_data.monday_hours,
                tuesday_hours=work_schedule_data.tuesday_hours,
                wednesday_hours=work_schedule_data.wednesday_hours,
                thursday_hours=work_schedule_data.thursday_hours,
                friday_hours=work_schedule_data.friday_hours,
                saturday_hours=work_schedule_data.saturday_hours,
                sunday_hours=work_schedule_data.sunday_hours,
                is_current=work_schedule_data.is_current
            )
            
            db.add(work_schedule)
            await db.commit()
            await db.refresh(work_schedule)
            
            return EmployeeWorkScheduleResponse(
                id=work_schedule.id,
                employee_id=work_schedule.employee_id,
                effective_from=work_schedule.effective_from,
                effective_to=work_schedule.effective_to,
                schedule_type=work_schedule.schedule_type,
                standard_hours_per_day=work_schedule.standard_hours_per_day,
                total_hours_per_week=work_schedule.total_hours_per_week,
                monday_hours=work_schedule.monday_hours,
                tuesday_hours=work_schedule.tuesday_hours,
                wednesday_hours=work_schedule.wednesday_hours,
                thursday_hours=work_schedule.thursday_hours,
                friday_hours=work_schedule.friday_hours,
                saturday_hours=work_schedule.saturday_hours,
                sunday_hours=work_schedule.sunday_hours,
                is_current=work_schedule.is_current,
                created_at=work_schedule.created_at,
                updated_at=work_schedule.updated_at
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_work_schedule(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeWorkScheduleResponse]:
        """Get all work schedule entries for an employee."""
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get work schedule entries
            result = await db.execute(
                select(EmployeeWorkSchedule)
                .where(EmployeeWorkSchedule.employee_id == employee_id)
                .order_by(EmployeeWorkSchedule.effective_from.desc())
            )
            work_schedules = result.scalars().all()
            
            return [
                EmployeeWorkScheduleResponse(
                    id=schedule.id,
                    employee_id=schedule.employee_id,
                    effective_from=schedule.effective_from,
                    effective_to=schedule.effective_to,
                    schedule_type=schedule.schedule_type,
                    standard_hours_per_day=schedule.standard_hours_per_day,
                    total_hours_per_week=schedule.total_hours_per_week,
                    monday_hours=schedule.monday_hours,
                    tuesday_hours=schedule.tuesday_hours,
                    wednesday_hours=schedule.wednesday_hours,
                    thursday_hours=schedule.thursday_hours,
                    friday_hours=schedule.friday_hours,
                    saturday_hours=schedule.saturday_hours,
                    sunday_hours=schedule.sunday_hours,
                    is_current=schedule.is_current,
                    created_at=schedule.created_at,
                    updated_at=schedule.updated_at
                ) for schedule in work_schedules
            ]
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_work_schedule(
        db: AsyncSession, 
        schedule_id: int, 
        work_schedule_data: EmployeeWorkScheduleRequest, 
        current_user: User
    ) -> EmployeeWorkScheduleResponse:
        """Update a work schedule entry."""
        try:
            # Get work schedule with employee verification
            result = await db.execute(
                select(EmployeeWorkSchedule)
                .join(Employee)
                .where(
                    and_(
                        EmployeeWorkSchedule.id == schedule_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            work_schedule = result.scalar_one_or_none()
            if not work_schedule:
                raise ValueError("Work schedule not found or access denied")
            
            # Update work schedule
            work_schedule.effective_from = work_schedule_data.effective_from
            work_schedule.effective_to = work_schedule_data.effective_to
            work_schedule.schedule_type = work_schedule_data.schedule_type
            work_schedule.standard_hours_per_day = work_schedule_data.standard_hours_per_day
            work_schedule.total_hours_per_week = work_schedule_data.total_hours_per_week
            work_schedule.monday_hours = work_schedule_data.monday_hours
            work_schedule.tuesday_hours = work_schedule_data.tuesday_hours
            work_schedule.wednesday_hours = work_schedule_data.wednesday_hours
            work_schedule.thursday_hours = work_schedule_data.thursday_hours
            work_schedule.friday_hours = work_schedule_data.friday_hours
            work_schedule.saturday_hours = work_schedule_data.saturday_hours
            work_schedule.sunday_hours = work_schedule_data.sunday_hours
            work_schedule.is_current = work_schedule_data.is_current
            work_schedule.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(work_schedule)
            
            return EmployeeWorkScheduleResponse(
                id=work_schedule.id,
                employee_id=work_schedule.employee_id,
                effective_from=work_schedule.effective_from,
                effective_to=work_schedule.effective_to,
                schedule_type=work_schedule.schedule_type,
                standard_hours_per_day=work_schedule.standard_hours_per_day,
                total_hours_per_week=work_schedule.total_hours_per_week,
                monday_hours=work_schedule.monday_hours,
                tuesday_hours=work_schedule.tuesday_hours,
                wednesday_hours=work_schedule.wednesday_hours,
                thursday_hours=work_schedule.thursday_hours,
                friday_hours=work_schedule.friday_hours,
                saturday_hours=work_schedule.saturday_hours,
                sunday_hours=work_schedule.sunday_hours,
                is_current=work_schedule.is_current,
                created_at=work_schedule.created_at,
                updated_at=work_schedule.updated_at
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_work_schedule(
        db: AsyncSession, 
        schedule_id: int, 
        current_user: User
    ) -> None:
        """Delete a work schedule entry."""
        try:
            # Get work schedule with employee verification
            result = await db.execute(
                select(EmployeeWorkSchedule)
                .join(Employee)
                .where(
                    and_(
                        EmployeeWorkSchedule.id == schedule_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            work_schedule = result.scalar_one_or_none()
            if not work_schedule:
                raise ValueError("Work schedule not found or access denied")
            
            await db.delete(work_schedule)
            await db.commit()
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def partial_update_employee_full(
        db: AsyncSession, 
        employee_id: int, 
        employee_data: EmployeePartialFullUpdateRequest, 
        current_user: User
    ) -> EmployeeFullResponse:
        """
        Partially update employee information with all related data.
        
        This method updates only the provided fields in the employee data
        and related data while preserving all existing data. Only provided 
        fields will be updated.
        
        Args:
            db: Database session
            employee_id: ID of the employee to update
            employee_data: Partial employee data with related data (only provided fields will be updated)
            current_user: Current authenticated user
            
        Returns:
            Updated EmployeeFullResponse with all related data
            
        Raises:
            ValueError: If employee not found or access denied
        """
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Update basic employee fields if provided
            if employee_data.first_name is not None:
                employee.first_name = employee_data.first_name
            if employee_data.last_name is not None:
                employee.last_name = employee_data.last_name
            if employee_data.email is not None:
                # Check for email uniqueness
                existing_email = await db.execute(
                    select(Employee).where(
                        and_(
                            Employee.email == employee_data.email,
                            Employee.id != employee_id,
                            Employee.user_id == current_user.id
                        )
                    )
                )
                if existing_email.scalar_one_or_none():
                    raise ValueError(f"Email '{employee_data.email}' is already in use by another employee")
                employee.email = employee_data.email
            if employee_data.phone is not None:
                employee.phone = employee_data.phone
            if employee_data.join_date is not None:
                employee.join_date = employee_data.join_date
            
            employee.updated_at = datetime.now(timezone.utc)
            
            # Update personal details if provided
            if employee_data.personal_details is not None:
                await EmployeeService.update_personal_details(db, employee_id, employee_data.personal_details, current_user)
            
            # Update bank info if provided
            if employee_data.bank_info is not None:
                await EmployeeService.update_bank_info(db, employee_id, employee_data.bank_info, current_user)
            
            # Update job timeline if provided
            if employee_data.job_timeline is not None:
                # Smart PATCH: Handle entries with and without IDs
                # Get existing job timeline entries
                existing_jobs = await db.execute(
                    select(EmployeeJobTimeline).where(EmployeeJobTimeline.employee_id == employee_id)
                )
                existing_jobs_list = existing_jobs.scalars().all()
                existing_jobs_by_id = {job.id: job for job in existing_jobs_list}
                
                # Process each job timeline entry
                for job_data in employee_data.job_timeline:
                    if job_data.id is not None and job_data.id in existing_jobs_by_id:
                        # Update existing entry
                        existing_job = existing_jobs_by_id[job_data.id]
                        existing_job.effective_date = job_data.effective_date
                        existing_job.end_date = job_data.end_date
                        existing_job.job_title = job_data.job_title
                        existing_job.position_type = job_data.position_type
                        existing_job.employment_type = job_data.employment_type
                        existing_job.line_manager_id = job_data.line_manager_id
                        existing_job.department = job_data.department
                        existing_job.office = job_data.office
                        existing_job.is_current = job_data.is_current
                        existing_job.updated_at = datetime.now(timezone.utc)
                    else:
                        # Create new entry (no ID or ID not found)
                        await EmployeeService.create_job_timeline(db, employee_id, job_data, current_user)
                
                # Delete existing entries that are not in the request
                requested_ids = {job_data.id for job_data in employee_data.job_timeline if job_data.id is not None}
                for existing_id, existing_job in existing_jobs_by_id.items():
                    if existing_id not in requested_ids:
                        await db.delete(existing_job)
            
            # Update contract timeline if provided
            if employee_data.contract_timeline is not None:
                # Smart PATCH: Handle entries with and without IDs
                # Get existing contract timeline entries
                existing_contracts = await db.execute(
                    select(EmployeeContractTimeline).where(EmployeeContractTimeline.employee_id == employee_id)
                )
                existing_contracts_list = existing_contracts.scalars().all()
                existing_contracts_by_id = {contract.id: contract for contract in existing_contracts_list}
                
                # Process each contract timeline entry
                for contract_data in employee_data.contract_timeline:
                    if contract_data.id is not None and contract_data.id in existing_contracts_by_id:
                        # Update existing entry
                        existing_contract = existing_contracts_by_id[contract_data.id]
                        existing_contract.contract_number = contract_data.contract_number
                        existing_contract.contract_name = contract_data.contract_name
                        existing_contract.contract_type = contract_data.contract_type
                        existing_contract.start_date = contract_data.start_date
                        existing_contract.end_date = contract_data.end_date
                        existing_contract.is_active = contract_data.is_active
                        existing_contract.updated_at = datetime.now(timezone.utc)
                    else:
                        # Create new entry (no ID or ID not found)
                        await EmployeeService.create_contract_timeline(db, employee_id, contract_data, current_user)
                
                # Delete existing entries that are not in the request
                requested_ids = {contract_data.id for contract_data in employee_data.contract_timeline if contract_data.id is not None}
                for existing_id, existing_contract in existing_contracts_by_id.items():
                    if existing_id not in requested_ids:
                        await db.delete(existing_contract)
            
            # Update work schedule if provided
            if employee_data.work_schedule is not None:
                # Smart PATCH: Handle entries with and without IDs
                # Get existing work schedule entries
                existing_schedules = await db.execute(
                    select(EmployeeWorkSchedule).where(EmployeeWorkSchedule.employee_id == employee_id)
                )
                existing_schedules_list = existing_schedules.scalars().all()
                existing_schedules_by_id = {schedule.id: schedule for schedule in existing_schedules_list}
                
                # Process each work schedule entry
                for schedule_data in employee_data.work_schedule:
                    if schedule_data.id is not None and schedule_data.id in existing_schedules_by_id:
                        # Update existing entry
                        existing_schedule = existing_schedules_by_id[schedule_data.id]
                        existing_schedule.effective_from = schedule_data.effective_from
                        existing_schedule.effective_to = schedule_data.effective_to
                        existing_schedule.schedule_type = schedule_data.schedule_type
                        existing_schedule.standard_hours_per_day = schedule_data.standard_hours_per_day
                        existing_schedule.total_hours_per_week = schedule_data.total_hours_per_week
                        existing_schedule.monday_hours = schedule_data.monday_hours
                        existing_schedule.tuesday_hours = schedule_data.tuesday_hours
                        existing_schedule.wednesday_hours = schedule_data.wednesday_hours
                        existing_schedule.thursday_hours = schedule_data.thursday_hours
                        existing_schedule.friday_hours = schedule_data.friday_hours
                        existing_schedule.saturday_hours = schedule_data.saturday_hours
                        existing_schedule.sunday_hours = schedule_data.sunday_hours
                        existing_schedule.is_current = schedule_data.is_current
                        existing_schedule.updated_at = datetime.now(timezone.utc)
                    else:
                        # Create new entry (no ID or ID not found)
                        await EmployeeService.create_work_schedule(db, employee_id, schedule_data, current_user)
                
                # Delete existing entries that are not in the request
                requested_ids = {schedule_data.id for schedule_data in employee_data.work_schedule if schedule_data.id is not None}
                for existing_id, existing_schedule in existing_schedules_by_id.items():
                    if existing_id not in requested_ids:
                        await db.delete(existing_schedule)
            
            # Update payroll records if provided
            if employee_data.payroll_records is not None:
                # Delete existing payroll items first (due to foreign key constraint)
                await db.execute(
                    delete(EmployeePayrollItem).where(
                        EmployeePayrollItem.payroll_record_id.in_(
                            select(EmployeePayrollRecord.id).where(EmployeePayrollRecord.employee_id == employee_id)
                        )
                    )
                )
                # Then delete existing payroll records
                await db.execute(
                    delete(EmployeePayrollRecord).where(EmployeePayrollRecord.employee_id == employee_id)
                )
                # Create new payroll records
                for payroll_data in employee_data.payroll_records:
                    await EmployeeService.create_payroll_record(db, employee_id, payroll_data, current_user)
            
            # Update dependents if provided
            if employee_data.dependents is not None:
                # Delete existing dependents
                await db.execute(
                    delete(EmployeeDependent).where(EmployeeDependent.employee_id == employee_id)
                )
                # Create new dependents
                for dependent_data in employee_data.dependents:
                    await EmployeeService.create_dependent(db, employee_id, dependent_data, current_user)
            
            # Update documents if provided
            if employee_data.documents is not None:
                # Delete existing documents
                await db.execute(
                    delete(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)
                )
                # Create new documents
                for document_data in employee_data.documents:
                    await EmployeeService.create_document(db, employee_id, document_data, current_user)
            
            await db.commit()
            await db.refresh(employee)
            
            # Return full employee data
            return await EmployeeService.get_employee_full(db, employee_id, current_user)
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== PAYROLL METHODS ====================
    
    @staticmethod
    async def create_payroll_record(
        db: AsyncSession, 
        employee_id: int, 
        payroll_data: EmployeePayrollRecordRequest, 
        current_user: User
    ) -> EmployeePayrollRecordResponse:
        """Create a payroll record for an employee."""
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create payroll record
            payroll_record = EmployeePayrollRecord(
                employee_id=employee_id,
                period_start=payroll_data.period_start,
                period_end=payroll_data.period_end,
                base_salary=payroll_data.base_salary,
                total_compensation=payroll_data.total_compensation,
                status=payroll_data.status,
                payment_date=payroll_data.payment_date
            )
            
            db.add(payroll_record)
            await db.commit()
            await db.refresh(payroll_record)
            
            # Create payroll items if provided
            payroll_items = []
            if payroll_data.payroll_items:
                for item_data in payroll_data.payroll_items:
                    payroll_item = EmployeePayrollItem(
                        payroll_record_id=payroll_record.id,
                        category=item_data.category,
                        item_type=item_data.item_type,
                        description=item_data.description,
                        amount=item_data.amount,
                        currency=item_data.currency,
                        quantity=item_data.quantity,
                        rate=item_data.rate,
                        meta_data=item_data.meta_data
                    )
                    db.add(payroll_item)
                    payroll_items.append(payroll_item)
                
                await db.commit()
                for item in payroll_items:
                    await db.refresh(item)
            
            # Build response
            payroll_items_response = [
                EmployeePayrollItemResponse(
                    id=item.id,
                    payroll_record_id=item.payroll_record_id,
                    category=item.category,
                    item_type=item.item_type,
                    description=item.description,
                    amount=item.amount,
                    currency=item.currency,
                    quantity=item.quantity,
                    rate=item.rate,
                    meta_data=item.meta_data,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                ) for item in payroll_items
            ]
            
            return EmployeePayrollRecordResponse(
                id=payroll_record.id,
                employee_id=payroll_record.employee_id,
                period_start=payroll_record.period_start,
                period_end=payroll_record.period_end,
                base_salary=payroll_record.base_salary,
                total_compensation=payroll_record.total_compensation,
                status=payroll_record.status,
                payment_date=payroll_record.payment_date,
                payroll_items=payroll_items_response,
                created_at=payroll_record.created_at,
                updated_at=payroll_record.updated_at
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def get_payroll_records(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeePayrollRecordResponse]:
        """Get all payroll records for an employee."""
        try:
            # Verify employee belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(Employee.id == employee_id, Employee.user_id == current_user.id)
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get payroll records with items
            result = await db.execute(
                select(EmployeePayrollRecord)
                .options(selectinload(EmployeePayrollRecord.payroll_items))
                .where(EmployeePayrollRecord.employee_id == employee_id)
                .order_by(EmployeePayrollRecord.period_start.desc())
            )
            payroll_records = result.scalars().all()
            
            return [
                EmployeePayrollRecordResponse(
                    id=record.id,
                    employee_id=record.employee_id,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    base_salary=record.base_salary,
                    total_compensation=record.total_compensation,
                    status=record.status,
                    payment_date=record.payment_date,
                    payroll_items=[
                        EmployeePayrollItemResponse(
                            id=item.id,
                            payroll_record_id=item.payroll_record_id,
                            category=item.category,
                            item_type=item.item_type,
                            description=item.description,
                            amount=item.amount,
                            currency=item.currency,
                            quantity=item.quantity,
                            rate=item.rate,
                            meta_data=item.meta_data,
                            created_at=item.created_at,
                            updated_at=item.updated_at
                        ) for item in record.payroll_items
                    ],
                    created_at=record.created_at,
                    updated_at=record.updated_at
                ) for record in payroll_records
            ]
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def update_payroll_record(
        db: AsyncSession, 
        payroll_id: int, 
        payroll_data: EmployeePayrollRecordRequest, 
        current_user: User
    ) -> EmployeePayrollRecordResponse:
        """Update a payroll record."""
        try:
            # Get payroll record with employee verification
            result = await db.execute(
                select(EmployeePayrollRecord)
                .join(Employee)
                .where(
                    and_(
                        EmployeePayrollRecord.id == payroll_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            payroll_record = result.scalar_one_or_none()
            if not payroll_record:
                raise ValueError("Payroll record not found or access denied")
            
            # Update payroll record
            payroll_record.period_start = payroll_data.period_start
            payroll_record.period_end = payroll_data.period_end
            payroll_record.base_salary = payroll_data.base_salary
            payroll_record.total_compensation = payroll_data.total_compensation
            payroll_record.status = payroll_data.status
            payroll_record.payment_date = payroll_data.payment_date
            payroll_record.updated_at = datetime.now(timezone.utc)
            
            # Update payroll items if provided
            if payroll_data.payroll_items is not None:
                # Delete existing items
                await db.execute(
                    delete(EmployeePayrollItem).where(EmployeePayrollItem.payroll_record_id == payroll_id)
                )
                # Create new items
                for item_data in payroll_data.payroll_items:
                    payroll_item = EmployeePayrollItem(
                        payroll_record_id=payroll_id,
                        category=item_data.category,
                        item_type=item_data.item_type,
                        description=item_data.description,
                        amount=item_data.amount,
                        currency=item_data.currency,
                        quantity=item_data.quantity,
                        rate=item_data.rate,
                        meta_data=item_data.meta_data
                    )
                    db.add(payroll_item)
            
            await db.commit()
            await db.refresh(payroll_record)
            
            # Get updated payroll items
            result = await db.execute(
                select(EmployeePayrollItem).where(EmployeePayrollItem.payroll_record_id == payroll_id)
            )
            payroll_items = result.scalars().all()
            
            return EmployeePayrollRecordResponse(
                id=payroll_record.id,
                employee_id=payroll_record.employee_id,
                period_start=payroll_record.period_start,
                period_end=payroll_record.period_end,
                base_salary=payroll_record.base_salary,
                total_compensation=payroll_record.total_compensation,
                status=payroll_record.status,
                payment_date=payroll_record.payment_date,
                payroll_items=[
                    EmployeePayrollItemResponse(
                        id=item.id,
                        payroll_record_id=item.payroll_record_id,
                        category=item.category,
                        item_type=item.item_type,
                        description=item.description,
                        amount=item.amount,
                        currency=item.currency,
                        quantity=item.quantity,
                        rate=item.rate,
                        meta_data=item.meta_data,
                        created_at=item.created_at,
                        updated_at=item.updated_at
                    ) for item in payroll_items
                ],
                created_at=payroll_record.created_at,
                updated_at=payroll_record.updated_at
            )
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete_payroll_record(
        db: AsyncSession, 
        payroll_id: int, 
        current_user: User
    ) -> None:
        """Delete a payroll record."""
        try:
            # Get payroll record with employee verification
            result = await db.execute(
                select(EmployeePayrollRecord)
                .join(Employee)
                .where(
                    and_(
                        EmployeePayrollRecord.id == payroll_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            payroll_record = result.scalar_one_or_none()
            if not payroll_record:
                raise ValueError("Payroll record not found or access denied")
            
            # Delete payroll items first
            await db.execute(
                delete(EmployeePayrollItem).where(EmployeePayrollItem.payroll_record_id == payroll_id)
            )
            
            # Then delete the payroll record
            await db.delete(payroll_record)
            await db.commit()
            
        except ValueError:
            # Re-raise ValueError as-is (validation errors)
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== ONE-OFF PAYMENT METHODS ====================
    
    @staticmethod
    async def create_one_off_payment(
        db: AsyncSession, 
        employee_id: int, 
        payment_data: EmployeeOneOffPaymentRequest, 
        current_user: User
    ) -> EmployeeOneOffPaymentResponse:
        """Create a new one-off payment for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create one-off payment
            one_off_payment = EmployeeOneOffPayment(
                employee_id=employee_id,
                item_name=payment_data.item_name,
                item_type=payment_data.item_type,
                amount=payment_data.amount,
                currency=payment_data.currency,
                payment_date=payment_data.payment_date,
                description=payment_data.description,
                meta_data=payment_data.meta_data
            )
            db.add(one_off_payment)
            await db.commit()
            await db.refresh(one_off_payment)
            
            return EmployeeOneOffPaymentResponse(
                id=one_off_payment.id,
                employee_id=one_off_payment.employee_id,
                payroll_record_id=one_off_payment.payroll_record_id,
                item_name=one_off_payment.item_name,
                item_type=one_off_payment.item_type,
                amount=one_off_payment.amount,
                currency=one_off_payment.currency,
                payment_date=one_off_payment.payment_date,
                description=one_off_payment.description,
                meta_data=one_off_payment.meta_data,
                created_at=one_off_payment.created_at,
                updated_at=one_off_payment.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def list_one_off_payments(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeOneOffPaymentResponse]:
        """Get all one-off payments for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get one-off payments
            result = await db.execute(
                select(EmployeeOneOffPayment)
                .where(EmployeeOneOffPayment.employee_id == employee_id)
                .order_by(EmployeeOneOffPayment.created_at.desc())
            )
            payments = result.scalars().all()
            
            return [
                EmployeeOneOffPaymentResponse(
                    id=payment.id,
                    employee_id=payment.employee_id,
                    payroll_record_id=payment.payroll_record_id,
                    item_name=payment.item_name,
                    item_type=payment.item_type,
                    amount=payment.amount,
                    currency=payment.currency,
                    payment_date=payment.payment_date,
                    description=payment.description,
                    meta_data=payment.meta_data,
                    created_at=payment.created_at,
                    updated_at=payment.updated_at
                )
                for payment in payments
            ]
            
        except ValueError:
            raise
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_one_off_payment(
        db: AsyncSession, 
        payment_id: int, 
        payment_data: EmployeeOneOffPaymentRequest, 
        current_user: User
    ) -> EmployeeOneOffPaymentResponse:
        """Update a one-off payment."""
        try:
            # Get payment with employee verification
            result = await db.execute(
                select(EmployeeOneOffPayment)
                .join(Employee)
                .where(
                    and_(
                        EmployeeOneOffPayment.id == payment_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            payment = result.scalar_one_or_none()
            if not payment:
                raise ValueError("One-off payment not found or access denied")
            
            # Update payment
            payment.item_name = payment_data.item_name
            payment.item_type = payment_data.item_type
            payment.amount = payment_data.amount
            payment.currency = payment_data.currency
            payment.payment_date = payment_data.payment_date
            payment.description = payment_data.description
            payment.meta_data = payment_data.meta_data
            payment.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(payment)
            
            return EmployeeOneOffPaymentResponse(
                id=payment.id,
                employee_id=payment.employee_id,
                payroll_record_id=payment.payroll_record_id,
                item_name=payment.item_name,
                item_type=payment.item_type,
                amount=payment.amount,
                currency=payment.currency,
                payment_date=payment.payment_date,
                description=payment.description,
                meta_data=payment.meta_data,
                created_at=payment.created_at,
                updated_at=payment.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete_one_off_payment(
        db: AsyncSession, 
        payment_id: int, 
        current_user: User
    ) -> None:
        """Delete a one-off payment."""
        try:
            # Get payment with employee verification
            result = await db.execute(
                select(EmployeeOneOffPayment)
                .join(Employee)
                .where(
                    and_(
                        EmployeeOneOffPayment.id == payment_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            payment = result.scalar_one_or_none()
            if not payment:
                raise ValueError("One-off payment not found or access denied")
            
            await db.delete(payment)
            await db.commit()
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== TIME-OFF METHODS ====================
    
    @staticmethod
    async def create_time_off(
        db: AsyncSession, 
        employee_id: int, 
        time_off_data: EmployeeTimeOffRequest, 
        current_user: User
    ) -> EmployeeTimeOffResponse:
        """Create a new time-off record for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create time-off record
            time_off = EmployeeTimeOff(
                employee_id=employee_id,
                time_off_type=time_off_data.time_off_type,
                days_used=time_off_data.days_used,
                days_remaining=time_off_data.days_remaining,
                amount=time_off_data.amount,
                currency=time_off_data.currency,
                period_start=time_off_data.period_start,
                period_end=time_off_data.period_end,
                description=time_off_data.description,
                meta_data=time_off_data.meta_data
            )
            db.add(time_off)
            await db.commit()
            await db.refresh(time_off)
            
            return EmployeeTimeOffResponse(
                id=time_off.id,
                employee_id=time_off.employee_id,
                time_off_type=time_off.time_off_type,
                days_used=time_off.days_used,
                days_remaining=time_off.days_remaining,
                amount=time_off.amount,
                currency=time_off.currency,
                period_start=time_off.period_start,
                period_end=time_off.period_end,
                description=time_off.description,
                meta_data=time_off.meta_data,
                created_at=time_off.created_at,
                updated_at=time_off.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def list_time_off(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeTimeOffResponse]:
        """Get all time-off records for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get time-off records
            result = await db.execute(
                select(EmployeeTimeOff)
                .where(EmployeeTimeOff.employee_id == employee_id)
                .order_by(EmployeeTimeOff.created_at.desc())
            )
            time_off_records = result.scalars().all()
            
            return [
                EmployeeTimeOffResponse(
                    id=record.id,
                    employee_id=record.employee_id,
                    time_off_type=record.time_off_type,
                    days_used=record.days_used,
                    days_remaining=record.days_remaining,
                    amount=record.amount,
                    currency=record.currency,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    description=record.description,
                    meta_data=record.meta_data,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                for record in time_off_records
            ]
            
        except ValueError:
            raise
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_time_off(
        db: AsyncSession, 
        time_off_id: int, 
        time_off_data: EmployeeTimeOffRequest, 
        current_user: User
    ) -> EmployeeTimeOffResponse:
        """Update a time-off record."""
        try:
            # Get time-off record with employee verification
            result = await db.execute(
                select(EmployeeTimeOff)
                .join(Employee)
                .where(
                    and_(
                        EmployeeTimeOff.id == time_off_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            time_off = result.scalar_one_or_none()
            if not time_off:
                raise ValueError("Time-off record not found or access denied")
            
            # Update time-off record
            time_off.time_off_type = time_off_data.time_off_type
            time_off.days_used = time_off_data.days_used
            time_off.days_remaining = time_off_data.days_remaining
            time_off.amount = time_off_data.amount
            time_off.currency = time_off_data.currency
            time_off.period_start = time_off_data.period_start
            time_off.period_end = time_off_data.period_end
            time_off.description = time_off_data.description
            time_off.meta_data = time_off_data.meta_data
            time_off.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(time_off)
            
            return EmployeeTimeOffResponse(
                id=time_off.id,
                employee_id=time_off.employee_id,
                time_off_type=time_off.time_off_type,
                days_used=time_off.days_used,
                days_remaining=time_off.days_remaining,
                amount=time_off.amount,
                currency=time_off.currency,
                period_start=time_off.period_start,
                period_end=time_off.period_end,
                description=time_off.description,
                meta_data=time_off.meta_data,
                created_at=time_off.created_at,
                updated_at=time_off.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete_time_off(
        db: AsyncSession, 
        time_off_id: int, 
        current_user: User
    ) -> None:
        """Delete a time-off record."""
        try:
            # Get time-off record with employee verification
            result = await db.execute(
                select(EmployeeTimeOff)
                .join(Employee)
                .where(
                    and_(
                        EmployeeTimeOff.id == time_off_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            time_off = result.scalar_one_or_none()
            if not time_off:
                raise ValueError("Time-off record not found or access denied")
            
            await db.delete(time_off)
            await db.commit()
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== OVERTIME METHODS ====================
    
    @staticmethod
    async def create_overtime(
        db: AsyncSession, 
        employee_id: int, 
        overtime_data: EmployeeOvertimeRequest, 
        current_user: User
    ) -> EmployeeOvertimeResponse:
        """Create a new overtime record for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create overtime record
            overtime = EmployeeOvertime(
                employee_id=employee_id,
                overtime_date=overtime_data.overtime_date,
                hours=overtime_data.hours,
                rate=overtime_data.rate,
                amount=overtime_data.amount,
                currency=overtime_data.currency,
                overtime_type=overtime_data.overtime_type,
                description=overtime_data.description,
                meta_data=overtime_data.meta_data
            )
            db.add(overtime)
            await db.commit()
            await db.refresh(overtime)
            
            return EmployeeOvertimeResponse(
                id=overtime.id,
                employee_id=overtime.employee_id,
                payroll_record_id=overtime.payroll_record_id,
                overtime_date=overtime.overtime_date,
                hours=overtime.hours,
                rate=overtime.rate,
                amount=overtime.amount,
                currency=overtime.currency,
                overtime_type=overtime.overtime_type,
                description=overtime.description,
                meta_data=overtime.meta_data,
                created_at=overtime.created_at,
                updated_at=overtime.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def list_overtime(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeOvertimeResponse]:
        """Get all overtime records for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get overtime records
            result = await db.execute(
                select(EmployeeOvertime)
                .where(EmployeeOvertime.employee_id == employee_id)
                .order_by(EmployeeOvertime.created_at.desc())
            )
            overtime_records = result.scalars().all()
            
            return [
                EmployeeOvertimeResponse(
                    id=record.id,
                    employee_id=record.employee_id,
                    payroll_record_id=record.payroll_record_id,
                    overtime_date=record.overtime_date,
                    hours=record.hours,
                    rate=record.rate,
                    amount=record.amount,
                    currency=record.currency,
                    overtime_type=record.overtime_type,
                    description=record.description,
                    meta_data=record.meta_data,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                for record in overtime_records
            ]
            
        except ValueError:
            raise
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_overtime(
        db: AsyncSession, 
        overtime_id: int, 
        overtime_data: EmployeeOvertimeRequest, 
        current_user: User
    ) -> EmployeeOvertimeResponse:
        """Update an overtime record."""
        try:
            # Get overtime record with employee verification
            result = await db.execute(
                select(EmployeeOvertime)
                .join(Employee)
                .where(
                    and_(
                        EmployeeOvertime.id == overtime_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            overtime = result.scalar_one_or_none()
            if not overtime:
                raise ValueError("Overtime record not found or access denied")
            
            # Update overtime record
            overtime.overtime_date = overtime_data.overtime_date
            overtime.hours = overtime_data.hours
            overtime.rate = overtime_data.rate
            overtime.amount = overtime_data.amount
            overtime.currency = overtime_data.currency
            overtime.overtime_type = overtime_data.overtime_type
            overtime.description = overtime_data.description
            overtime.meta_data = overtime_data.meta_data
            overtime.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(overtime)
            
            return EmployeeOvertimeResponse(
                id=overtime.id,
                employee_id=overtime.employee_id,
                payroll_record_id=overtime.payroll_record_id,
                overtime_date=overtime.overtime_date,
                hours=overtime.hours,
                rate=overtime.rate,
                amount=overtime.amount,
                currency=overtime.currency,
                overtime_type=overtime.overtime_type,
                description=overtime.description,
                meta_data=overtime.meta_data,
                created_at=overtime.created_at,
                updated_at=overtime.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete_overtime(
        db: AsyncSession, 
        overtime_id: int, 
        current_user: User
    ) -> None:
        """Delete an overtime record."""
        try:
            # Get overtime record with employee verification
            result = await db.execute(
                select(EmployeeOvertime)
                .join(Employee)
                .where(
                    and_(
                        EmployeeOvertime.id == overtime_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            overtime = result.scalar_one_or_none()
            if not overtime:
                raise ValueError("Overtime record not found or access denied")
            
            await db.delete(overtime)
            await db.commit()
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== DEFICIT METHODS ====================
    
    @staticmethod
    async def create_deficit(
        db: AsyncSession, 
        employee_id: int, 
        deficit_data: EmployeeDeficitRequest, 
        current_user: User
    ) -> EmployeeDeficitResponse:
        """Create a new deficit record for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create deficit record
            deficit = EmployeeDeficit(
                employee_id=employee_id,
                deficit_type=deficit_data.deficit_type,
                deficit_hours=deficit_data.deficit_hours,
                deficit_amount=deficit_data.deficit_amount,
                currency=deficit_data.currency,
                period_start=deficit_data.period_start,
                period_end=deficit_data.period_end,
                description=deficit_data.description,
                meta_data=deficit_data.meta_data
            )
            db.add(deficit)
            await db.commit()
            await db.refresh(deficit)
            
            return EmployeeDeficitResponse(
                id=deficit.id,
                employee_id=deficit.employee_id,
                payroll_record_id=deficit.payroll_record_id,
                deficit_type=deficit.deficit_type,
                deficit_hours=deficit.deficit_hours,
                deficit_amount=deficit.deficit_amount,
                currency=deficit.currency,
                period_start=deficit.period_start,
                period_end=deficit.period_end,
                description=deficit.description,
                meta_data=deficit.meta_data,
                created_at=deficit.created_at,
                updated_at=deficit.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def list_deficits(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeDeficitResponse]:
        """Get all deficit records for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get deficit records
            result = await db.execute(
                select(EmployeeDeficit)
                .where(EmployeeDeficit.employee_id == employee_id)
                .order_by(EmployeeDeficit.created_at.desc())
            )
            deficit_records = result.scalars().all()
            
            return [
                EmployeeDeficitResponse(
                    id=record.id,
                    employee_id=record.employee_id,
                    payroll_record_id=record.payroll_record_id,
                    deficit_type=record.deficit_type,
                    deficit_hours=record.deficit_hours,
                    deficit_amount=record.deficit_amount,
                    currency=record.currency,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    description=record.description,
                    meta_data=record.meta_data,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                for record in deficit_records
            ]
            
        except ValueError:
            raise
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_deficit(
        db: AsyncSession, 
        deficit_id: int, 
        deficit_data: EmployeeDeficitRequest, 
        current_user: User
    ) -> EmployeeDeficitResponse:
        """Update a deficit record."""
        try:
            # Get deficit record with employee verification
            result = await db.execute(
                select(EmployeeDeficit)
                .join(Employee)
                .where(
                    and_(
                        EmployeeDeficit.id == deficit_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            deficit = result.scalar_one_or_none()
            if not deficit:
                raise ValueError("Deficit record not found or access denied")
            
            # Update deficit record
            deficit.deficit_type = deficit_data.deficit_type
            deficit.deficit_hours = deficit_data.deficit_hours
            deficit.deficit_amount = deficit_data.deficit_amount
            deficit.currency = deficit_data.currency
            deficit.period_start = deficit_data.period_start
            deficit.period_end = deficit_data.period_end
            deficit.description = deficit_data.description
            deficit.meta_data = deficit_data.meta_data
            deficit.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(deficit)
            
            return EmployeeDeficitResponse(
                id=deficit.id,
                employee_id=deficit.employee_id,
                payroll_record_id=deficit.payroll_record_id,
                deficit_type=deficit.deficit_type,
                deficit_hours=deficit.deficit_hours,
                deficit_amount=deficit.deficit_amount,
                currency=deficit.currency,
                period_start=deficit.period_start,
                period_end=deficit.period_end,
                description=deficit.description,
                meta_data=deficit.meta_data,
                created_at=deficit.created_at,
                updated_at=deficit.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete_deficit(
        db: AsyncSession, 
        deficit_id: int, 
        current_user: User
    ) -> None:
        """Delete a deficit record."""
        try:
            # Get deficit record with employee verification
            result = await db.execute(
                select(EmployeeDeficit)
                .join(Employee)
                .where(
                    and_(
                        EmployeeDeficit.id == deficit_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            deficit = result.scalar_one_or_none()
            if not deficit:
                raise ValueError("Deficit record not found or access denied")
            
            await db.delete(deficit)
            await db.commit()
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e

    # ==================== ATTENDANCE METHODS ====================
    
    @staticmethod
    async def create_attendance(
        db: AsyncSession, 
        employee_id: int, 
        attendance_data: EmployeeAttendanceRequest, 
        current_user: User
    ) -> EmployeeAttendanceResponse:
        """Create a new attendance record for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Create attendance record
            attendance = EmployeeAttendance(
                employee_id=employee_id,
                period=attendance_data.period,
                expected_hours=attendance_data.expected_hours,
                actual_work_hours=attendance_data.actual_work_hours,
                period_start=attendance_data.period_start,
                period_end=attendance_data.period_end,
                description=attendance_data.description,
                meta_data=attendance_data.meta_data
            )
            db.add(attendance)
            await db.commit()
            await db.refresh(attendance)
            
            return EmployeeAttendanceResponse(
                id=attendance.id,
                employee_id=attendance.employee_id,
                payroll_record_id=attendance.payroll_record_id,
                period=attendance.period,
                expected_hours=attendance.expected_hours,
                actual_work_hours=attendance.actual_work_hours,
                period_start=attendance.period_start,
                period_end=attendance.period_end,
                description=attendance.description,
                meta_data=attendance.meta_data,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def list_attendance(
        db: AsyncSession, 
        employee_id: int, 
        current_user: User
    ) -> List[EmployeeAttendanceResponse]:
        """Get all attendance records for an employee."""
        try:
            # Verify employee exists and belongs to current user
            result = await db.execute(
                select(Employee).where(
                    and_(
                        Employee.id == employee_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise ValueError("Employee not found or access denied")
            
            # Get attendance records
            result = await db.execute(
                select(EmployeeAttendance)
                .where(EmployeeAttendance.employee_id == employee_id)
                .order_by(EmployeeAttendance.created_at.desc())
            )
            attendance_records = result.scalars().all()
            
            return [
                EmployeeAttendanceResponse(
                    id=record.id,
                    employee_id=record.employee_id,
                    payroll_record_id=record.payroll_record_id,
                    period=record.period,
                    expected_hours=record.expected_hours,
                    actual_work_hours=record.actual_work_hours,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    description=record.description,
                    meta_data=record.meta_data,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                for record in attendance_records
            ]
            
        except ValueError:
            raise
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_attendance(
        db: AsyncSession, 
        attendance_id: int, 
        attendance_data: EmployeeAttendanceRequest, 
        current_user: User
    ) -> EmployeeAttendanceResponse:
        """Update an attendance record."""
        try:
            # Get attendance record with employee verification
            result = await db.execute(
                select(EmployeeAttendance)
                .join(Employee)
                .where(
                    and_(
                        EmployeeAttendance.id == attendance_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            attendance = result.scalar_one_or_none()
            if not attendance:
                raise ValueError("Attendance record not found or access denied")
            
            # Update attendance record
            attendance.period = attendance_data.period
            attendance.expected_hours = attendance_data.expected_hours
            attendance.actual_work_hours = attendance_data.actual_work_hours
            attendance.period_start = attendance_data.period_start
            attendance.period_end = attendance_data.period_end
            attendance.description = attendance_data.description
            attendance.meta_data = attendance_data.meta_data
            attendance.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(attendance)
            
            return EmployeeAttendanceResponse(
                id=attendance.id,
                employee_id=attendance.employee_id,
                payroll_record_id=attendance.payroll_record_id,
                period=attendance.period,
                expected_hours=attendance.expected_hours,
                actual_work_hours=attendance.actual_work_hours,
                period_start=attendance.period_start,
                period_end=attendance.period_end,
                description=attendance.description,
                meta_data=attendance.meta_data,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete_attendance(
        db: AsyncSession, 
        attendance_id: int, 
        current_user: User
    ) -> None:
        """Delete an attendance record."""
        try:
            # Get attendance record with employee verification
            result = await db.execute(
                select(EmployeeAttendance)
                .join(Employee)
                .where(
                    and_(
                        EmployeeAttendance.id == attendance_id,
                        Employee.user_id == current_user.id
                    )
                )
            )
            attendance = result.scalar_one_or_none()
            if not attendance:
                raise ValueError("Attendance record not found or access denied")
            
            await db.delete(attendance)
            await db.commit()
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            raise e

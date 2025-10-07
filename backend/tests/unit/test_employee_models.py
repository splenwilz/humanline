"""
Unit tests for Employee models.

Tests model behavior, properties, and relationships without database operations.
Focuses on model-specific logic and computed properties.
"""

import pytest
from datetime import datetime, date, timezone

from models.employee import (
    Employee, EmployeePersonalDetails, EmployeeJobTimeline,
    EmployeeContractTimeline, EmployeeWorkSchedule, EmployeePayrollRecord,
    EmployeePayrollItem, EmployeeBankInfo, EmployeeDependent, EmployeeDocument
)


class TestEmployeeModel:
    """Test Employee model behavior and properties."""
    
    def test_employee_creation(self):
        """Test creating employee instance with all fields."""
        now = datetime.now(timezone.utc)
        
        employee = Employee(
            id=1,
            user_id=123,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15),
            created_at=now,
            updated_at=now
        )
        
        # Verify all fields are set correctly
        assert employee.id == 1
        assert employee.user_id == 123
        assert employee.first_name == "John"
        assert employee.last_name == "Doe"
        assert employee.email == "john.doe@example.com"
        assert employee.phone == "(555) 123-4567"
        assert employee.join_date == date(2024, 1, 15)
        assert employee.created_at == now
        assert employee.updated_at == now
    
    def test_employee_repr(self):
        """Test string representation of employee."""
        employee = Employee(
            id=1,
            user_id=123,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15)
        )
        
        repr_str = repr(employee)
        
        assert "Employee" in repr_str
        assert "id=1" in repr_str
        assert "first_name=John" in repr_str
        assert "last_name=Doe" in repr_str
        assert "email=john.doe@example.com" in repr_str
    
    def test_employee_tablename(self):
        """Test that table name is set correctly."""
        assert Employee.__tablename__ == "employees"


class TestEmployeePersonalDetailsModel:
    """Test EmployeePersonalDetails model behavior."""
    
    def test_personal_details_creation(self):
        """Test creating personal details instance."""
        now = datetime.now(timezone.utc)
        
        personal_details = EmployeePersonalDetails(
            id=1,
            employee_id=123,
            gender="MALE",
            date_of_birth=date(1990, 1, 15),
            nationality="American",
            health_care_provider="Blue Cross",
            marital_status="SINGLE",
            personal_tax_id="123-45-6789",
            social_insurance_number="123456789",
            primary_address="123 Main St",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001",
            created_at=now,
            updated_at=now
        )
        
        assert personal_details.id == 1
        assert personal_details.employee_id == 123
        assert personal_details.gender == "MALE"
        assert personal_details.date_of_birth == date(1990, 1, 15)
        assert personal_details.nationality == "American"
        assert personal_details.marital_status == "SINGLE"
        assert personal_details.created_at == now
        assert personal_details.updated_at == now
    
    def test_personal_details_repr(self):
        """Test string representation of personal details."""
        personal_details = EmployeePersonalDetails(
            id=1,
            employee_id=123,
            gender="MALE",
            date_of_birth=date(1990, 1, 15),
            nationality="American",
            marital_status="SINGLE"
        )
        
        repr_str = repr(personal_details)
        
        assert "EmployeePersonalDetails" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "gender=MALE" in repr_str
    
    def test_personal_details_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeePersonalDetails.__tablename__ == "employee_personal_details"


class TestEmployeeJobTimelineModel:
    """Test EmployeeJobTimeline model behavior."""
    
    def test_job_timeline_creation(self):
        """Test creating job timeline instance."""
        now = datetime.now(timezone.utc)
        
        job_timeline = EmployeeJobTimeline(
            id=1,
            employee_id=123,
            effective_date=date(2024, 1, 15),
            end_date=date(2024, 12, 31),
            job_title="Software Engineer",
            position_type="Individual Contributor",
            employment_type="FULL_TIME",
            line_manager_id=456,
            department="Engineering",
            office="New York",
            is_current=True,
            created_at=now,
            updated_at=now
        )
        
        assert job_timeline.id == 1
        assert job_timeline.employee_id == 123
        assert job_timeline.effective_date == date(2024, 1, 15)
        assert job_timeline.end_date == date(2024, 12, 31)
        assert job_timeline.job_title == "Software Engineer"
        assert job_timeline.employment_type == "FULL_TIME"
        assert job_timeline.is_current is True
        assert job_timeline.created_at == now
        assert job_timeline.updated_at == now
    
    def test_job_timeline_repr(self):
        """Test string representation of job timeline."""
        job_timeline = EmployeeJobTimeline(
            id=1,
            employee_id=123,
            effective_date=date(2024, 1, 15),
            job_title="Software Engineer",
            employment_type="FULL_TIME",
            department="Engineering",
            office="New York",
            is_current=True
        )
        
        repr_str = repr(job_timeline)
        
        assert "EmployeeJobTimeline" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "job_title=Software Engineer" in repr_str
    
    def test_job_timeline_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeeJobTimeline.__tablename__ == "employee_job_timeline"


class TestEmployeeContractTimelineModel:
    """Test EmployeeContractTimeline model behavior."""
    
    def test_contract_timeline_creation(self):
        """Test creating contract timeline instance."""
        now = datetime.now(timezone.utc)
        
        contract_timeline = EmployeeContractTimeline(
            id=1,
            employee_id=123,
            contract_number="CONTRACT-2024-001",
            contract_name="Employment Contract 2024",
            contract_type="FULL_TIME",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 12, 31),
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        assert contract_timeline.id == 1
        assert contract_timeline.employee_id == 123
        assert contract_timeline.contract_number == "CONTRACT-2024-001"
        assert contract_timeline.contract_name == "Employment Contract 2024"
        assert contract_timeline.contract_type == "FULL_TIME"
        assert contract_timeline.is_active is True
        assert contract_timeline.created_at == now
        assert contract_timeline.updated_at == now
    
    def test_contract_timeline_repr(self):
        """Test string representation of contract timeline."""
        contract_timeline = EmployeeContractTimeline(
            id=1,
            employee_id=123,
            contract_number="CONTRACT-2024-001",
            contract_name="Employment Contract 2024",
            contract_type="FULL_TIME",
            start_date=date(2024, 1, 15),
            is_active=True
        )
        
        repr_str = repr(contract_timeline)
        
        assert "EmployeeContractTimeline" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "contract_number=CONTRACT-2024-001" in repr_str
    
    def test_contract_timeline_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeeContractTimeline.__tablename__ == "employee_contract_timeline"


class TestEmployeeWorkScheduleModel:
    """Test EmployeeWorkSchedule model behavior."""
    
    def test_work_schedule_creation(self):
        """Test creating work schedule instance."""
        now = datetime.now(timezone.utc)
        
        work_schedule = EmployeeWorkSchedule(
            id=1,
            employee_id=123,
            effective_from=date(2024, 1, 15),
            effective_to=date(2024, 12, 31),
            schedule_type="STANDARD",
            standard_hours_per_day=8.0,
            total_hours_per_week=40.0,
            monday_hours=8.0,
            tuesday_hours=8.0,
            wednesday_hours=8.0,
            thursday_hours=8.0,
            friday_hours=8.0,
            saturday_hours=0.0,
            sunday_hours=0.0,
            is_current=True,
            created_at=now,
            updated_at=now
        )
        
        assert work_schedule.id == 1
        assert work_schedule.employee_id == 123
        assert work_schedule.effective_from == date(2024, 1, 15)
        assert work_schedule.schedule_type == "STANDARD"
        assert work_schedule.total_hours_per_week == 40.0
        assert work_schedule.is_current is True
        assert work_schedule.created_at == now
        assert work_schedule.updated_at == now
    
    def test_work_schedule_repr(self):
        """Test string representation of work schedule."""
        work_schedule = EmployeeWorkSchedule(
            id=1,
            employee_id=123,
            effective_from=date(2024, 1, 15),
            schedule_type="STANDARD",
            total_hours_per_week=40.0,
            is_current=True
        )
        
        repr_str = repr(work_schedule)
        
        assert "EmployeeWorkSchedule" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "schedule_type=STANDARD" in repr_str
    
    def test_work_schedule_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeeWorkSchedule.__tablename__ == "employee_work_schedule"


class TestEmployeePayrollRecordModel:
    """Test EmployeePayrollRecord model behavior."""
    
    def test_payroll_record_creation(self):
        """Test creating payroll record instance."""
        now = datetime.now(timezone.utc)
        
        payroll_record = EmployeePayrollRecord(
            id=1,
            employee_id=123,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            base_salary=5000.0,
            total_compensation=5500.0,
            status="PAID",
            payment_date=date(2024, 2, 1),
            created_at=now,
            updated_at=now
        )
        
        assert payroll_record.id == 1
        assert payroll_record.employee_id == 123
        assert payroll_record.period_start == date(2024, 1, 1)
        assert payroll_record.period_end == date(2024, 1, 31)
        assert payroll_record.base_salary == 5000.0
        assert payroll_record.total_compensation == 5500.0
        assert payroll_record.status == "PAID"
        assert payroll_record.payment_date == date(2024, 2, 1)
        assert payroll_record.created_at == now
        assert payroll_record.updated_at == now
    
    def test_payroll_record_repr(self):
        """Test string representation of payroll record."""
        payroll_record = EmployeePayrollRecord(
            id=1,
            employee_id=123,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            base_salary=5000.0,
            total_compensation=5500.0,
            status="PAID"
        )
        
        repr_str = repr(payroll_record)
        
        assert "EmployeePayrollRecord" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "base_salary=5000.0" in repr_str
    
    def test_payroll_record_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeePayrollRecord.__tablename__ == "employee_payroll_record"


class TestEmployeePayrollItemModel:
    """Test EmployeePayrollItem model behavior."""
    
    def test_payroll_item_creation(self):
        """Test creating payroll item instance."""
        now = datetime.now(timezone.utc)
        
        payroll_item = EmployeePayrollItem(
            id=1,
            payroll_record_id=123,
            category="EARNINGS",
            item_type="BASE_SALARY",
            description="Monthly base salary",
            amount=5000.0,
            currency="USD",
            quantity=1.0,
            rate=5000.0,
            meta_data={"tax_year": 2024},
            created_at=now,
            updated_at=now
        )
        
        assert payroll_item.id == 1
        assert payroll_item.payroll_record_id == 123
        assert payroll_item.category == "EARNINGS"
        assert payroll_item.item_type == "BASE_SALARY"
        assert payroll_item.amount == 5000.0
        assert payroll_item.currency == "USD"
        assert payroll_item.meta_data == {"tax_year": 2024}
        assert payroll_item.created_at == now
        assert payroll_item.updated_at == now
    
    def test_payroll_item_repr(self):
        """Test string representation of payroll item."""
        payroll_item = EmployeePayrollItem(
            id=1,
            payroll_record_id=123,
            category="EARNINGS",
            item_type="BASE_SALARY",
            amount=5000.0,
            currency="USD"
        )
        
        repr_str = repr(payroll_item)
        
        assert "EmployeePayrollItem" in repr_str
        assert "id=1" in repr_str
        assert "payroll_record_id=123" in repr_str
        assert "category=EARNINGS" in repr_str
    
    def test_payroll_item_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeePayrollItem.__tablename__ == "employee_payroll_item"


class TestEmployeeBankInfoModel:
    """Test EmployeeBankInfo model behavior."""
    
    def test_bank_info_creation(self):
        """Test creating bank info instance."""
        now = datetime.now(timezone.utc)
        
        bank_info = EmployeeBankInfo(
            id=1,
            employee_id=123,
            bank_name="Chase Bank",
            account_number="1234567890",
            routing_number="021000021",
            account_type="CHECKING",
            account_holder_name="John Doe",
            account_holder_type="INDIVIDUAL",
            is_primary=True,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        assert bank_info.id == 1
        assert bank_info.employee_id == 123
        assert bank_info.bank_name == "Chase Bank"
        assert bank_info.account_number == "1234567890"
        assert bank_info.routing_number == "021000021"
        assert bank_info.is_primary is True
        assert bank_info.is_active is True
        assert bank_info.created_at == now
        assert bank_info.updated_at == now
    
    def test_bank_info_repr(self):
        """Test string representation of bank info."""
        bank_info = EmployeeBankInfo(
            id=1,
            employee_id=123,
            bank_name="Chase Bank",
            account_number="1234567890",
            routing_number="021000021",
            account_type="CHECKING",
            account_holder_name="John Doe",
            account_holder_type="INDIVIDUAL"
        )
        
        repr_str = repr(bank_info)
        
        assert "EmployeeBankInfo" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "bank_name=Chase Bank" in repr_str
    
    def test_bank_info_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeeBankInfo.__tablename__ == "employee_bank_info"


class TestEmployeeDependentModel:
    """Test EmployeeDependent model behavior."""
    
    def test_dependent_creation(self):
        """Test creating dependent instance."""
        now = datetime.now(timezone.utc)
        
        dependent = EmployeeDependent(
            id=1,
            employee_id=123,
            name="Jane Doe",
            relationship_type="SPOUSE",
            date_of_birth=date(1992, 5, 20),
            gender="FEMALE",
            nationality="American",
            primary_address="123 Main St",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001",
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        assert dependent.id == 1
        assert dependent.employee_id == 123
        assert dependent.name == "Jane Doe"
        assert dependent.relationship_type == "SPOUSE"
        assert dependent.date_of_birth == date(1992, 5, 20)
        assert dependent.is_active is True
        assert dependent.created_at == now
        assert dependent.updated_at == now
    
    def test_dependent_repr(self):
        """Test string representation of dependent."""
        dependent = EmployeeDependent(
            id=1,
            employee_id=123,
            name="Jane Doe",
            relationship_type="SPOUSE",
            date_of_birth=date(1992, 5, 20),
            is_active=True
        )
        
        repr_str = repr(dependent)
        
        assert "EmployeeDependent" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "name=Jane Doe" in repr_str
    
    def test_dependent_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeeDependent.__tablename__ == "employee_dependent"


class TestEmployeeDocumentModel:
    """Test EmployeeDocument model behavior."""
    
    def test_document_creation(self):
        """Test creating document instance."""
        now = datetime.now(timezone.utc)
        
        document = EmployeeDocument(
            id=1,
            employee_id=123,
            document_type="PASSPORT",
            file_name="passport.pdf",
            file_path="/uploads/passport_123.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            upload_date=now,
            uploaded_by_user_id=456,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        assert document.id == 1
        assert document.employee_id == 123
        assert document.document_type == "PASSPORT"
        assert document.file_name == "passport.pdf"
        assert document.file_size == 1024000
        assert document.uploaded_by_user_id == 456
        assert document.is_active is True
        assert document.created_at == now
        assert document.updated_at == now
    
    def test_document_repr(self):
        """Test string representation of document."""
        document = EmployeeDocument(
            id=1,
            employee_id=123,
            document_type="PASSPORT",
            file_name="passport.pdf",
            file_path="/uploads/passport_123.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            uploaded_by_user_id=456
        )
        
        repr_str = repr(document)
        
        assert "EmployeeDocument" in repr_str
        assert "id=1" in repr_str
        assert "employee_id=123" in repr_str
        assert "document_type=PASSPORT" in repr_str
    
    def test_document_tablename(self):
        """Test that table name is set correctly."""
        assert EmployeeDocument.__tablename__ == "employee_document"

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, DateTime, ForeignKey, Boolean, Float, JSON, Integer
from typing import List
from datetime import datetime, date, timezone
from models.user import User

class Employee(Base):
    """
    Employee model for managing employee data.
    """
    
    __tablename__ = "employees"
    
    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=True)
    join_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="employees")
    
    # One-to-One relationships (one employee has one personal details record)
    personal_details: Mapped["EmployeePersonalDetails"] = relationship("EmployeePersonalDetails", back_populates="employee", uselist=False)
    bank_info: Mapped["EmployeeBankInfo"] = relationship("EmployeeBankInfo", back_populates="employee", uselist=False)
    
    # One-to-Many relationships (one employee can have multiple records)
    job_timeline: Mapped[List["EmployeeJobTimeline"]] = relationship("EmployeeJobTimeline", back_populates="employee", uselist=True, foreign_keys="EmployeeJobTimeline.employee_id")
    contract_timeline: Mapped[List["EmployeeContractTimeline"]] = relationship("EmployeeContractTimeline", back_populates="employee", uselist=True)
    work_schedule: Mapped[List["EmployeeWorkSchedule"]] = relationship("EmployeeWorkSchedule", back_populates="employee", uselist=True)
    payroll_records: Mapped[List["EmployeePayrollRecord"]] = relationship("EmployeePayrollRecord", back_populates="employee", uselist=True)
    dependents: Mapped[List["EmployeeDependent"]] = relationship("EmployeeDependent", back_populates="employee", uselist=True)
    documents: Mapped[List["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="employee", uselist=True)
    
    # New payroll-related relationships
    one_off_payments: Mapped[List["EmployeeOneOffPayment"]] = relationship("EmployeeOneOffPayment", back_populates="employee", uselist=True)
    time_off_records: Mapped[List["EmployeeTimeOff"]] = relationship("EmployeeTimeOff", back_populates="employee", uselist=True)
    overtime_records: Mapped[List["EmployeeOvertime"]] = relationship("EmployeeOvertime", back_populates="employee", uselist=True)
    deficit_records: Mapped[List["EmployeeDeficit"]] = relationship("EmployeeDeficit", back_populates="employee", uselist=True)
    attendance_records: Mapped[List["EmployeeAttendance"]] = relationship("EmployeeAttendance", back_populates="employee", uselist=True)

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, phone={self.phone}, join_date={self.join_date})>"

class EmployeePersonalDetails(Base):
    """
    Employee personal details model for managing employee personal details.
    """
    
    __tablename__ = "employee_personal_details"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, unique=True)  # One-to-One relationship
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    nationality: Mapped[str] = mapped_column(String(100), nullable=True)
    health_care_provider: Mapped[str] = mapped_column(String(255), nullable=True)
    marital_status: Mapped[str] = mapped_column(String(20), nullable=True)
    personal_tax_id: Mapped[str] = mapped_column(String(50), nullable=True)
    social_insurance_number: Mapped[str] = mapped_column(String(50), nullable=True)
    primary_address: Mapped[str] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="personal_details")

    def __repr__(self) -> str:
        return f"<EmployeePersonalDetails(id={self.id}, employee_id={self.employee_id}, gender={self.gender}, date_of_birth={self.date_of_birth}, nationality={self.nationality}, health_care_provider={self.health_care_provider}, marital_status={self.marital_status}, personal_tax_id={self.personal_tax_id}, social_insurance_number={self.social_insurance_number}, primary_address={self.primary_address}, city={self.city}, state={self.state}, country={self.country}, postal_code={self.postal_code})>"

class EmployeeJobTimeline(Base):
    """
    Employee job timeline model for managing employee job timeline.
    """
    
    __tablename__ = "employee_job_timeline"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)  # When this job position ended
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    position_type: Mapped[str] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    line_manager_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    office: Mapped[str] = mapped_column(String(100), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="job_timeline", foreign_keys=[employee_id])

    def __repr__(self) -> str:
        return f"<EmployeeJobTimeline(id={self.id}, employee_id={self.employee_id}, effective_date={self.effective_date}, job_title={self.job_title}, position_type={self.position_type}, employment_type={self.employment_type}, line_manager_id={self.line_manager_id}, department={self.department}, office={self.office}, is_current={self.is_current})>"

class EmployeeContractTimeline(Base):
    """
    Employee contract timeline model for managing employee contract timeline.
    """
    
    __tablename__ = "employee_contract_timeline"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    contract_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="contract_timeline")

    def __repr__(self) -> str:
        return f"<EmployeeContractTimeline(id={self.id}, employee_id={self.employee_id}, contract_number={self.contract_number}, contract_name={self.contract_name}, contract_type={self.contract_type}, start_date={self.start_date}, end_date={self.end_date}, is_active={self.is_active})>"

class EmployeeWorkSchedule(Base):
    """
    Employee work schedule model for managing employee work schedule.
    """
    
    __tablename__ = "employee_work_schedule"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date] = mapped_column(Date, nullable=True)  # When this schedule ends
    schedule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    standard_hours_per_day: Mapped[float] = mapped_column(Float, nullable=True)
    total_hours_per_week: Mapped[float] = mapped_column(Float, nullable=False)
    monday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    tuesday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    wednesday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    thursday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    friday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    saturday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    sunday_hours: Mapped[float] = mapped_column(Float, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="work_schedule")

    def __repr__(self) -> str:
        return f"<EmployeeWorkSchedule(id={self.id}, employee_id={self.employee_id}, schedule_type={self.schedule_type}, standard_hours_per_day={self.standard_hours_per_day}, total_hours_per_week={self.total_hours_per_week}, monday_hours={self.monday_hours}, tuesday_hours={self.tuesday_hours}, wednesday_hours={self.wednesday_hours}, thursday_hours={self.thursday_hours}, friday_hours={self.friday_hours}, saturday_hours={self.saturday_hours}, sunday_hours={self.sunday_hours})>"

class EmployeePayrollRecord(Base):
    """
    Employee payroll record model for managing employee payroll record.
    """
    
    __tablename__ = "employee_payroll_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    base_salary: Mapped[float] = mapped_column(Float, nullable=False)
    total_compensation: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="payroll_records")
    payroll_items: Mapped[List["EmployeePayrollItem"]] = relationship("EmployeePayrollItem", back_populates="payroll_record")
    
    # New payroll-related relationships
    one_off_payments: Mapped[List["EmployeeOneOffPayment"]] = relationship("EmployeeOneOffPayment", back_populates="payroll_record")
    overtime_records: Mapped[List["EmployeeOvertime"]] = relationship("EmployeeOvertime", back_populates="payroll_record")
    deficit_records: Mapped[List["EmployeeDeficit"]] = relationship("EmployeeDeficit", back_populates="payroll_record")
    attendance_records: Mapped[List["EmployeeAttendance"]] = relationship("EmployeeAttendance", back_populates="payroll_record")

    def __repr__(self) -> str:
        return f"<EmployeePayrollRecord(id={self.id}, employee_id={self.employee_id}, period_start={self.period_start}, period_end={self.period_end}, base_salary={self.base_salary}, total_compensation={self.total_compensation}, status={self.status}, payment_date={self.payment_date})>"

class EmployeePayrollItem(Base):
    """
    Employee payroll item model for managing employee payroll item.
    """
    
    __tablename__ = "employee_payroll_item"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    payroll_record_id: Mapped[int] = mapped_column(ForeignKey("employee_payroll_record.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    quantity: Mapped[float] = mapped_column(Float, nullable=True)
    rate: Mapped[float] = mapped_column(Float, nullable=True)
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    payroll_record: Mapped["EmployeePayrollRecord"] = relationship("EmployeePayrollRecord", back_populates="payroll_items")

    def __repr__(self) -> str:
        return f"<EmployeePayrollItem(id={self.id}, payroll_record_id={self.payroll_record_id}, category={self.category}, item_type={self.item_type}, description={self.description}, amount={self.amount}, currency={self.currency}, quantity={self.quantity}, rate={self.rate}, meta_data={self.meta_data})>"

class EmployeeOneOffPayment(Base):
    """
    Employee one-off payment model for managing one-time payments, bonuses, incentives.
    """
    __tablename__ = "employee_one_off_payment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    payroll_record_id: Mapped[int] = mapped_column(ForeignKey("employee_payroll_record.id"), nullable=True)  # Optional link to payroll period
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Name of the one-off item
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Type: bonus, incentive, commission, etc.
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Payment amount
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")  # Currency code
    payment_date: Mapped[date] = mapped_column(Date, nullable=True)  # When payment was made
    description: Mapped[str] = mapped_column(String(500), nullable=True)  # Additional description
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee")
    payroll_record: Mapped["EmployeePayrollRecord"] = relationship("EmployeePayrollRecord")

    def __repr__(self) -> str:
        return f"<EmployeeOneOffPayment(id={self.id}, employee_id={self.employee_id}, item_name={self.item_name}, item_type={self.item_type}, amount={self.amount}, currency={self.currency}, payment_date={self.payment_date})>"

class EmployeeTimeOff(Base):
    """
    Employee time-off model for managing vacation, sick leave, and other time-off tracking.
    """
    __tablename__ = "employee_time_off"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    time_off_type: Mapped[str] = mapped_column(String(50), nullable=False)  # vacation, sick_leave, personal, etc.
    days_used: Mapped[float] = mapped_column(Float, nullable=False, default=0)  # Days used in this period
    days_remaining: Mapped[float] = mapped_column(Float, nullable=True)  # Days remaining
    amount: Mapped[float] = mapped_column(Float, nullable=True)  # Monetary value if applicable
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")  # Currency code
    period_start: Mapped[date] = mapped_column(Date, nullable=True)  # Time-off period start
    period_end: Mapped[date] = mapped_column(Date, nullable=True)  # Time-off period end
    description: Mapped[str] = mapped_column(String(500), nullable=True)  # Additional description
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee")

    def __repr__(self) -> str:
        return f"<EmployeeTimeOff(id={self.id}, employee_id={self.employee_id}, time_off_type={self.time_off_type}, days_used={self.days_used}, days_remaining={self.days_remaining}, amount={self.amount}, currency={self.currency})>"

class EmployeeOvertime(Base):
    """
    Employee overtime model for managing overtime hours and payments.
    """
    __tablename__ = "employee_overtime"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    payroll_record_id: Mapped[int] = mapped_column(ForeignKey("employee_payroll_record.id"), nullable=True)  # Optional link to payroll period
    overtime_date: Mapped[date] = mapped_column(Date, nullable=False)  # Date of overtime work
    hours: Mapped[float] = mapped_column(Float, nullable=False)  # Overtime hours worked
    rate: Mapped[float] = mapped_column(Float, nullable=False)  # Overtime rate per hour
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Total overtime amount (hours * rate)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")  # Currency code
    overtime_type: Mapped[str] = mapped_column(String(50), nullable=True)  # regular, holiday, weekend, etc.
    description: Mapped[str] = mapped_column(String(500), nullable=True)  # Additional description
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee")
    payroll_record: Mapped["EmployeePayrollRecord"] = relationship("EmployeePayrollRecord")

    def __repr__(self) -> str:
        return f"<EmployeeOvertime(id={self.id}, employee_id={self.employee_id}, overtime_date={self.overtime_date}, hours={self.hours}, rate={self.rate}, amount={self.amount}, currency={self.currency})>"

class EmployeeDeficit(Base):
    """
    Employee deficit model for managing time deficits and penalties.
    """
    __tablename__ = "employee_deficit"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    payroll_record_id: Mapped[int] = mapped_column(ForeignKey("employee_payroll_record.id"), nullable=True)  # Optional link to payroll period
    deficit_type: Mapped[str] = mapped_column(String(50), nullable=False)  # regular, penalty, adjustment, etc.
    deficit_hours: Mapped[str] = mapped_column(String(50), nullable=True)  # Deficit hours (e.g., "-13h 30m")
    deficit_amount: Mapped[float] = mapped_column(Float, nullable=False)  # Monetary deficit amount
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")  # Currency code
    period_start: Mapped[date] = mapped_column(Date, nullable=True)  # Deficit period start
    period_end: Mapped[date] = mapped_column(Date, nullable=True)  # Deficit period end
    description: Mapped[str] = mapped_column(String(500), nullable=True)  # Additional description
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee")
    payroll_record: Mapped["EmployeePayrollRecord"] = relationship("EmployeePayrollRecord")

    def __repr__(self) -> str:
        return f"<EmployeeDeficit(id={self.id}, employee_id={self.employee_id}, deficit_type={self.deficit_type}, deficit_hours={self.deficit_hours}, deficit_amount={self.deficit_amount}, currency={self.currency})>"

class EmployeeAttendance(Base):
    """
    Employee attendance model for tracking work hours vs expected hours.
    """
    __tablename__ = "employee_attendance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    payroll_record_id: Mapped[int] = mapped_column(ForeignKey("employee_payroll_record.id"), nullable=True)  # Optional link to payroll period
    period: Mapped[str] = mapped_column(String(100), nullable=False)  # Period description (e.g., "Week 1", "Month 1")
    expected_hours: Mapped[float] = mapped_column(Float, nullable=False)  # Expected work hours for period
    actual_work_hours: Mapped[float] = mapped_column(Float, nullable=False)  # Actual hours worked
    period_start: Mapped[date] = mapped_column(Date, nullable=True)  # Period start date
    period_end: Mapped[date] = mapped_column(Date, nullable=True)  # Period end date
    description: Mapped[str] = mapped_column(String(500), nullable=True)  # Additional description
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee")
    payroll_record: Mapped["EmployeePayrollRecord"] = relationship("EmployeePayrollRecord")

    def __repr__(self) -> str:
        return f"<EmployeeAttendance(id={self.id}, employee_id={self.employee_id}, period={self.period}, expected_hours={self.expected_hours}, actual_work_hours={self.actual_work_hours})>"

class EmployeeBankInfo(Base):
    """
    Employee bank info model for managing employee bank info.
    """
    __tablename__ = "employee_bank_info"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, unique=True)  # One-to-One relationship
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=True)  # Bank branch name
    swift_bic: Mapped[str] = mapped_column(String(11), nullable=True)  # SWIFT/BIC code for international transfers
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    routing_number: Mapped[str] = mapped_column(String(20), nullable=False)
    iban: Mapped[str] = mapped_column(String(34), nullable=True)  # IBAN for European/international accounts
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_holder_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="bank_info")

    def __repr__(self) -> str:
        return f"<EmployeeBankInfo(id={self.id}, employee_id={self.employee_id}, bank_name={self.bank_name}, account_number={self.account_number}, routing_number={self.routing_number}, account_type={self.account_type}, account_holder_name={self.account_holder_name}, account_holder_type={self.account_holder_type})>"

class EmployeeDependent(Base):
    """
    Employee dependent model for managing employee dependent.
    """
    
    __tablename__ = "employee_dependent"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)  # Make nullable
    gender: Mapped[str] = mapped_column(String(20), nullable=True)  # Make nullable
    nationality: Mapped[str] = mapped_column(String(100), nullable=True)  # Make nullable
    primary_address: Mapped[str] = mapped_column(String(500), nullable=True)  # Make nullable
    city: Mapped[str] = mapped_column(String(100), nullable=True)  # Make nullable
    state: Mapped[str] = mapped_column(String(100), nullable=True)  # Make nullable
    country: Mapped[str] = mapped_column(String(100), nullable=True)  # Make nullable
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)  # Make nullable
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="dependents")

    def __repr__(self) -> str:
        return f"<EmployeeDependent(id={self.id}, employee_id={self.employee_id}, name={self.name}, relationship_type={self.relationship_type}, date_of_birth={self.date_of_birth}, gender={self.gender}, nationality={self.nationality}, primary_address={self.primary_address}, city={self.city}, state={self.state}, country={self.country}, postal_code={self.postal_code})>"

class EmployeeDocument(Base):
    """
    Employee document model for managing employee document.
    """
    
    __tablename__ = "employee_document"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="documents")

    def __repr__(self) -> str:
        return f"<EmployeeDocument(id={self.id}, employee_id={self.employee_id}, document_type={self.document_type}, file_name={self.file_name}, file_path={self.file_path}, file_size={self.file_size}, mime_type={self.mime_type}, upload_date={self.upload_date}, uploaded_by_user_id={self.uploaded_by_user_id})>"


export type EmploymentStatus = 'ACTIVE' | 'INACTIVE' | 'TERMINATED' | 'ON_LEAVE' | 'SUSPENDED'

export type EmployeePersonalDetails = {
    id: number
    employee_id: number
    gender: "MALE" | "FEMALE" | "OTHER" | "PREFER_NOT_TO_SAY"
    date_of_birth: string | null
    nationality: string | null
    health_care_provider: string | null
    marital_status: "SINGLE" | "MARRIED" | "DIVORCED" | "WIDOWED" | "SEPARATED"
    personal_tax_id: string | null
    social_insurance_number: string | null
    primary_address: string | null
    city: string | null
    state: string | null
    country: string | null
    postal_code: string | null
    created_at: string
    updated_at: string
}

export type EmployeeBankInfo = {
    id: number
    employee_id: number
    bank_name: string | null
    branch: string | null
    swift_bic: string | null
    account_number: string | null
    routing_number: string | null
    iban: string | null
    account_type: string | null
    account_holder_name: string | null
    account_holder_type: string | null
    is_primary: boolean
    is_active: boolean
    created_at: string
    updated_at: string
}

export type EmployeeJobTimeline = {
    id: number
    employee_id: number
    effective_date: string | null
    end_date: string | null
    job_title: string | null
    position_type: string | null
    employment_type: string | null
    line_manager_id: number | null
    department: string | null
    office: string | null
    is_current: boolean
    created_at: string
    updated_at: string
}

export type EmployeeContractTimeline = {
    id: number
    employee_id: number
    contract_title: string | null
    contract_type: string | null
    start_date: string | null
    end_date: string | null
    is_active: boolean
    created_at: string
    updated_at: string
}

export type EmployeeWorkSchedule = {
    id: number
    employee_id: number
    effective_from: string | null
    effective_to: string | null
    schedule_type: string | null
    standard_hours_per_day: number | null
    total_hours_per_week: number | null
    monday_hours: number | null
    tuesday_hours: number | null
    wednesday_hours: number | null
    thursday_hours: number | null
    friday_hours: number | null
    saturday_hours: number | null
    sunday_hours: number | null
    is_current: boolean
    created_at: string
    updated_at: string
    
}

export type EmployeePayrollItem = {
    id: number
      payroll_record_id: number
      category: string | null
      item_type: string | null
      description: string | null
      amount: number | null
      currency: string | null
      quantity: number | null
      rate: number | null
      meta_data: string | null
      created_at: string
      updated_at: string
}

export type EmployeePayrollRecord = {
    id: number
    employee_id: number
    period_start: string | null
    period_end: string | null
    base_salary: number | null
    total_compensation: number | null
    status: string | null
    payment_date: string | null
    payroll_items: EmployeePayrollItem[],
    created_at: string
    updated_at: string
    payroll_record_id: number | null
    payroll_record_name: string | null
    payroll_record_type: string | null
    payroll_record_start_date: string | null
    payroll_record_end_date: string | null
}

export type EmployeeDependent = {
    id: number
    employee_id: number
    name: string | null
    relationship_type: string | null
    date_of_birth: string | null
    gender: string | null
    nationality: string | null
    primary_address: string | null
    city: string | null
    state: string | null
    country: string | null
    postal_code: string | null
    is_active: boolean
    created_at: string
    updated_at: string
}

export type EmployeeDocument = {
    id: number
    employee_id: number
    document_type: string | null
    file_name: string | null
    file_path: string | null
    file_size: number | null
    mime_type: string | null
    upload_date: string | null
    uploaded_by_user_id: number | null
    is_active: boolean
    created_at: string
    updated_at: string
}
//  /employees/1; this gets an individual employee
export type Employee = {
  id: number
  user_id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  join_date: string
  employment_status: EmploymentStatus
  created_at: string
  updated_at: string
  personal_details: EmployeePersonalDetails
  bank_info: EmployeeBankInfo,
  job_timeline: EmployeeJobTimeline[],
  contract_timeline: EmployeeContractTimeline[],
  work_schedule: EmployeeWorkSchedule[],
  payroll_records: EmployeePayrollRecord[],
  dependents: EmployeeDependent[],
  documents: EmployeeDocument[],
}

// /employees; this gets all employees
export type Employees = {
  id: number
  user_id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  join_date: string
  created_at: string
  updated_at: string
  job_title: string | null
  department: string | null
  office: string | null
  line_manager_id: number | null
  line_manager_name: string | null
  employment_status: EmploymentStatus
}

export type CreateEmployeeRequest = {
    first_name: string
    last_name: string
    email: string
    phone: string
    join_date: string
    employment_status: EmploymentStatus
}
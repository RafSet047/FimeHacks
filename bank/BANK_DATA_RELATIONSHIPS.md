# Bank Data Relationships Documentation

## Overview
This document outlines the comprehensive relationships between all CSV files in the bank database system, showing how operational and strategic data are interconnected.

## Core Operational Tables

### 1. bank_customers.csv
- **Primary Key**: customer_id
- **Relationships**:
  - Links to `bank_accounts.csv` via customer_id
  - Links to `bank_loans.csv` via customer_id
  - Links to `bank_transactions.csv` via account_id (through bank_accounts)
  - Links to `bank_branches.csv` via branch_preference

### 2. bank_accounts.csv
- **Primary Key**: account_id
- **Foreign Keys**:
  - customer_id → bank_customers.customer_id
  - branch_id → bank_branches.branch_id
  - account_manager → bank_employees.employee_id
- **Relationships**:
  - Links to `bank_transactions.csv` via account_id
  - Links to `bank_customers.csv` via customer_id
  - Links to `bank_branches.csv` via branch_id
  - Links to `bank_employees.csv` via account_manager

### 3. bank_transactions.csv
- **Primary Key**: transaction_id
- **Foreign Keys**:
  - account_id → bank_accounts.account_id
  - branch_id → bank_branches.branch_id
  - teller_id → bank_employees.employee_id
- **Relationships**:
  - Links to `bank_accounts.csv` via account_id
  - Links to `bank_branches.csv` via branch_id
  - Links to `bank_employees.csv` via teller_id

### 4. bank_loans.csv
- **Primary Key**: loan_id
- **Foreign Keys**:
  - customer_id → bank_customers.customer_id
  - branch_id → bank_branches.branch_id
  - loan_officer → bank_employees.employee_id
- **Relationships**:
  - Links to `bank_customers.csv` via customer_id
  - Links to `bank_branches.csv` via branch_id
  - Links to `bank_employees.csv` via loan_officer

### 5. bank_branches.csv
- **Primary Key**: branch_id
- **Foreign Keys**:
  - manager_id → bank_employees.employee_id
- **Relationships**:
  - Links to `bank_employees.csv` via manager_id
  - Links to `bank_accounts.csv` via branch_id
  - Links to `bank_transactions.csv` via branch_id
  - Links to `bank_loans.csv` via branch_id

### 6. bank_employees.csv
- **Primary Key**: employee_id
- **Foreign Keys**:
  - manager_id → bank_employees.employee_id (self-referencing)
  - branch_id → bank_branches.branch_id
- **Relationships**:
  - Links to `bank_executives.csv` via employee_id
  - Links to `bank_branches.csv` via branch_id
  - Self-referencing via manager_id for organizational hierarchy

## Strategic Executive Tables

### 7. bank_executives.csv
- **Primary Key**: executive_id
- **Foreign Keys**:
  - employee_id → bank_employees.employee_id
  - mentor_id → bank_executives.executive_id (self-referencing)
- **Relationships**:
  - Links to `executive_meetings.csv` via chairperson_id/secretary_id
  - Links to `strategic_decisions.csv` via proposed_by/approved_by
  - Links to `budget_allocations.csv` via responsible_executive
  - Links to `executive_actions.csv` via assigned_to/assigned_by
  - Links to `executive_performance.csv` via executive_id
  - Links to `technology_projects.csv` via project_manager/executive_sponsor
  - Links to `acquisition_opportunities.csv` via responsible_executive

### 8. executive_meetings.csv
- **Primary Key**: meeting_id
- **Foreign Keys**:
  - chairperson_id → bank_executives.executive_id
  - secretary_id → bank_executives.executive_id
- **Relationships**:
  - Links to `strategic_decisions.csv` via meeting_id
  - Links to `executive_actions.csv` via meeting_id
  - Links to `budget_allocations.csv` via decision_id (through strategic_decisions)

### 9. strategic_decisions.csv
- **Primary Key**: decision_id
- **Foreign Keys**:
  - meeting_id → executive_meetings.meeting_id
  - proposed_by → bank_executives.executive_id
  - approved_by → bank_executives.executive_id
- **Relationships**:
  - Links to `budget_allocations.csv` via decision_id
  - Links to `risk_assessments.csv` via decision_id
  - Links to `executive_actions.csv` via decision_id
  - Links to `technology_projects.csv` via decision_id
  - Links to `acquisition_opportunities.csv` via decision_id

### 10. budget_allocations.csv
- **Primary Key**: budget_id
- **Foreign Keys**:
  - decision_id → strategic_decisions.decision_id
  - responsible_executive → bank_executives.executive_id
- **Relationships**:
  - Links to `strategic_decisions.csv` via decision_id
  - Links to `bank_executives.csv` via responsible_executive

### 11. risk_assessments.csv
- **Primary Key**: risk_id
- **Foreign Keys**:
  - decision_id → strategic_decisions.decision_id
  - risk_owner → bank_executives.executive_id
- **Relationships**:
  - Links to `strategic_decisions.csv` via decision_id
  - Links to `bank_executives.csv` via risk_owner

### 12. executive_actions.csv
- **Primary Key**: action_id
- **Foreign Keys**:
  - meeting_id → executive_meetings.meeting_id
  - decision_id → strategic_decisions.decision_id
  - assigned_to → bank_executives.executive_id
  - assigned_by → bank_executives.executive_id
- **Relationships**:
  - Links to `executive_meetings.csv` via meeting_id
  - Links to `strategic_decisions.csv` via decision_id
  - Links to `bank_executives.csv` via assigned_to/assigned_by

### 13. executive_performance.csv
- **Primary Key**: performance_id
- **Foreign Keys**:
  - executive_id → bank_executives.executive_id
  - reviewer_id → bank_executives.executive_id
- **Relationships**:
  - Links to `bank_executives.csv` via executive_id/reviewer_id

### 14. technology_projects.csv
- **Primary Key**: project_id
- **Foreign Keys**:
  - decision_id → strategic_decisions.decision_id
  - project_manager → bank_executives.executive_id
  - executive_sponsor → bank_executives.executive_id
- **Relationships**:
  - Links to `strategic_decisions.csv` via decision_id
  - Links to `bank_executives.csv` via project_manager/executive_sponsor

### 15. acquisition_opportunities.csv
- **Primary Key**: acquisition_id
- **Foreign Keys**:
  - decision_id → strategic_decisions.decision_id
  - responsible_executive → bank_executives.executive_id
- **Relationships**:
  - Links to `strategic_decisions.csv` via decision_id
  - Links to `bank_executives.csv` via responsible_executive

## Data Flow Relationships

### Strategic Decision Flow
1. **Executive Meetings** → **Strategic Decisions** → **Budget Allocations**
2. **Strategic Decisions** → **Risk Assessments** → **Executive Actions**
3. **Strategic Decisions** → **Technology Projects** → **Executive Actions**
4. **Strategic Decisions** → **Acquisition Opportunities** → **Executive Actions**

### Performance Tracking Flow
1. **Executive Performance** → **Strategic Goals** → **Success Metrics**
2. **Budget Allocations** → **Financial Performance** → **ROI Projections**
3. **Risk Assessments** → **Mitigation Strategies** → **Monitoring Frequency**

### Operational Integration
1. **Bank Employees** → **Bank Executives** → **Strategic Leadership**
2. **Bank Branches** → **Operational Performance** → **Strategic Initiatives**
3. **Bank Customers** → **Market Analysis** → **Strategic Decisions**

## Key Business Intelligence Queries

### Strategic Performance Analysis
- Executive performance vs. strategic goals
- Budget allocation effectiveness
- Risk assessment impact on decisions
- Technology project ROI analysis

### Operational Excellence
- Branch performance metrics
- Employee productivity analysis
- Customer satisfaction correlation
- Transaction volume trends

### Financial Performance
- Revenue growth by strategic initiative
- Cost optimization effectiveness
- Budget variance analysis
- ROI by department and project

### Risk Management
- Risk assessment trends
- Compliance score correlation
- Risk mitigation effectiveness
- Regulatory impact analysis

## Data Quality and Consistency

### Primary Key Constraints
- All tables have unique primary keys
- Foreign key relationships maintain referential integrity
- Executive IDs link operational and strategic data

### Temporal Consistency
- All strategic data uses consistent fiscal year (2024)
- Quarterly reporting alignment across all tables
- Meeting dates align with decision timelines

### Financial Consistency
- Budget allocations match strategic decision amounts
- Performance metrics align with success criteria
- ROI projections based on consistent methodology

This comprehensive data structure enables executive-level strategic analysis while maintaining operational data integrity and providing a complete view of the bank's performance across all dimensions. 
# SESF v3 Complete Examples

Six complete specifications demonstrating every SESF v3 tier and style. Examples 1-3 are declarative (BEHAVIOR-centric), showing rules about what must be true. Examples 4-6 are procedural (PROCEDURE-centric), showing step-by-step processes. Together they cover the full range of SESF v3. Each is a working spec with concrete data, suitable as a reference when writing new specifications.

---

## Example 1: Micro Tier -- Email Address Validator

```
Email Address Validator

Meta: Version 1.0.0 | Date 2026-03-01 | Domain: Input Validation | Status: active | Tier: micro

Purpose
Validate that a given string is a structurally valid email address before passing it to downstream systems.

BEHAVIOR validate_email: Check that an input string conforms to basic email address structure

  RULE contains_at_sign:
    input MUST contain exactly one "@" character

  RULE has_domain:
    WHEN input contains "@"
    THEN the portion after "@" MUST contain at least one "." character
         AND the portion after "@" MUST be at least 3 characters long

  ERROR invalid_email:
    WHEN input fails contains_at_sign OR has_domain
    SEVERITY critical
    ACTION reject input
    MESSAGE "Invalid email address: does not meet structural requirements"

  EXAMPLE valid_email:
    INPUT: "reggie.chan@tenebrus.ca"
    EXPECTED: { "valid": true }
    NOTES: Contains one @ with a valid domain portion (tenebrus.ca)

  EXAMPLE missing_at_sign:
    INPUT: "reggie.chan.tenebrus.ca"
    EXPECTED: { "valid": false,
                "error": "Invalid email address: does not meet structural requirements" }
    NOTES: No @ character present — triggers contains_at_sign rule failure

Constraints
* Validation is structural only — does not verify that the domain exists or accepts mail
```

---

## Example 2: Standard Tier -- Commercial Lease Abstraction

```
Commercial Lease Abstraction

Meta
* Version: 2.0.0
* Date: 2026-03-01
* Domain: Real Estate / Document Processing
* Status: active
* Tier: standard

Purpose
Extract structured data from commercial lease PDF documents to populate a standardized
lease database for portfolio management and analysis. Focuses on the five core extraction
concerns: parties, premises, term, rent, and overall confidence scoring.

Scope
* IN SCOPE: Party identification (landlord, tenant), premises details,
  lease term dates, rent and escalation terms, extraction confidence scoring
* OUT OF SCOPE: Legal clause interpretation, market rent analysis,
  negotiation recommendations, amendment tracking, estoppel generation

Inputs
* lease_pdf: file - PDF document of a commercial lease agreement - required
* property_id: string - portfolio identifier for the property - optional

Outputs
* lease_data: LeaseData - structured lease information with all extracted fields
* confidence: number - overall extraction confidence score (0.0 to 1.0)
* warnings: list of string - issues encountered during extraction

Types

LeaseData {
  parties: Parties, required
  premises: Premises, required
  term: Term, required
  rent: Rent, required
}

Parties {
  landlord: Party, required
  tenant: Party, required
}

Party {
  name: string, required
  entity_type: enum [Individual, Corporation, LLC, Partnership, Trust], optional
  address: string, optional
}

Premises {
  address: string, required
  city: string, required
  province_or_state: string, required
  postal_code: string, optional
  sqft: number, required
  unit: string, optional
  permitted_use: string, optional
}

Term {
  commencement: date, required
  expiration: date, required
  months: integer, required
}

Rent {
  base_amount: number, required
  period: enum [monthly, annual, psf_annual], required
  currency: enum [CAD, USD], default: CAD
  escalations: list of Escalation, optional
}

Escalation {
  effective_date: date, required
  new_amount: number, required
  method: enum [fixed, percentage, CPI], required
}

Functions

FUNCTION months_between(start, end):
  year_diff = end.year - start.year
  month_diff = end.month - start.month
  RETURNS (year_diff * 12) + month_diff

FUNCTION annual_rent(rent, sqft):
  IF rent.period = "monthly" THEN
    result = rent.base_amount * 12
  ELSE IF rent.period = "annual" THEN
    result = rent.base_amount
  ELSE IF rent.period = "psf_annual" THEN
    result = rent.base_amount * sqft
  RETURNS result

FUNCTION confidence_score(extracted, required_fields):
  found = count of required_fields where value is not null
  total = count of required_fields
  RETURNS found / total

BEHAVIOR party_extraction: Identify landlord and tenant entities from the lease document

  RULE landlord_required:
    parties.landlord MUST be present
    AND parties.landlord.name MUST NOT be empty

  RULE tenant_required:
    parties.tenant MUST be present
    AND parties.tenant.name MUST NOT be empty

  RULE entity_type_inference:
    WHEN party name contains "Inc", "Corp", "Ltd", or "Limited"
    THEN entity_type SHOULD be set to "Corporation"

  ERROR missing_landlord:
    WHEN parties.landlord is null or parties.landlord.name is empty
    SEVERITY critical
    ACTION halt extraction
    MESSAGE "Could not identify landlord in lease document"

  ERROR missing_tenant:
    WHEN parties.tenant is null or parties.tenant.name is empty
    SEVERITY critical
    ACTION halt extraction
    MESSAGE "Could not identify tenant in lease document"

  EXAMPLE successful_party_extraction:
    INPUT: { "lease_pdf": "456_queen_west_lease.pdf" }
    EXPECTED: {
      "parties": {
        "landlord": { "name": "Brookfield Asset Management Ltd.", "entity_type": "Corporation", "address": "181 Bay Street, Suite 300, Toronto, ON M5J 2T3" },
        "tenant": { "name": "Northern Lights Coffee Inc.", "entity_type": "Corporation", "address": "456 Queen Street West, Toronto, ON M5V 2A8" }
      }
    }
    NOTES: Both parties extracted with entity_type inferred from "Ltd." and "Inc."

  EXAMPLE missing_landlord_case:
    INPUT: { "lease_pdf": "damaged_scan_lease.pdf" }
    EXPECTED: {
      "error": "Could not identify landlord in lease document",
      "confidence": 0.0
    }
    NOTES: OCR damage obscured first page — landlord name unreadable. Extraction halts.


BEHAVIOR premises_extraction: Extract physical property details from the lease

  RULE sqft_positive:
    premises.sqft MUST be greater than zero

  RULE address_required:
    premises.address MUST NOT be empty
         AND premises.city MUST NOT be empty

  RULE sqft_reasonableness:
    premises.sqft SHOULD be between 100 and 2000000
    -- flag outliers for review

  ERROR missing_sqft:
    WHEN premises.sqft is null or premises.sqft = 0
    SEVERITY warning
    ACTION continue with flag
    MESSAGE "Square footage not found -- may require manual review"

  EXAMPLE complete_premises:
    INPUT: { "lease_pdf": "456_queen_west_lease.pdf" }
    EXPECTED: {
      "premises": { "address": "456 Queen Street West, Unit 2B", "city": "Toronto", "province_or_state": "ON", "postal_code": "M5V 2A8", "sqft": 3200, "unit": "2B", "permitted_use": "Retail food service and ancillary uses" }
    }

  EXAMPLE missing_sqft_case:
    INPUT: { "lease_pdf": "older_format_lease.pdf" }
    EXPECTED: {
      "premises": {
        "address": "89 Wellington Street East",
        "city": "Aurora",
        "province_or_state": "ON",
        "sqft": null
      },
      "warnings": ["Square footage not found -- may require manual review"]
    }
    NOTES: Older lease format did not include sqft. Extraction continues with warning.


BEHAVIOR term_extraction: Extract and validate lease commencement and expiration dates

  RULE expiration_after_commencement:
    term.expiration MUST be after term.commencement

  RULE months_calculation:
    term.months MUST equal months_between(term.commencement, term.expiration)

  RULE term_reasonableness:
    term.months SHOULD be between 1 and 300
    -- flag unusual terms for review

  ERROR date_parse_failure:
    WHEN commencement or expiration date cannot be parsed from document text
    SEVERITY critical
    ACTION halt extraction
    MESSAGE "Could not parse lease term dates from document"

  EXAMPLE valid_five_year_term:
    INPUT: { "lease_pdf": "456_queen_west_lease.pdf" }
    EXPECTED: {
      "term": {
        "commencement": "2026-07-01",
        "expiration": "2031-06-30",
        "months": 60
      }
    }
    NOTES: Standard 5-year commercial term. months_between(2026-07-01, 2031-06-30) = 60.

  EXAMPLE invalid_dates_case:
    INPUT: { "lease_pdf": "corrupted_dates_lease.pdf" }
    EXPECTED: {
      "error": "Could not parse lease term dates from document"
    }
    NOTES: Document contained handwritten date amendments that OCR could not resolve.


BEHAVIOR rent_extraction: Extract base rent, payment period, and escalation schedule

  RULE positive_rent:
    rent.base_amount MUST be greater than zero

  RULE escalation_chronology:
    WHEN rent.escalations is present
    THEN each escalation.effective_date MUST be after term.commencement
    AND escalation dates MUST be in ascending order

  ERROR missing_rent:
    WHEN rent.base_amount is null or rent.base_amount <= 0
    SEVERITY critical
    ACTION halt extraction
    MESSAGE "Could not extract base rent amount from document"

  EXAMPLE psf_rent_with_escalations:
    INPUT: { "lease_pdf": "456_queen_west_lease.pdf" }
    EXPECTED: {
      "rent": {
        "base_amount": 32.50,
        "period": "psf_annual",
        "currency": "CAD",
        "escalations": [
          { "effective_date": "2027-07-01", "new_amount": 33.48, "method": "percentage" },
          { "effective_date": "2028-07-01", "new_amount": 34.48, "method": "percentage" },
          { "effective_date": "2029-07-01", "new_amount": 35.51, "method": "percentage" },
          { "effective_date": "2030-07-01", "new_amount": 36.58, "method": "percentage" }
        ]
      }
    }
    NOTES: $32.50 PSF with ~3% annual escalations. annual_rent(rent, 3200) = $104,000 in year one.

  EXAMPLE monthly_rent_no_escalations:
    INPUT: { "lease_pdf": "simple_retail_lease.pdf" }
    EXPECTED: {
      "rent": {
        "base_amount": 4500.00,
        "period": "monthly",
        "currency": "CAD",
        "escalations": []
      }
    }
    NOTES: Flat $4,500/month with no escalations. annual_rent(rent, null) = $54,000.


BEHAVIOR confidence_scoring: Compute overall extraction confidence based on field completeness

  RULE confidence_calculation:
    confidence MUST equal confidence_score(lease_data, [parties.landlord, parties.tenant, premises.address, premises.sqft, term.commencement, term.expiration, rent.base_amount])

  RULE confidence_range:
    confidence MUST be between 0.0 and 1.0

  EXAMPLE high_confidence:
    INPUT: { "extracted_fields": ["parties.landlord", "parties.tenant", "premises.address", "premises.sqft", "term.commencement", "term.expiration", "rent.base_amount"] }
    EXPECTED: { "confidence": 1.0 }
    NOTES: All 7 required fields extracted. 7/7 = 1.0.

  EXAMPLE low_confidence:
    INPUT: { "extracted_fields": ["parties.tenant", "premises.address", "rent.base_amount"] }
    EXPECTED: { "confidence": 0.43 }
    NOTES: Only 3 of 7 required fields found. 3/7 = 0.43. Missing landlord, sqft, and both dates.

Constraints
* Extraction MUST handle PDFs up to 200 pages
* OCR MUST be applied to scanned documents automatically
* Processing time SHOULD NOT exceed 30 seconds per document
* All monetary amounts MUST preserve precision to 2 decimal places
* Date parsing MUST support formats: YYYY-MM-DD, MM/DD/YYYY, DD-Mon-YYYY, written-out months

Dependencies
* PDF processing library with OCR capability (e.g., Tesseract, Amazon Textract)
* Date parsing library supporting multiple North American date formats
* Text extraction engine with layout preservation for tabular rent schedules
```

---

## Example 3: Complex Tier -- Purchase Order Approval Workflow

```
Purchase Order Approval Workflow

Meta
* Version: 2.1.0
* Date: 2026-03-01
* Domain: Finance / Procurement
* Status: active
* Tier: complex

Purpose
Route purchase order requests through the appropriate approval chain based on dollar
thresholds, department policies, and urgency levels. Manage notification dispatch,
timeout escalation, and state transitions to ensure proper financial controls while
allowing emergency overrides for time-critical needs.

Scope
* IN SCOPE: PO validation, approval routing by amount threshold, emergency override,
  notification dispatch (sequential and parallel), timeout escalation, state management
* OUT OF SCOPE: Purchase order creation UI, vendor management, payment processing,
  budget tracking, three-way matching

Audience
* AI agents: This spec drives an automated workflow engine. Each behavior is
  self-contained. Process behaviors in PRECEDENCE order when a PO enters the system.
* Human reviewers: Start with approval_routing to understand threshold logic,
  then read notification_dispatch and timeout_escalation for the async flow.
* Administrators: Threshold amounts and timeout durations are defined as constants
  in the rules. Adjust these values when corporate policy changes.

Inputs
* purchase_order: PurchaseOrder - the PO requiring approval - required
* requester: User - employee submitting the request - required
* urgency: enum [standard, urgent, emergency] - processing priority - optional, default: standard

Outputs
* approval_status: ApprovalStatus - current workflow state and next steps
* approval_chain: list of Approver - ordered list of approvers with their decisions
* notifications: list of Notification - all messages dispatched during the workflow

Types

PurchaseOrder {
  id: string, required
  amount: number, required
  currency: enum [CAD, USD], default: CAD
  vendor: string, required
  description: string, required
  department: enum [Engineering, Sales, Marketing, Operations, Finance, Legal], required
  justification: string, required
  budget_code: string, required
  created_at: datetime, required
}

User {
  id: string, required
  name: string, required
  email: string, required
  department: enum [Engineering, Sales, Marketing, Operations, Finance, Legal], required
  manager_id: string, optional
}

ApprovalStatus {
  state: enum [pending, in_review, approved, rejected, info_requested], required
  current_approver_id: string, optional
  last_updated: datetime, required
}

Approver {
  user_id: string, required
  role: string, required
  level: integer, required
  decision: enum [pending, approved, rejected, info_requested], required
  decided_at: datetime, optional
  comments: string, optional
}

Notification {
  id: string, required
  recipient_email: string, required
  type: enum [approval_request, approved, rejected, info_requested, escalation, reminder], required
  po_id: string, required
  sent_at: datetime, required
  message: string, required
}

Functions

FUNCTION get_department_head(department):
  lookup department in org_directory
  RETURNS user_id of the department head

FUNCTION calculate_timeout(urgency):
  IF urgency = "standard" THEN
    timeout = 48 hours
  ELSE IF urgency = "urgent" THEN
    timeout = 4 hours
  ELSE IF urgency = "emergency" THEN
    timeout = 2 hours
  RETURNS timeout

BEHAVIOR request_validation: Validate that a purchase order has all required fields
  and a valid budget code before entering the approval workflow

  RULE required_fields:
    purchase_order.vendor MUST NOT be empty
    AND purchase_order.description MUST NOT be empty
    AND purchase_order.justification MUST NOT be empty
    AND purchase_order.amount MUST be greater than zero

  RULE budget_code_valid:
    purchase_order.budget_code MUST match pattern "[A-Z]{2}-[0-9]{4}-[0-9]{3}"
    -- Format: two-letter department prefix, four-digit cost center, three-digit account code
    -- Example: EN-4200-310 = Engineering, cost center 4200, account 310

  RULE requester_has_manager:
    requester.manager_id MUST NOT be null
    -- Every PO needs at least one approver in the chain

  ERROR missing_required_fields:
    WHEN any of vendor, description, justification, or amount fails validation
    SEVERITY critical
    ACTION reject PO and return to requester
    MESSAGE "Purchase order is incomplete.
             All fields (vendor, description, justification, amount) are required."

  ERROR invalid_budget_code:
    WHEN purchase_order.budget_code does not match required pattern
    SEVERITY critical
    ACTION reject PO and return to requester
    MESSAGE "Budget code format invalid.
             Expected format: XX-0000-000 (e.g., EN-4200-310)."

  EXAMPLE valid_request:
    INPUT: {
      "purchase_order": {
        "id": "PO-2026-00847", "amount": 12500.00, "vendor": "Dell Technologies Canada",
        "description": "15x Dell Latitude 5550 laptops for Q2 new hires",
        "department": "Engineering", "justification": "Approved headcount expansion per Q2 hiring plan",
        "budget_code": "EN-4200-310"
      },
      "requester": { "id": "usr_391", "name": "Priya Sharma", "email": "priya.sharma@company.ca", "department": "Engineering", "manager_id": "usr_102" }
    }
    EXPECTED: { "validation": "passed", "next": "approval_routing" }

  EXAMPLE invalid_budget_code:
    INPUT: {
      "purchase_order": {
        "id": "PO-2026-00848", "amount": 3200.00, "vendor": "Staples Business Advantage",
        "description": "Office furniture for boardroom refresh",
        "department": "Operations", "justification": "Boardroom chairs past useful life",
        "budget_code": "OPS-42"
      },
      "requester": { "id": "usr_205", "name": "Marcus Chen", "email": "marcus.chen@company.ca", "department": "Operations", "manager_id": "usr_088" }
    }
    EXPECTED: { "validation": "failed", "error": "Budget code format invalid. Expected format: XX-0000-000 (e.g., EN-4200-310)." }
    NOTES: "OPS-42" does not match the required pattern [A-Z]{2}-[0-9]{4}-[0-9]{3}.


BEHAVIOR approval_routing: Determine the approval chain based on PO amount,
  then route for review. Emergency purchases bypass the standard chain.

  State: pending -> in_review -> approved | rejected | info_requested

  RULE emergency_override:
    WHEN urgency = "emergency"
         AND purchase_order.amount <= 10000
    THEN approval_chain = [get_department_head(purchase_order.department)]
         AND approval_status.state = "in_review"
    PRIORITY 1

  RULE amount_threshold_1:
    WHEN purchase_order.amount <= 5000
    THEN approval_chain = [requester.manager_id]
         AND approval_status.state = "in_review"
    PRIORITY 5

  RULE amount_threshold_2:
    WHEN purchase_order.amount > 5000
         AND purchase_order.amount <= 25000
    THEN approval_chain = [requester.manager_id,
                           get_department_head(purchase_order.department)]
         AND approval_status.state = "in_review"
    PRIORITY 6

  RULE amount_threshold_3:
    WHEN purchase_order.amount > 25000
         AND purchase_order.amount <= 100000
    THEN approval_chain = [requester.manager_id,
                           get_department_head(purchase_order.department),
                           "usr_finance_director"]
         AND approval_status.state = "in_review"
    PRIORITY 7

  RULE amount_threshold_4:
    WHEN purchase_order.amount > 100000
    THEN approval_chain = [requester.manager_id,
                           get_department_head(purchase_order.department),
                           "usr_finance_director", "usr_cfo"]
         AND approval_status.state = "in_review"
    PRIORITY 8

  RULE chain_progression:
    WHEN current approver decision = "approved" AND next approver exists in chain
    THEN advance current_approver_id to next approver in chain

  RULE final_approval:
    WHEN last approver in chain decision = "approved"
    THEN approval_status.state = "approved"

  RULE any_rejection:
    WHEN any approver decision = "rejected"
    THEN approval_status.state = "rejected"
    AND remaining approvers are not consulted

  ERROR missing_manager:
    WHEN requester.manager_id is null AND urgency != "emergency"
    SEVERITY critical
    ACTION halt workflow
    MESSAGE "Requester has no manager assigned. Cannot build approval chain."

  EXAMPLE small_purchase_single_approver:
    INPUT: {
      "purchase_order": { "id": "PO-2026-00851", "amount": 2800.00, "department": "Sales" },
      "requester": { "id": "usr_445", "name": "Dana Williams", "manager_id": "usr_220" },
      "urgency": "standard"
    }
    EXPECTED: {
      "approval_status": { "state": "in_review", "current_approver_id": "usr_220" },
      "approval_chain": [
        { "user_id": "usr_220", "role": "Direct Manager", "level": 1, "decision": "pending" }
      ]
    }
    NOTES: $2,800 <= $5,000 threshold. Single approver: direct manager only.

  EXAMPLE large_purchase_three_approvers:
    INPUT: {
      "purchase_order": { "id": "PO-2026-00852", "amount": 67000.00, "department": "Engineering" },
      "requester": { "id": "usr_391", "name": "Priya Sharma", "manager_id": "usr_102" },
      "urgency": "standard"
    }
    EXPECTED: {
      "approval_status": { "state": "in_review", "current_approver_id": "usr_102" },
      "approval_chain": [
        { "user_id": "usr_102", "role": "Direct Manager", "level": 1, "decision": "pending" },
        { "user_id": "usr_eng_head", "role": "Department Head", "level": 2, "decision": "pending" },
        { "user_id": "usr_finance_director", "role": "Finance Director", "level": 3, "decision": "pending" }
      ]
    }
    NOTES: $67,000 falls in the $25K-$100K band. Three approvers required, processed sequentially.

  EXAMPLE emergency_override_to_department_head:
    INPUT: {
      "purchase_order": { "id": "PO-2026-00853", "amount": 8500.00, "department": "Operations" },
      "requester": { "id": "usr_205", "name": "Marcus Chen", "manager_id": "usr_088" },
      "urgency": "emergency"
    }
    EXPECTED: {
      "approval_status": { "state": "in_review", "current_approver_id": "usr_ops_head" },
      "approval_chain": [
        { "user_id": "usr_ops_head", "role": "Department Head", "level": 1, "decision": "pending" }
      ]
    }
    NOTES: Emergency + amount <= $10K triggers PRIORITY 1 override.
           Bypasses manager, routes directly to department head. 2-hour timeout applies.


BEHAVIOR notification_dispatch: Send approval request notifications to the
  appropriate approvers. Standard urgency uses sequential notification; urgent
  uses parallel.

  RULE standard_sequential:
    WHEN urgency = "standard"
    THEN notify only the current approver in the chain
         AND do not notify subsequent approvers until the current one decides

  RULE urgent_parallel:
    WHEN urgency = "urgent"
    THEN notify all approvers in the chain simultaneously
         AND all approvers MUST approve for the PO to be approved
    PRIORITY 2

  RULE emergency_immediate:
    WHEN urgency = "emergency"
    THEN notify the single approver immediately
    AND include "EMERGENCY" prefix in message subject

  RULE notification_content:
    notification.message MUST include PO id, amount, vendor, and requester name

  ERROR notification_send_failure:
    WHEN notification delivery fails after 3 retry attempts
    SEVERITY warning
    ACTION log failure, continue workflow, alert system administrator
    MESSAGE "Failed to deliver notification to {recipient_email}
             after 3 attempts"

  EXAMPLE standard_sequential_notification:
    INPUT: {
      "po_id": "PO-2026-00851",
      "approval_chain": [{ "user_id": "usr_220", "level": 1 }],
      "urgency": "standard"
    }
    EXPECTED: {
      "notifications": [
        { "id": "ntf_90001", "recipient_email": "tom.park@company.ca", "type": "approval_request", "po_id": "PO-2026-00851", "sent_at": "2026-03-01T09:15:00-05:00", "message": "Approval required: PO-2026-00851 for $2,800.00 from Staples Business Advantage, submitted by Dana Williams." }
      ]
    }
    NOTES: Standard urgency -- only the current approver is notified. Next approver waits.

  EXAMPLE urgent_parallel_notification:
    INPUT: {
      "po_id": "PO-2026-00852",
      "approval_chain": [
        { "user_id": "usr_102", "level": 1 },
        { "user_id": "usr_eng_head", "level": 2 },
        { "user_id": "usr_finance_director", "level": 3 }
      ],
      "urgency": "urgent"
    }
    EXPECTED: {
      "notifications": [
        { "id": "ntf_90002", "recipient_email": "raj.kumar@company.ca", "type": "approval_request", "sent_at": "2026-03-01T09:15:00-05:00" },
        { "id": "ntf_90003", "recipient_email": "engineering.head@company.ca", "type": "approval_request", "sent_at": "2026-03-01T09:15:00-05:00" },
        { "id": "ntf_90004", "recipient_email": "finance.director@company.ca", "type": "approval_request", "sent_at": "2026-03-01T09:15:01-05:00" }
      ]
    }
    NOTES: Urgent — all three approvers notified simultaneously
           with identical URGENT-prefixed messages. All must approve.


BEHAVIOR timeout_escalation: Escalate to the next level of management when an
  approver does not respond within the timeout window defined by urgency level.

  RULE standard_timeout:
    WHEN urgency = "standard"
         AND current approver has not responded within 48 hours
    THEN send reminder notification to current approver
         AND if no response within additional 24 hours,
             escalate to current approver's manager

  RULE urgent_timeout:
    WHEN urgency = "urgent"
         AND any approver has not responded within 4 hours
    THEN escalate immediately to that approver's manager
         AND send escalation notification

  RULE emergency_timeout:
    WHEN urgency = "emergency"
         AND approver has not responded within 2 hours
    THEN escalate to CFO directly
         AND send escalation notification with "EMERGENCY ESCALATION" prefix

  ERROR approver_unavailable:
    WHEN escalation target (approver's manager) is also unavailable
         or has no manager_id
    SEVERITY critical
    ACTION escalate to CFO as final fallback, alert system administrator
    MESSAGE "Approval chain broken: no available escalation target
             for PO {po_id}"

  EXAMPLE standard_timeout_escalation:
    INPUT: {
      "po_id": "PO-2026-00851",
      "current_approver": { "user_id": "usr_220", "manager_id": "usr_sales_head" },
      "urgency": "standard",
      "time_since_notification": "49 hours"
    }
    EXPECTED: {
      "action": "reminder_sent",
      "notification": {
        "recipient_email": "tom.park@company.ca",
        "type": "reminder",
        "message": "Reminder: PO-2026-00851 for $2,800.00 is awaiting your approval. Please respond within 24 hours to avoid escalation."
      }
    }
    NOTES: 49 hours > 48-hour threshold. Reminder sent first. If no response by hour 72, escalation to usr_sales_head occurs.

  EXAMPLE urgent_escalation:
    INPUT: {
      "po_id": "PO-2026-00852",
      "current_approver": { "user_id": "usr_102", "manager_id": "usr_eng_head" },
      "urgency": "urgent",
      "time_since_notification": "5 hours"
    }
    EXPECTED: {
      "action": "escalated",
      "escalated_to": "usr_eng_head",
      "notification": {
        "recipient_email": "engineering.head@company.ca",
        "type": "escalation",
        "message": "ESCALATION: PO-2026-00852 for $67,000.00 has not been actioned by Raj Kumar within the 4-hour urgent window. Your approval is required."
      }
    }
    NOTES: 5 hours > 4-hour urgent threshold. Immediate escalation to approver's manager.

PRECEDENCE:
  1. emergency_override (from BEHAVIOR approval_routing)
  2. urgent_parallel (from BEHAVIOR notification_dispatch)
  3. amount_threshold_4 (from BEHAVIOR approval_routing)
  4. amount_threshold_3 (from BEHAVIOR approval_routing)
  5. amount_threshold_2 (from BEHAVIOR approval_routing)
  6. amount_threshold_1 (from BEHAVIOR approval_routing)

Constraints
* Approval decisions MUST be recorded with timestamp
  and persisted to survive system restarts
* Notifications MUST be dispatched within 60 seconds of a state change
* Timeout checks MUST run on a recurring schedule (every 15 minutes minimum)
* All monetary amounts MUST be displayed with two decimal places and currency code
* A user MUST NOT appear more than once in the same approval chain
* Emergency override MUST NOT apply to POs exceeding $10,000

Dependencies
* org_directory service for manager lookups and department head resolution
* budget_code registry for validation against pattern
  [A-Z]{2}-[0-9]{4}-[0-9]{3}
* notification service (email gateway) with retry capability
* workflow state persistence store (database or durable queue)
* scheduled job runner for timeout escalation checks

Changelog
* 2.1.0: 2026-03-01 - Migrated to SESF v2 behavior-centric format.
  Added PRECEDENCE block and explicit PRIORITY tags to approval_routing rules.
* 2.0.0: 2026-01-18 - Added emergency override rule for amounts under $10K.
  Added timeout escalation behavior.
* 1.1.0: 2025-11-22 - Added parallel notification for urgent requests
* 1.0.0: 2025-09-01 - Initial version with sequential approval only
```

---

## Example 4: Micro Tier -- Daily Sales Report Generator (PROCEDURE)

```
Daily Sales Report Generator

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Reporting | Status: active | Tier: micro

Purpose
Generate a daily summary of sales transactions and distribute it to the management team.

PROCEDURE generate_daily_report: Compile sales data and produce a summary report

  STEP gather_data: Collect the day's transactions
    Read all sales transactions for the current date from the database
    Start with total_revenue at 0 and transaction_count at 0

  STEP calculate_totals: Sum up the day's numbers
    For each transaction in the day's sales:
      Add transaction.amount to total_revenue
      Add 1 to transaction_count
    Calculate average_sale as total_revenue divided by transaction_count

  STEP generate_report: Build and distribute the report
    Write the summary to /reports/daily/YYYY-MM-DD.pdf
    Send the report to the management distribution list

  ERROR no_transactions:
    WHEN the day's sales list is empty
    SEVERITY warning
    ACTION generate an empty report noting "No transactions recorded"
    MESSAGE "No sales transactions found for {date}"

  ERROR database_unavailable:
    WHEN the database connection fails
    SEVERITY critical
    ACTION notify the on-call engineer and skip report generation
    MESSAGE "Cannot generate daily report: database connection failed"

  EXAMPLE typical_day:
    INPUT: { "date": "2026-03-01" }
    EXPECTED: { "total_revenue": 15420.50, "transaction_count": 47, "average_sale": 328.10, "report_path": "/reports/daily/2026-03-01.pdf" }
    NOTES: 47 transactions totaling $15,420.50. Average sale = $15,420.50 / 47 = $328.10.

  EXAMPLE no_sales:
    INPUT: { "date": "2026-01-01" }
    EXPECTED: { "total_revenue": 0, "transaction_count": 0, "report_path": "/reports/daily/2026-01-01.pdf", "warning": "No sales transactions found for 2026-01-01" }
    NOTES: New Year's Day -- store was closed. Empty report generated with warning.

Constraints
* Report generation SHOULD complete within 60 seconds
* All monetary amounts MUST be rounded to 2 decimal places
```

---

## Example 5: Standard Tier -- Customer Onboarding Workflow (mixed BEHAVIOR + PROCEDURE)

```
Customer Onboarding Workflow

Meta
* Version: 1.0.0
* Date: 2026-03-01
* Domain: Customer Success
* Status: active
* Tier: standard

Purpose
Validate incoming customer data, provision a new account, send a welcome package,
and schedule a follow-up call. Combines declarative validation rules with a
procedural onboarding flow.

Scope
* IN SCOPE: Customer data validation, account provisioning, welcome email dispatch,
  onboarding score calculation, follow-up scheduling
* OUT OF SCOPE: Billing setup, product configuration, CRM data migration,
  contract generation, identity verification

Inputs
* customer: Customer - the new customer to onboard - required
* plan: enum [starter, professional, enterprise] - selected subscription plan - required
* referral_code: string - promotional referral code - optional

Outputs
* result: OnboardingResult - summary of the onboarding outcome
* notifications: list of Notification - all messages sent during onboarding

Types

Customer {
  name: string, required
  email: string, required
  company: string, required
  phone: string, optional
  industry: enum [Technology, Healthcare, Finance, Retail, Manufacturing, Other], required
  employee_count: integer, required
}

OnboardingResult {
  account_id: string, required
  status: enum [active, pending_verification, failed], required
  onboarding_score: number, required
  welcome_sent: boolean, required
  followup_date: date, required
}

Notification {
  recipient: string, required
  type: enum [welcome_email, internal_alert, followup_reminder], required
  sent_at: datetime, required
  message: string, required
}

Account {
  id: string, required
  customer_name: string, required
  customer_email: string, required
  plan: enum [starter, professional, enterprise], required
  provisioned_at: datetime, required
  region: string, required
}

Functions

FUNCTION calculate_onboarding_score(customer, plan):
  Start with score at 50
  IF customer.phone is present THEN add 10 to score
  IF customer.employee_count is at least 50 THEN add 15 to score
  IF plan = "enterprise" THEN add 25 to score
  ELSE IF plan = "professional" THEN add 15 to score
  RETURNS score
  -- Score ranges: 50 (bare minimum) to 100 (enterprise with phone and 50+ employees)

FUNCTION determine_region(customer):
  IF customer.industry = "Healthcare" or customer.industry = "Finance"
    THEN region = "us-east-1"
    -- regulated industries default to US East for compliance
  ELSE region = "us-west-2"
  RETURNS region

FUNCTION calculate_followup_date(plan):
  IF plan = "enterprise" THEN followup = 2 business days from today
  ELSE IF plan = "professional" THEN followup = 5 business days from today
  ELSE followup = 10 business days from today
  RETURNS followup


BEHAVIOR validate_customer_data: Ensure the customer record is complete
  and well-formed before onboarding begins

  RULE email_format:
    customer.email MUST contain exactly one "@" character
    AND the portion after "@" MUST contain at least one "." character

  RULE company_required:
    customer.company MUST NOT be empty

  RULE employee_count_positive:
    customer.employee_count MUST be greater than zero

  RULE enterprise_needs_phone:
    WHEN plan = "enterprise"
    THEN customer.phone MUST be present
    -- enterprise customers require a phone number for dedicated support

  ERROR invalid_email:
    WHEN customer.email fails email_format
    SEVERITY critical
    ACTION reject onboarding and return the error to the submitter
    MESSAGE "Invalid email address: {customer.email}"

  ERROR missing_company:
    WHEN customer.company is empty
    SEVERITY critical
    ACTION reject onboarding
    MESSAGE "Company name is required for all customers"

  ERROR enterprise_missing_phone:
    WHEN plan = "enterprise" and customer.phone is missing
    SEVERITY critical
    ACTION reject onboarding
    MESSAGE "Enterprise customers must provide a phone number"

  EXAMPLE valid_professional_customer:
    INPUT: {
      "customer": { "name": "Alicia Torres", "email": "alicia@brightpath.io", "company": "Brightpath Solutions", "phone": "+1-416-555-0199", "industry": "Technology", "employee_count": 120 },
      "plan": "professional"
    }
    EXPECTED: { "validation": "passed" }
    NOTES: All fields present and valid. Phone is optional for professional plan but provided.

  EXAMPLE enterprise_missing_phone:
    INPUT: {
      "customer": { "name": "James Whitfield", "email": "j.whitfield@meridian.com", "company": "Meridian Health Group", "industry": "Healthcare", "employee_count": 500 },
      "plan": "enterprise"
    }
    EXPECTED: { "validation": "failed", "error": "Enterprise customers must provide a phone number" }
    NOTES: Enterprise plan requires phone. Onboarding cannot proceed.


PROCEDURE onboard_customer: Walk through each onboarding step in order,
  from account creation to follow-up scheduling

  STEP validate: Run the validation rules first
    Validate the customer data using the validate_customer_data behavior
    Stop processing if validation fails

  STEP provision_account: Create the customer's account
    Calculate the region using determine_region(customer)
    Create a new account with the customer's name, email, selected plan, and region
    Record the account_id for the remaining steps

  STEP score: Assess onboarding completeness
    Calculate onboarding_score using calculate_onboarding_score(customer, plan)

  STEP send_welcome: Dispatch the welcome package
    Send a welcome email to the customer using send_welcome_package
    Record that welcome_sent is true
    If the onboarding_score is at least 75:
      Include a personalized note from the account manager in the welcome email

  STEP schedule_followup: Set up the follow-up call
    Calculate the followup_date using calculate_followup_date(plan)
    Send a follow-up reminder to the assigned account manager
    Send an internal alert to the customer success team with the onboarding summary

  ERROR account_provisioning_failure:
    WHEN account creation fails
    SEVERITY critical
    ACTION notify the infrastructure team and mark onboarding as failed
    MESSAGE "Account provisioning failed for {customer.email}. Infrastructure team notified."

  ERROR welcome_email_failure:
    WHEN the welcome email cannot be delivered after 3 attempts
    SEVERITY warning
    ACTION log the failure, continue onboarding, and flag for manual follow-up
    MESSAGE "Welcome email delivery failed for {customer.email}. Manual follow-up required."

  EXAMPLE successful_professional_onboarding:
    INPUT: {
      "customer": { "name": "Alicia Torres", "email": "alicia@brightpath.io", "company": "Brightpath Solutions", "phone": "+1-416-555-0199", "industry": "Technology", "employee_count": 120 },
      "plan": "professional"
    }
    EXPECTED: {
      "result": {
        "account_id": "acct_20260301_00142",
        "status": "active",
        "onboarding_score": 90,
        "welcome_sent": true,
        "followup_date": "2026-03-08"
      },
      "notifications": [
        { "recipient": "alicia@brightpath.io", "type": "welcome_email" },
        { "recipient": "csm-team@company.ca", "type": "internal_alert" },
        { "recipient": "account-manager@company.ca", "type": "followup_reminder" }
      ]
    }
    NOTES: Score = 50 base + 10 (phone) + 15 (120 employees >= 50) + 15 (professional) = 90.
           Score >= 75 so welcome email includes personalized note.
           Professional plan follow-up = 5 business days from Mar 1 = Mar 8.
           Technology industry -> us-west-2 region.

  EXAMPLE starter_minimal_customer:
    INPUT: {
      "customer": { "name": "Sam Nguyen", "email": "sam@tinycorp.io", "company": "TinyCorp", "industry": "Retail", "employee_count": 3 },
      "plan": "starter"
    }
    EXPECTED: {
      "result": {
        "account_id": "acct_20260301_00143",
        "status": "active",
        "onboarding_score": 50,
        "welcome_sent": true,
        "followup_date": "2026-03-15"
      },
      "notifications": [
        { "recipient": "sam@tinycorp.io", "type": "welcome_email" },
        { "recipient": "csm-team@company.ca", "type": "internal_alert" },
        { "recipient": "account-manager@company.ca", "type": "followup_reminder" }
      ]
    }
    NOTES: Score = 50 base only (no phone, 3 employees < 50, starter plan adds 0).
           Score < 75 so no personalized note in welcome email.
           Starter plan follow-up = 10 business days from Mar 1 = Mar 15.
           Retail industry -> us-west-2 region.


ACTION send_welcome_package(customer, account, onboarding_score):
  Generate the welcome email from the onboarding template
  If onboarding_score is at least 75:
    Append a personalized note from the account manager
  Send the email to customer.email
  Log: "Welcome package sent to {customer.email} for account {account.id}"
  RETURNS the delivery confirmation

Constraints
* Account provisioning MUST complete within 30 seconds
* Welcome email MUST be sent within 5 minutes of account creation
* Follow-up date MUST be a business day (skip weekends and statutory holidays)
* Onboarding score MUST be between 0 and 100

Dependencies
* Account provisioning service (internal API)
* Email delivery service with retry capability
* Calendar service for business day calculations
* Customer success team notification channel
```

---

## Example 6: Complex Tier -- Data Pipeline Processor (PROCEDURE-heavy)

```
Data Pipeline Processor

Meta
* Version: 3.0.0
* Date: 2026-03-01
* Domain: Data Engineering
* Status: active
* Tier: complex

Purpose
Ingest data files from an upload directory, validate their structure, transform
the records, and load them into the data warehouse. Track each file through its
lifecycle (queued, validating, transforming, loading, completed, failed) with
retry logic and error recovery.

Scope
* IN SCOPE: File ingestion, schema validation, data transformation, warehouse
  loading, state tracking, retry logic, error recovery, pipeline monitoring
* OUT OF SCOPE: File upload mechanism, warehouse schema migrations, downstream
  analytics, data access permissions, visualization

Audience
* AI agents: Process files by running ingest_file for each file in the upload
  directory. Respect PRECEDENCE -- quarantine checks run before any processing.
* Human operators: Start with the run_pipeline procedure for the end-to-end flow.
  Review the state lifecycle (queued -> validating -> transforming -> loading ->
  completed) to understand where a file is at any time.
* Data engineers: Transformation rules are in transform_records. Add new
  transformations as additional steps within that procedure.

Inputs
* upload_directory: string - path to the directory where new files arrive - required
* warehouse_connection: string - connection string for the target warehouse - required
* max_retries: integer - maximum retry attempts per file - optional, default: 3
* batch_size: integer - number of records to process at a time - optional, default: 500

Outputs
* pipeline_result: PipelineResult - summary of the entire pipeline run
* file_results: list of FileResult - per-file outcome details
* audit_log: list of AuditEntry - chronological record of all pipeline actions

Types

PipelineResult {
  run_id: string, required
  started_at: datetime, required
  completed_at: datetime, optional
  files_processed: integer, required
  files_succeeded: integer, required
  files_failed: integer, required
  total_records_loaded: integer, required
  status: enum [completed, completed_with_errors, failed], required
}

FileResult {
  file_name: string, required
  file_size: integer, required
  state: enum [queued, validating, transforming, loading, completed, failed, quarantined], required
  records_in: integer, optional
  records_out: integer, optional
  errors: list of string, optional
  retry_count: integer, required
  started_at: datetime, optional
  completed_at: datetime, optional
}

DataFile {
  name: string, required
  path: string, required
  size: integer, required
  format: enum [csv, json, parquet], required
  uploaded_at: datetime, required
}

Record {
  id: string, required
  fields: list of Field, required
  source_file: string, required
  row_number: integer, required
}

Field {
  name: string, required
  value: string, optional
  type: enum [string, number, date, boolean], required
}

Schema {
  name: string, required
  columns: list of ColumnDef, required
  version: string, required
}

ColumnDef {
  name: string, required
  type: enum [string, number, date, boolean], required
  required: boolean, required
  pattern: string, optional
}

AuditEntry {
  timestamp: datetime, required
  file_name: string, required
  action: string, required
  detail: string, optional
  severity: enum [info, warning, error], required
}

Functions

FUNCTION detect_format(file_name):
  IF file_name ends with ".csv" THEN format = "csv"
  ELSE IF file_name ends with ".json" THEN format = "json"
  ELSE IF file_name ends with ".parquet" THEN format = "parquet"
  ELSE format = "unknown"
  RETURNS format

FUNCTION select_schema(format, header_row):
  Look up the schema registry for a schema matching the format and header_row columns
  IF a matching schema is found THEN RETURNS the schema
  ELSE RETURNS nothing

FUNCTION calculate_batch_count(total_records, batch_size):
  Calculate count as total_records divided by batch_size, rounded up to the nearest whole number
  RETURNS count

FUNCTION summarize_run(file_results):
  Calculate files_succeeded as the number of items in file_results where state is "completed"
  Calculate files_failed as the number of items in file_results where state is "failed" or state is "quarantined"
  Calculate total_records_loaded as the sum of records_out across file_results where state is "completed"
  IF files_failed is greater than 0 and files_succeeded is greater than 0
    THEN status = "completed_with_errors"
  ELSE IF files_failed equals the number of items in file_results
    THEN status = "failed"
  ELSE status = "completed"
  RETURNS { files_processed, files_succeeded, files_failed, total_records_loaded, status }


BEHAVIOR quarantine_check: Determine whether a file should be quarantined
  before any processing begins

  RULE file_too_large:
    WHEN file.size exceeds 500000000
    THEN quarantine the file
    -- 500 MB limit protects against runaway resource consumption
    PRIORITY 1

  RULE unsupported_format:
    WHEN detect_format(file.name) equals "unknown"
    THEN quarantine the file
    PRIORITY 2

  RULE duplicate_file:
    WHEN a record exists in the audit log where file_name equals file.name
         and action equals "completed" and the entry is from the last 24 hours
    THEN quarantine the file
    -- prevent reprocessing of recently completed files
    PRIORITY 3

  ERROR quarantined_file:
    WHEN any quarantine rule matches
    SEVERITY warning
    ACTION move the file to the quarantine directory, log the reason, notify the data team
    MESSAGE "File {file.name} quarantined: {reason}"

  EXAMPLE oversized_file:
    INPUT: { "file": { "name": "huge_export.csv", "size": 750000000 } }
    EXPECTED: { "state": "quarantined", "reason": "File size 750000000 exceeds 500 MB limit" }
    NOTES: 750 MB file triggers file_too_large rule. Moved to quarantine without further processing.

  EXAMPLE unknown_format:
    INPUT: { "file": { "name": "data.xlsx", "size": 1024000 } }
    EXPECTED: { "state": "quarantined", "reason": "Unsupported file format: unknown" }
    NOTES: .xlsx is not in the supported format list. File quarantined.

  EXAMPLE duplicate_recent:
    INPUT: { "file": { "name": "daily_sales.csv", "size": 2048000 }, "audit_log": [{ "file_name": "daily_sales.csv", "action": "completed", "timestamp": "2026-03-01T06:00:00Z" }] }
    EXPECTED: { "state": "quarantined", "reason": "Duplicate of file completed within last 24 hours" }
    NOTES: Same file name was successfully processed 4 hours ago. Quarantined to prevent double-load.


PROCEDURE validate_file: Check that a file's structure matches the expected
  schema before transformation

  STEP detect: Identify the file format
    Determine the format using detect_format(file.name)
    Move the file from "queued" to "validating"
    Log an audit entry: "Validation started for {file.name}"

  STEP read_header: Read the file header to identify columns
    Read the first row of the file to extract the column names
    If the file is empty:
      Stop processing and raise empty_file error

  STEP match_schema: Find the appropriate schema
    Look up the schema using select_schema(format, header_row)
    If no schema is found:
      Stop processing and raise schema_not_found error

  STEP validate_columns: Verify each column against the schema
    For each column defined in the schema:
      If the column is marked as required and is missing from the file header:
        Add "Missing required column: {column.name}" to the error list
      If the column is present and has a pattern defined:
        Check that at least 95% of values in that column match the pattern
        If fewer than 95% match:
          Add "Column {column.name}: {match_percentage}% of values match expected pattern (minimum 95%)" to the error list
    If the error list is not empty:
      Stop processing and raise validation_failed error

  STEP record_stats: Capture file statistics
    Count the total number of records in the file (excluding the header)
    Record records_in on the file result
    Log an audit entry: "Validation passed for {file.name}: {records_in} records found"

  ERROR empty_file:
    WHEN the file contains no data rows
    SEVERITY warning
    ACTION move the file from "validating" to "failed", log the issue
    MESSAGE "File {file.name} is empty -- no records to process"

  ERROR schema_not_found:
    WHEN no matching schema exists for the file's format and column structure
    SEVERITY critical
    ACTION move the file from "validating" to "failed", notify the data engineering team
    MESSAGE "No schema found for {file.name} with format {format}. Manual schema registration required."

  ERROR validation_failed:
    WHEN one or more columns fail validation
    SEVERITY critical
    ACTION move the file from "validating" to "failed", attach the error list to the file result
    MESSAGE "Validation failed for {file.name}: {error_count} column issues found"

  EXAMPLE valid_csv_file:
    INPUT: {
      "file": { "name": "orders_20260301.csv", "path": "/uploads/orders_20260301.csv", "format": "csv" },
      "header_row": ["order_id", "customer_id", "amount", "order_date", "status"]
    }
    EXPECTED: {
      "state": "validating",
      "records_in": 1250,
      "audit_entry": "Validation passed for orders_20260301.csv: 1250 records found"
    }
    NOTES: All 5 columns match the orders schema. 1250 data rows found.

  EXAMPLE missing_required_column:
    INPUT: {
      "file": { "name": "orders_broken.csv", "path": "/uploads/orders_broken.csv", "format": "csv" },
      "header_row": ["order_id", "amount", "order_date"]
    }
    EXPECTED: {
      "state": "failed",
      "errors": ["Missing required column: customer_id", "Missing required column: status"]
    }
    NOTES: customer_id and status columns are required by the orders schema but missing from the file.


PROCEDURE transform_records: Apply data transformations to validated records
  before loading them into the warehouse

  STEP prepare: Set up transformation context
    Move the file from "validating" to "transforming"
    Calculate the number of batches using calculate_batch_count(records_in, batch_size)
    Start with records_out at 0 and current_batch at 1
    Log an audit entry: "Transformation started for {file.name}: {batch_count} batches"

  STEP process_batches: Transform records in batches
    While current_batch is at most batch_count:
      Read the next batch of records from the file
      For each record in the batch:
        Trim whitespace from all string fields
        Convert date fields to ISO 8601 format (YYYY-MM-DD)
        Convert all number fields to standard decimal notation
        If any required field is missing or null:
          Skip this record and add a warning to the audit log:
            "Skipped record {record.row_number}: missing required field {field.name}"
        Otherwise:
          Add 1 to records_out
      Add 1 to current_batch

  STEP deduplicate: Remove duplicate records
    Sort the transformed records by record.id
    Group the records by record.id
    For each group with more than one record:
      Keep only the first record in the group
      Subtract the number of removed duplicates from records_out
      Log an audit entry: "Removed {duplicate_count} duplicate records from {file.name}"

  STEP finalize: Record transformation outcome
    Log an audit entry: "Transformation complete for {file.name}: {records_out} of {records_in} records ready to load"

  ERROR batch_read_failure:
    WHEN a batch cannot be read from the file
    SEVERITY critical
    ACTION move the file from "transforming" to "failed", log the error with the batch number
    MESSAGE "Failed to read batch {current_batch} of {batch_count} from {file.name}"

  EXAMPLE successful_transformation:
    INPUT: {
      "file": { "name": "orders_20260301.csv", "records_in": 1250 },
      "batch_size": 500
    }
    EXPECTED: {
      "state": "transforming",
      "batch_count": 3,
      "records_out": 1247,
      "audit_entries": [
        "Transformation started for orders_20260301.csv: 3 batches",
        "Skipped record 412: missing required field customer_id",
        "Skipped record 889: missing required field amount",
        "Removed 1 duplicate records from orders_20260301.csv",
        "Transformation complete for orders_20260301.csv: 1247 of 1250 records ready to load"
      ]
    }
    NOTES: 3 batches (500 + 500 + 250). Two records skipped for missing fields,
           one duplicate removed. 1250 - 2 skipped - 1 duplicate = 1247 records out.

  EXAMPLE all_records_skipped:
    INPUT: {
      "file": { "name": "corrupt_data.json", "records_in": 15 },
      "batch_size": 500
    }
    EXPECTED: {
      "state": "transforming",
      "batch_count": 1,
      "records_out": 0,
      "audit_entries": [
        "Transformation started for corrupt_data.json: 1 batch",
        "Skipped record 1: missing required field id",
        "... (all 15 records skipped)",
        "Transformation complete for corrupt_data.json: 0 of 15 records ready to load"
      ]
    }
    NOTES: Every record was missing required fields. records_out = 0.
           The load step will handle the zero-record case.


PROCEDURE load_to_warehouse: Load transformed records into the data warehouse
  with retry logic for transient failures

  STEP check_records: Verify there are records to load
    If records_out equals 0:
      Log an audit entry: "No records to load for {file.name} -- skipping warehouse load"
      Move the file from "transforming" to "completed"
      Return the result
      -- Zero records is not an error -- transformation may have filtered everything out

  STEP connect: Establish the warehouse connection
    Move the file from "transforming" to "loading"
    Attempt to connect to the warehouse using warehouse_connection:
      If it fails:
        Log the error and raise connection_failed error

  STEP load_batches: Insert records in batches
    Calculate the number of load batches using calculate_batch_count(records_out, batch_size)
    Start with loaded_count at 0 and current_batch at 1
    While current_batch is at most load_batch_count:
      Take the next batch of transformed records
      Attempt to insert the batch into the warehouse:
        If it succeeds:
          Add the number of records in the batch to loaded_count
        If it fails:
          Attempt the insert again up to max_retries times
          If all retries fail:
            Log the error with the batch number and raise load_failed error
      Add 1 to current_batch

  STEP verify: Confirm the load
    Query the warehouse to count the records just inserted for this file
    If the warehouse count does not equal loaded_count:
      Log a warning: "Record count mismatch: expected {loaded_count}, found {warehouse_count}"
    Move the file from "loading" to "completed"
    Log an audit entry: "Load complete for {file.name}: {loaded_count} records inserted"

  ERROR connection_failed:
    WHEN the warehouse connection cannot be established after 3 attempts
    SEVERITY critical
    ACTION move the file from "loading" to "failed", notify the infrastructure team
    MESSAGE "Cannot connect to warehouse: {connection_error}. File {file.name} load aborted."

  ERROR load_failed:
    WHEN a batch insert fails after max_retries attempts
    SEVERITY critical
    ACTION move the file from "loading" to "failed", record which batch failed,
           roll back any partially inserted records for this file
    MESSAGE "Batch {current_batch} failed after {max_retries} retries for {file.name}. Partial load rolled back."

  EXAMPLE successful_load:
    INPUT: {
      "file": { "name": "orders_20260301.csv", "records_out": 1247 },
      "batch_size": 500,
      "max_retries": 3
    }
    EXPECTED: {
      "state": "completed",
      "loaded_count": 1247,
      "audit_entry": "Load complete for orders_20260301.csv: 1247 records inserted"
    }
    NOTES: 3 load batches (500 + 500 + 247). All inserted successfully on first attempt.

  EXAMPLE retry_then_success:
    INPUT: {
      "file": { "name": "products_20260301.json", "records_out": 800 },
      "batch_size": 500,
      "max_retries": 3
    }
    EXPECTED: {
      "state": "completed",
      "loaded_count": 800,
      "retry_count": 1,
      "audit_entries": [
        "Batch 1: insert failed (timeout), retrying (attempt 1 of 3)",
        "Batch 1: insert succeeded on retry",
        "Load complete for products_20260301.json: 800 records inserted"
      ]
    }
    NOTES: First batch failed once with a timeout, succeeded on first retry.
           Second batch (300 records) succeeded on first attempt.

  EXAMPLE permanent_failure:
    INPUT: {
      "file": { "name": "events_20260301.parquet", "records_out": 5000 },
      "batch_size": 500,
      "max_retries": 3
    }
    EXPECTED: {
      "state": "failed",
      "loaded_count": 0,
      "retry_count": 3,
      "error": "Batch 1 failed after 3 retries for events_20260301.parquet. Partial load rolled back."
    }
    NOTES: First batch failed on all 3 retry attempts. No records loaded.
           Any partially inserted records are rolled back.


PROCEDURE run_pipeline: Orchestrate the full ingestion pipeline from file
  discovery through warehouse loading

  STEP discover: Find files waiting to be processed
    Read the list of files in the upload_directory
    Keep only the files that have not been processed before
      -- check the audit log for previous completions
    Sort the files by uploaded_at, oldest first
    If no files are found:
      Log an audit entry: "Pipeline run: no new files found"
      Return an empty result

  STEP initialize: Set up the pipeline run
    Generate a new run_id
    Record the started_at timestamp
    Start with files_processed at 0

  STEP process_files: Run each file through the pipeline
    For each file in the discovery list:
      Add 1 to files_processed
      Run quarantine_check on the file
      If the file is quarantined:
        Record the file result with state "quarantined" and skip to the next file
      Run validate_file on the file
      If validation fails:
        Record the file result with state "failed" and skip to the next file
      Run transform_records on the file
      If transformation produces zero records:
        Record the file result with state "completed" and skip to the next file
      Run load_to_warehouse on the file
      Record the file result

  STEP summarize: Produce the pipeline summary
    Calculate the pipeline result using summarize_run(file_results)
    Record the completed_at timestamp
    Log an audit entry: "Pipeline run {run_id} complete: {files_succeeded} succeeded, {files_failed} failed, {total_records_loaded} records loaded"

  ERROR pipeline_interrupted:
    WHEN an unexpected error halts the pipeline before all files are processed
    SEVERITY critical
    ACTION record partial results, log the interruption point, notify the data engineering team
    MESSAGE "Pipeline run {run_id} interrupted after processing {files_processed} of {total_files} files"

  EXAMPLE full_pipeline_run:
    INPUT: {
      "upload_directory": "/data/uploads",
      "warehouse_connection": "warehouse://prod-cluster:5439/analytics",
      "max_retries": 3,
      "batch_size": 500,
      "files_in_directory": [
        { "name": "orders_20260301.csv", "size": 2048000, "uploaded_at": "2026-03-01T01:00:00Z" },
        { "name": "huge_export.csv", "size": 750000000, "uploaded_at": "2026-03-01T01:05:00Z" },
        { "name": "products_20260301.json", "size": 512000, "uploaded_at": "2026-03-01T01:10:00Z" }
      ]
    }
    EXPECTED: {
      "pipeline_result": {
        "run_id": "run_20260301_001",
        "status": "completed_with_errors",
        "files_processed": 3,
        "files_succeeded": 2,
        "files_failed": 1,
        "total_records_loaded": 2047
      },
      "file_results": [
        { "file_name": "orders_20260301.csv", "state": "completed", "records_in": 1250, "records_out": 1247 },
        { "file_name": "huge_export.csv", "state": "quarantined", "errors": ["File size 750000000 exceeds 500 MB limit"] },
        { "file_name": "products_20260301.json", "state": "completed", "records_in": 820, "records_out": 800 }
      ]
    }
    NOTES: Three files discovered. orders_20260301.csv processed successfully (1247 records).
           huge_export.csv quarantined for exceeding 500 MB. products_20260301.json processed
           successfully (800 records after transformation). Total loaded = 1247 + 800 = 2047.

  EXAMPLE empty_upload_directory:
    INPUT: {
      "upload_directory": "/data/uploads",
      "warehouse_connection": "warehouse://prod-cluster:5439/analytics",
      "files_in_directory": []
    }
    EXPECTED: {
      "pipeline_result": {
        "status": "completed",
        "files_processed": 0,
        "files_succeeded": 0,
        "files_failed": 0,
        "total_records_loaded": 0
      },
      "audit_entry": "Pipeline run: no new files found"
    }
    NOTES: No files to process. Pipeline exits early with an empty result.

PRECEDENCE:
  1. file_too_large (from BEHAVIOR quarantine_check)
  2. unsupported_format (from BEHAVIOR quarantine_check)
  3. duplicate_file (from BEHAVIOR quarantine_check)
  4. validate_file (PROCEDURE -- runs after quarantine clears)
  5. transform_records (PROCEDURE -- runs after validation passes)
  6. load_to_warehouse (PROCEDURE -- runs after transformation completes)
  -- Quarantine checks always run first. If a file is quarantined,
  -- no validation, transformation, or loading occurs.

Constraints
* File state transitions MUST follow the lifecycle: queued -> validating ->
  transforming -> loading -> completed (or failed/quarantined at any point)
* A file MUST NOT move backward in the state lifecycle
* Batch size MUST be between 1 and 10000
* All timestamps MUST use ISO 8601 format in UTC
* Partial loads MUST be rolled back on failure -- no half-loaded files
* The audit log MUST record every state transition for every file
* Pipeline runs MUST be idempotent -- rerunning after a failure skips already completed files
* Warehouse inserts MUST use transactions to ensure atomicity per batch

Dependencies
* File system access to the upload and quarantine directories
* Schema registry service for column validation rules
* Data warehouse with transactional insert support
* Audit log persistence store
* Notification service for team alerts
* Scheduling service for recurring pipeline runs

Changelog
* 3.0.0: 2026-03-01 - Rewrote in SESF v3 procedural format. Added PROCEDURE
  blocks for validate_file, transform_records, load_to_warehouse, and
  run_pipeline. Added quarantine_check behavior with PRECEDENCE.
* 2.0.0: 2025-12-15 - Added retry logic and batch processing. Introduced
  state lifecycle tracking.
* 1.1.0: 2025-10-01 - Added parquet format support and deduplication step
* 1.0.0: 2025-08-01 - Initial version with CSV-only support
```

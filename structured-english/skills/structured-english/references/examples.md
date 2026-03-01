# SESF v2 Complete Examples

Three complete specifications demonstrating each SESF v2 tier. Each is a working spec with concrete data, suitable as a reference when writing new specifications.

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

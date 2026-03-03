# SESF v4 Complete Examples

Six complete specifications demonstrating every SESF v4 tier and style. Examples 1-3 are declarative (BEHAVIOR-centric), showing rules about what must be true. Examples 4-6 are procedural (PROCEDURE-centric), showing step-by-step processes. Together they cover the full range of SESF v4. Each is a working spec with concrete data, suitable as a reference when writing new specifications.

---

## Example 1: Micro Tier -- Email Address Validator

```
Email Address Validator

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Input Validation | Status: active | Tier: micro

Purpose
Validate that a given string is a structurally valid email address before passing it to downstream systems.

Behaviors

BEHAVIOR validate_email: Check that an input string conforms to basic email address structure

  RULE contains_at_sign:
    input MUST contain exactly one "@" character

  RULE has_domain:
    WHEN input contains "@"
    THEN the portion after "@" MUST contain at least one "." character
         AND the portion after "@" MUST be at least 3 characters long

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | invalid_email | input fails contains_at_sign OR has_domain | critical | reject input | "Invalid email address: does not meet structural requirements" |

  EXAMPLES:
    valid_email: input="reggie.chan@tenebrus.ca" → { "valid": true }
    missing_at_sign: input="reggie.chan.tenebrus.ca" → rejected with "Invalid email address: does not meet structural requirements"

Constraints
* Validation is structural only — does not verify that the domain exists or accepts mail
```

---

## Example 2: Standard Tier -- Commercial Lease Abstraction

```
---
name: lease-abstraction
description: "Extract structured data from commercial lease PDFs"
---

# Commercial Lease Abstraction

Meta
* Version: 2.1.0
* Date: 2026-03-01
* Domain: Real Estate / Document Processing
* Status: active
* Tier: standard

Notation
* $ — references a variable or config value (e.g., $config.min_confidence)
* @ — marks a structured block (@config for parameters, @route for decision tables)
* → — means "produces" (in steps), "routes to" (in tables), or "yields" (in examples)
* MUST/SHOULD/MAY/CAN — requirement strength keywords

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

@config
  min_confidence: 0.5
  required_fields: [parties.landlord, parties.tenant, premises.address, premises.sqft, term.commencement, term.expiration, rent.base_amount]
  sqft_range:
    min: 100
    max: 2000000
  max_term_months: 300
  output_format: json
  currency_default: CAD

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
  currency: enum [CAD, USD], default: $config.currency_default
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

Behaviors

BEHAVIOR party_extraction: Identify landlord and tenant entities from the lease document

  RULE landlord_required:
    parties.landlord MUST be present
    AND parties.landlord.name MUST NOT be empty

  RULE tenant_required:
    parties.tenant MUST be present
    AND parties.tenant.name MUST NOT be empty

  @route entity_type_classification [first_match_wins]
    party name contains "Inc", "Corp", "Ltd", or "Limited"  → set entity_type to "Corporation"
    party name contains "LLC" or "L.L.C."                    → set entity_type to "LLC"
    party name contains "LP" or "L.P." or "Partnership"      → set entity_type to "Partnership"
    *                                                         → set entity_type to "Individual"

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | missing_landlord | parties.landlord is null or parties.landlord.name is empty | critical | halt extraction | "Could not identify landlord in lease document" |
  | missing_tenant | parties.tenant is null or parties.tenant.name is empty | critical | halt extraction | "Could not identify tenant in lease document" |

  EXAMPLE successful_party_extraction:
    INPUT: { "lease_pdf": "456_queen_west_lease.pdf" }
    EXPECTED: {
      "parties": {
        "landlord": { "name": "Brookfield Asset Management Ltd.", "entity_type": "Corporation", "address": "181 Bay Street, Suite 300, Toronto, ON M5J 2T3" },
        "tenant": { "name": "Northern Lights Coffee Inc.", "entity_type": "Corporation", "address": "456 Queen Street West, Toronto, ON M5V 2A8" }
      }
    }
    NOTES: Both parties extracted with entity_type inferred from "Ltd." and "Inc." via @route entity_type_classification.

  EXAMPLES:
    missing_landlord_case: lease_pdf="damaged_scan_lease.pdf" → rejected with "Could not identify landlord in lease document"


BEHAVIOR premises_extraction: Extract physical property details from the lease

  RULE sqft_positive:
    premises.sqft MUST be greater than zero

  RULE address_required:
    premises.address MUST NOT be empty
         AND premises.city MUST NOT be empty

  RULE sqft_reasonableness:
    premises.sqft SHOULD be between $config.sqft_range.min and $config.sqft_range.max
    -- flag outliers for review

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | missing_sqft | premises.sqft is null or premises.sqft = 0 | warning | continue with flag | "Square footage not found -- may require manual review" |

  EXAMPLE complete_premises:
    INPUT: { "lease_pdf": "456_queen_west_lease.pdf" }
    EXPECTED: {
      "premises": { "address": "456 Queen Street West, Unit 2B", "city": "Toronto", "province_or_state": "ON", "postal_code": "M5V 2A8", "sqft": 3200, "unit": "2B", "permitted_use": "Retail food service and ancillary uses" }
    }

  EXAMPLES:
    missing_sqft_case: lease_pdf="older_format_lease.pdf" → premises extracted with sqft=null and warning "Square footage not found -- may require manual review"


BEHAVIOR term_extraction: Extract and validate lease commencement and expiration dates

  RULE expiration_after_commencement:
    term.expiration MUST be after term.commencement

  RULE months_calculation:
    term.months MUST equal months_between(term.commencement, term.expiration)

  RULE term_reasonableness:
    term.months SHOULD be between 1 and $config.max_term_months
    -- flag unusual terms for review

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | date_parse_failure | commencement or expiration date cannot be parsed from document text | critical | halt extraction | "Could not parse lease term dates from document" |

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

  EXAMPLES:
    invalid_dates_case: lease_pdf="corrupted_dates_lease.pdf" → rejected with "Could not parse lease term dates from document"


BEHAVIOR rent_extraction: Extract base rent, payment period, and escalation schedule

  RULE positive_rent:
    rent.base_amount MUST be greater than zero

  RULE escalation_chronology:
    WHEN rent.escalations is present
    THEN EACH escalation.effective_date MUST be after term.commencement
    AND escalation dates MUST be in ascending order

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | missing_rent | rent.base_amount is null or rent.base_amount <= 0 | critical | halt extraction | "Could not extract base rent amount from document" |

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

  EXAMPLES:
    monthly_rent_no_escalations: lease_pdf="simple_retail_lease.pdf" → rent extracted with base_amount=4500.00, period="monthly", escalations=[]


BEHAVIOR confidence_scoring: Compute overall extraction confidence based on field completeness

  RULE confidence_calculation:
    confidence MUST equal confidence_score(lease_data, $config.required_fields)

  RULE confidence_range:
    confidence MUST be between 0.0 and 1.0

  EXAMPLES:
    high_confidence: all 7 required fields extracted → { "confidence": 1.0 }
    low_confidence: only 3 of 7 required fields found → { "confidence": 0.43 }

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
---
name: po-approval
description: "Route purchase orders through approval chains based on amount thresholds and urgency"
---

# Purchase Order Approval Workflow

Meta
* Version: 3.0.0
* Date: 2026-03-01
* Domain: Finance / Procurement
* Status: active
* Tier: complex

Notation
* $ — references a variable or config value (e.g., $config.thresholds.tier_1)
* @ — marks a structured block (@config for parameters, @route for decision tables)
* → — means "produces" (in steps), "routes to" (in tables), or "yields" (in examples)
* MUST/SHOULD/MAY/CAN — requirement strength keywords

Purpose
Route purchase order requests through the appropriate approval chain based on dollar
thresholds, department policies, and urgency levels. Manage notification dispatch,
timeout escalation, and state transitions to ensure proper financial controls while
allowing emergency overrides for time-critical needs.

Audience
* AI agents: This spec drives an automated workflow engine. Each behavior is
  self-contained. Process behaviors in PRECEDENCE order when a PO enters the system.
* Human reviewers: Start with approval_routing to understand threshold logic,
  then read notification_dispatch and timeout_escalation for the async flow.
* Administrators: Threshold amounts and timeout durations are in @config.
  Adjust these values when corporate policy changes.

Scope
* IN SCOPE: PO validation, approval routing by amount threshold, emergency override,
  notification dispatch (sequential and parallel), timeout escalation, state management
* OUT OF SCOPE: Purchase order creation UI, vendor management, payment processing,
  budget tracking, three-way matching

Inputs
* purchase_order: PurchaseOrder - the PO requiring approval - required
* requester: User - employee submitting the request - required
* urgency: enum [standard, urgent, emergency] - processing priority - optional, default: standard

Outputs
* approval_status: ApprovalStatus - current workflow state and next steps
* approval_chain: list of Approver - ordered list of approvers with their decisions
* notifications: list of Notification - all messages dispatched during the workflow

@config
  thresholds:
    tier_1: 5000
    tier_2: 25000
    tier_3: 100000
    emergency_max: 10000
  timeouts:
    standard_hours: 48
    standard_reminder_hours: 24
    urgent_hours: 4
    emergency_hours: 2
  notification:
    max_retries: 3
    dispatch_deadline_seconds: 60
  escalation:
    final_fallback: usr_cfo
  budget_code_pattern: "[A-Z]{2}-[0-9]{4}-[0-9]{3}"

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
    timeout = $config.timeouts.standard_hours hours
  ELSE IF urgency = "urgent" THEN
    timeout = $config.timeouts.urgent_hours hours
  ELSE IF urgency = "emergency" THEN
    timeout = $config.timeouts.emergency_hours hours
  RETURNS timeout

Behaviors

BEHAVIOR request_validation: Validate that a purchase order has all required fields
  and a valid budget code before entering the approval workflow

  RULE required_fields:
    purchase_order.vendor MUST NOT be empty
    AND purchase_order.description MUST NOT be empty
    AND purchase_order.justification MUST NOT be empty
    AND purchase_order.amount MUST be greater than zero

  RULE budget_code_valid:
    purchase_order.budget_code MUST match pattern $config.budget_code_pattern
    -- Format: two-letter department prefix, four-digit cost center, three-digit account code
    -- Example: EN-4200-310 = Engineering, cost center 4200, account 310

  RULE requester_has_manager:
    requester.manager_id MUST NOT be null
    -- Every PO needs at least one approver in the chain

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | missing_required_fields | any of vendor, description, justification, or amount fails validation | critical | reject PO and return to requester | "Purchase order is incomplete. All fields (vendor, description, justification, amount) are required." |
  | invalid_budget_code | purchase_order.budget_code does not match $config.budget_code_pattern | critical | reject PO and return to requester | "Budget code format invalid. Expected format: XX-0000-000 (e.g., EN-4200-310)." |

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

  EXAMPLES:
    invalid_budget_code_case: budget_code="OPS-42" → rejected with "Budget code format invalid. Expected format: XX-0000-000 (e.g., EN-4200-310)."


BEHAVIOR approval_routing: Determine the approval chain based on PO amount,
  then route for review. Emergency purchases bypass the standard chain.

  @route approval_chain_assignment [first_match_wins]
    urgency = "emergency" AND amount <= $config.thresholds.emergency_max  → chain = [department_head] (emergency override)
    amount <= $config.thresholds.tier_1                                   → chain = [manager]
    amount <= $config.thresholds.tier_2                                   → chain = [manager, department_head]
    amount <= $config.thresholds.tier_3                                   → chain = [manager, department_head, finance_director]
    *                                                                     → chain = [manager, department_head, finance_director, $config.escalation.final_fallback]

  RULE chain_progression:
    WHEN current approver decision = "approved" AND next approver exists in chain
    THEN advance current_approver_id to next approver in chain

  RULE final_approval:
    WHEN last approver in chain decision = "approved"
    THEN approval_status.state = "approved"

  RULE any_rejection:
    WHEN ANY approver decision = "rejected"
    THEN approval_status.state = "rejected"
    AND remaining approvers are not consulted

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | missing_manager | requester.manager_id is null AND urgency != "emergency" | critical | halt workflow | "Requester has no manager assigned. Cannot build approval chain." |

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
    NOTES: $2,800 <= $config.thresholds.tier_1 ($5,000). Single approver: direct manager only.

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
    NOTES: $67,000 falls in the $25K-$100K band via @route. Three approvers required, processed sequentially.

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
    NOTES: Emergency + amount <= $config.thresholds.emergency_max ($10K) triggers first @route row.
           Bypasses manager, routes directly to department head. 2-hour timeout applies.

  State/Flow
    pending -> in_review: WHEN approval_chain_assignment matches and approver(s) notified
    in_review -> approved: WHEN last approver in chain decision = "approved"
    in_review -> rejected: WHEN ANY approver decision = "rejected"
    in_review -> info_requested: WHEN ANY approver requests additional information


BEHAVIOR notification_dispatch: Send approval request notifications to the
  appropriate approvers. Standard urgency uses sequential notification; urgent
  uses parallel.

  @route notification_strategy [first_match_wins]
    urgency = "standard"   → notify only the current approver; wait for decision before notifying next
    urgency = "urgent"     → notify ALL approvers simultaneously; ALL MUST approve
    urgency = "emergency"  → notify the single approver IMMEDIATELY with "EMERGENCY" prefix
    *                      → notify only the current approver (fallback to sequential)

  RULE notification_content:
    notification.message MUST include PO id, amount, vendor, and requester name

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | notification_send_failure | notification delivery fails after $config.notification.max_retries retry attempts | warning | log failure, continue workflow, alert system administrator | "Failed to deliver notification to {recipient_email} after {$config.notification.max_retries} attempts" |

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
    NOTES: Standard urgency via @route notification_strategy -- only the current approver is notified. Next approver waits.

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
    NOTES: Urgent via @route notification_strategy -- all three approvers notified
           simultaneously with URGENT-prefixed messages. ALL MUST approve.


BEHAVIOR timeout_escalation: Escalate to the next level of management when an
  approver does not respond within the timeout window defined by urgency level.

  @route escalation_action [first_match_wins]
    urgency = "standard" AND no response within $config.timeouts.standard_hours hours    → send reminder; if no response within additional $config.timeouts.standard_reminder_hours hours, escalate to approver's manager
    urgency = "urgent" AND no response within $config.timeouts.urgent_hours hours        → escalate IMMEDIATELY to approver's manager
    urgency = "emergency" AND no response within $config.timeouts.emergency_hours hours  → escalate to $config.escalation.final_fallback with "EMERGENCY ESCALATION" prefix
    *                                                                                     → no action (timeout not yet reached)

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | approver_unavailable | escalation target (approver's manager) is also unavailable or has no manager_id | critical | escalate to $config.escalation.final_fallback as final fallback, alert system administrator | "Approval chain broken: no available escalation target for PO {po_id}" |

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
    NOTES: 49 hours > $config.timeouts.standard_hours (48). Reminder sent first.
           If no response by hour 72, escalation to usr_sales_head occurs.

  EXAMPLES:
    urgent_escalation: po_id="PO-2026-00852", urgency="urgent", time_since_notification="5 hours" → escalated to usr_eng_head with "ESCALATION" prefix

Precedence

PRECEDENCE:
  1. required_fields (from BEHAVIOR request_validation)
  2. budget_code_valid (from BEHAVIOR request_validation)
  3. approval_chain_assignment (from BEHAVIOR approval_routing)
  4. notification_strategy (from BEHAVIOR notification_dispatch)
  5. escalation_action (from BEHAVIOR timeout_escalation)
  6. chain_progression (from BEHAVIOR approval_routing)
  7. any_rejection (from BEHAVIOR approval_routing)

Constraints
* Approval decisions MUST be recorded with timestamp
  and persisted to survive system restarts
* Notifications MUST be dispatched within $config.notification.dispatch_deadline_seconds seconds of a state change
* Timeout checks MUST run on a recurring schedule (EVERY 15 minutes at minimum)
* All monetary amounts MUST be displayed with two decimal places and currency code
* A user MUST NOT appear more than once in the same approval chain
* Emergency override MUST NOT apply to POs exceeding $config.thresholds.emergency_max

Dependencies
* org_directory service for manager lookups and department head resolution
* budget_code registry for validation against $config.budget_code_pattern
* notification service (email gateway) with retry capability
* workflow state persistence store (database or durable queue)
* scheduled job runner for timeout escalation checks

Changelog
* 3.0.0: 2026-03-01 - Migrated to SESF v4 hybrid notation. Added @config, @route
  tables, compact ERRORS, Notation section, State/Flow subsections, and updated
  PRECEDENCE to reference only BEHAVIOR rules.
* 2.1.0: 2026-02-15 - Migrated to SESF v2 behavior-centric format.
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

  STEP gather_data → $transactions, $total_revenue, $transaction_count:
    Read all sales transactions for the current date from the database → $transactions
    Set $total_revenue to 0
    Set $transaction_count to 0

  STEP calculate_totals → $average_sale:
    For each transaction in $transactions:
      Add transaction.amount to $total_revenue
      Add 1 to $transaction_count
    Calculate $average_sale as $total_revenue divided by $transaction_count

  STEP generate_report → $report_path:
    Write the summary to /reports/daily/YYYY-MM-DD.pdf → $report_path
    Send the report to the management distribution list

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | no_transactions | the day's sales list is empty | warning | generate an empty report noting "No transactions recorded" | "No sales transactions found for {date}" |
  | database_unavailable | the database connection fails | critical | notify the on-call engineer and skip report generation | "Cannot generate daily report: database connection failed" |

  EXAMPLES:
    typical_day: date="2026-03-01" → { "total_revenue": 15420.50, "transaction_count": 47, "average_sale": 328.10, "report_path": "/reports/daily/2026-03-01.pdf" }
    no_sales: date="2026-01-01" → { "total_revenue": 0, "transaction_count": 0, "report_path": "/reports/daily/2026-01-01.pdf", "warning": "No sales transactions found for 2026-01-01" }

Constraints
* Report generation SHOULD complete within 60 seconds
* All monetary amounts MUST be rounded to 2 decimal places
```

---

## Example 5: Standard Tier -- Customer Onboarding Workflow (mixed BEHAVIOR + PROCEDURE)

```
---
name: customer-onboarding
description: "Validate customer data, provision account, send welcome package, and schedule follow-up"
---

# Customer Onboarding Workflow

Meta
* Version: 2.0.0
* Date: 2026-03-01
* Domain: Customer Success
* Status: active
* Tier: standard

Notation
* $ -- references a variable or config value (e.g., $config.scoring.personalized_threshold)
* @ -- marks a structured block (@config for parameters)
* → -- means "produces" (in steps) or "yields" (in examples)
* MUST/SHOULD/MAY/CAN -- requirement strength keywords

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

@config
  scoring:
    base_score: 50
    phone_bonus: 10
    large_company_bonus: 15
    large_company_threshold: 50
    enterprise_bonus: 25
    professional_bonus: 15
    personalized_threshold: 75
  templates:
    welcome_email: "/templates/welcome_email.html"
    followup_reminder: "/templates/followup_reminder.html"
    internal_alert: "/templates/internal_alert.html"
  provisioning:
    timeout_seconds: 30
    email_deadline_minutes: 5
  followup:
    enterprise_days: 2
    professional_days: 5
    starter_days: 10

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
  Start with $score at $config.scoring.base_score
  IF customer.phone is present THEN add $config.scoring.phone_bonus to $score
  IF customer.employee_count is at least $config.scoring.large_company_threshold THEN add $config.scoring.large_company_bonus to $score
  IF plan = "enterprise" THEN add $config.scoring.enterprise_bonus to $score
  ELSE IF plan = "professional" THEN add $config.scoring.professional_bonus to $score
  RETURNS $score
  -- Score ranges: 50 (bare minimum) to 100 (enterprise with phone and 50+ employees)

FUNCTION determine_region(customer):
  IF customer.industry = "Healthcare" or customer.industry = "Finance"
    THEN $region = "us-east-1"
    -- regulated industries default to US East for compliance
  ELSE $region = "us-west-2"
  RETURNS $region

FUNCTION calculate_followup_date(plan):
  IF plan = "enterprise" THEN $followup = $config.followup.enterprise_days business days from today
  ELSE IF plan = "professional" THEN $followup = $config.followup.professional_days business days from today
  ELSE $followup = $config.followup.starter_days business days from today
  RETURNS $followup

ACTION send_welcome_package(customer, account, onboarding_score):
  Generate the welcome email from $config.templates.welcome_email
  If onboarding_score is at least $config.scoring.personalized_threshold:
    Append a personalized note from the account manager
  Send the email to customer.email
  Log: "Welcome package sent to {customer.email} for account {account.id}"
  RETURNS the delivery confirmation


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

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | invalid_email | customer.email fails email_format | critical | reject onboarding and return the error to the submitter | "Invalid email address: {customer.email}" |
  | missing_company | customer.company is empty | critical | reject onboarding | "Company name is required for all customers" |
  | enterprise_missing_phone | plan = "enterprise" and customer.phone is missing | critical | reject onboarding | "Enterprise customers must provide a phone number" |

  EXAMPLES:
    valid_professional_customer: customer={ "name": "Alicia Torres", "email": "alicia@brightpath.io", "company": "Brightpath Solutions", "phone": "+1-416-555-0199", "industry": "Technology", "employee_count": 120 }, plan="professional" → { "validation": "passed" }
    enterprise_missing_phone: customer={ "name": "James Whitfield", "email": "j.whitfield@meridian.com", "company": "Meridian Health Group", "industry": "Healthcare", "employee_count": 500 }, plan="enterprise" → rejected with "Enterprise customers must provide a phone number"


PROCEDURE onboard_customer: Walk through each onboarding step in order,
  from account creation to follow-up scheduling

  STEP validate → $validation_result:
    Validate the customer data using the validate_customer_data behavior → $validation_result
    Stop processing if $validation_result indicates failure

  STEP provision_account → $account, $account_id:
    Calculate the region using determine_region(customer) → $region
    Create a new account with the customer's name, email, selected plan, and $region → $account
    Record $account.id as $account_id for the remaining steps

  STEP score → $onboarding_score:
    Calculate $onboarding_score using calculate_onboarding_score(customer, plan)

  STEP send_welcome → $welcome_sent:
    Send a welcome email to the customer using send_welcome_package(customer, $account, $onboarding_score)
    Set $welcome_sent to true
    If $onboarding_score is at least $config.scoring.personalized_threshold:
      Include a personalized note from the account manager in the welcome email

  STEP schedule_followup → $followup_date:
    Calculate $followup_date using calculate_followup_date(plan)
    Send a follow-up reminder to the assigned account manager
    Send an internal alert to the customer success team with the onboarding summary

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | account_provisioning_failure | account creation fails | critical | notify the infrastructure team and mark onboarding as failed | "Account provisioning failed for {customer.email}. Infrastructure team notified." |
  | welcome_email_failure | the welcome email cannot be delivered after 3 attempts | warning | log the failure, continue onboarding, and flag for manual follow-up | "Welcome email delivery failed for {customer.email}. Manual follow-up required." |

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
           Score >= $config.scoring.personalized_threshold (75) so welcome email includes personalized note.
           Professional plan follow-up = $config.followup.professional_days (5) business days from Mar 1 = Mar 8.
           Technology industry -> us-west-2 region.

  EXAMPLES:
    starter_minimal_customer: customer={ "name": "Sam Nguyen", "email": "sam@tinycorp.io", "company": "TinyCorp", "industry": "Retail", "employee_count": 3 }, plan="starter" → { "account_id": "acct_20260301_00143", "status": "active", "onboarding_score": 50, "welcome_sent": true, "followup_date": "2026-03-15" }

Constraints
* Account provisioning MUST complete within $config.provisioning.timeout_seconds seconds
* Welcome email MUST be sent within $config.provisioning.email_deadline_minutes minutes of account creation
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
---
name: data-pipeline
description: "Ingest, validate, transform, and load data files into the warehouse with retry and recovery"
---

# Data Pipeline Processor

Meta
* Version: 4.0.0
* Date: 2026-03-01
* Domain: Data Engineering
* Status: active
* Tier: complex

Notation
* $ -- references a variable or config value (e.g., $config.file_size_limit)
* @ -- marks a structured block (@config for parameters)
* → -- means "produces" (in steps) or "yields" (in examples)
* MUST/SHOULD/MAY/CAN -- requirement strength keywords

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

@config
  file_size_limit: 500000000
  format_whitelist: [csv, json, parquet]
  duplicate_window_hours: 24
  column_match_threshold: 0.95
  warehouse:
    connection_retries: 3
    batch_size_min: 1
    batch_size_max: 10000
  quarantine_directory: "/data/quarantine"
  upload_directory: "/data/uploads"

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
  IF file_name ends with ".csv" THEN $format = "csv"
  ELSE IF file_name ends with ".json" THEN $format = "json"
  ELSE IF file_name ends with ".parquet" THEN $format = "parquet"
  ELSE $format = "unknown"
  RETURNS $format

FUNCTION select_schema(format, header_row):
  Look up the schema registry for a schema matching the format and header_row columns
  IF a matching schema is found THEN RETURNS the schema
  ELSE RETURNS nothing

FUNCTION calculate_batch_count(total_records, batch_size):
  Calculate $count as total_records divided by batch_size, rounded up to the nearest whole number
  RETURNS $count

FUNCTION summarize_run(file_results):
  Calculate $files_succeeded as the number of items in file_results where state is "completed"
  Calculate $files_failed as the number of items in file_results where state is "failed" or state is "quarantined"
  Calculate $total_records_loaded as the sum of records_out across file_results where state is "completed"
  IF $files_failed is greater than 0 and $files_succeeded is greater than 0
    THEN $status = "completed_with_errors"
  ELSE IF $files_failed equals the number of items in file_results
    THEN $status = "failed"
  ELSE $status = "completed"
  RETURNS { files_processed, $files_succeeded, $files_failed, $total_records_loaded, $status }


BEHAVIOR quarantine_check: Determine whether a file should be quarantined
  before any processing begins

  RULE file_too_large:
    WHEN file.size exceeds $config.file_size_limit
    THEN quarantine the file
    -- 500 MB limit protects against runaway resource consumption

  RULE unsupported_format:
    WHEN detect_format(file.name) returns a value not in $config.format_whitelist
    THEN quarantine the file

  RULE duplicate_file:
    WHEN a record exists in the audit log where file_name equals file.name
         and action equals "completed" and the entry is from the last $config.duplicate_window_hours hours
    THEN quarantine the file
    -- prevent reprocessing of recently completed files

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | quarantined_file | any quarantine rule matches | warning | move the file to $config.quarantine_directory, log the reason, notify the data team | "File {file.name} quarantined: {reason}" |

  EXAMPLES:
    oversized_file: file={ "name": "huge_export.csv", "size": 750000000 } → { "state": "quarantined", "reason": "File size 750000000 exceeds 500 MB limit" }
    unknown_format: file={ "name": "data.xlsx", "size": 1024000 } → { "state": "quarantined", "reason": "Unsupported file format: unknown" }
    duplicate_recent: file={ "name": "daily_sales.csv", "size": 2048000 }, recent_completion=true → { "state": "quarantined", "reason": "Duplicate of file completed within last 24 hours" }


PROCEDURE validate_file: Check that a file's structure matches the expected
  schema before transformation

  STEP detect → $format:
    Determine the format using detect_format(file.name) → $format
    Move the file from "queued" to "validating"
    Log an audit entry: "Validation started for {file.name}"

  STEP read_header → $header_row:
    Read the first row of the file to extract the column names → $header_row
    If the file is empty:
      Stop processing and raise empty_file error

  STEP match_schema → $schema:
    Look up the schema using select_schema($format, $header_row) → $schema
    If no schema is found:
      Stop processing and raise schema_not_found error

  STEP validate_columns → $error_list:
    Set $error_list to empty
    For each column defined in $schema:
      If the column is marked as required and is missing from $header_row:
        Add "Missing required column: {column.name}" to $error_list
      If the column is present and has a pattern defined:
        Check that at least $config.column_match_threshold of values in that column match the pattern
        If fewer than $config.column_match_threshold match:
          Add "Column {column.name}: {match_percentage}% of values match expected pattern (minimum 95%)" to $error_list
    If $error_list is not empty:
      Stop processing and raise validation_failed error

  STEP record_stats → $records_in:
    Count the total number of records in the file (excluding the header) → $records_in
    Record $records_in on the file result
    Log an audit entry: "Validation passed for {file.name}: {$records_in} records found"

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | empty_file | the file contains no data rows | warning | move the file from "validating" to "failed", log the issue | "File {file.name} is empty -- no records to process" |
  | schema_not_found | no matching schema exists for the file's format and column structure | critical | move the file from "validating" to "failed", notify the data engineering team | "No schema found for {file.name} with format {$format}. Manual schema registration required." |
  | validation_failed | one or more columns fail validation | critical | move the file from "validating" to "failed", attach $error_list to the file result | "Validation failed for {file.name}: {error_count} column issues found" |

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

  EXAMPLES:
    missing_required_column: file={ "name": "orders_broken.csv", "format": "csv" }, header_row=["order_id", "amount", "order_date"] → { "state": "failed", "errors": ["Missing required column: customer_id", "Missing required column: status"] }


PROCEDURE transform_records: Apply data transformations to validated records
  before loading them into the warehouse

  STEP prepare → $batch_count, $records_out, $current_batch:
    Move the file from "validating" to "transforming"
    Calculate the number of batches using calculate_batch_count($records_in, batch_size) → $batch_count
    Set $records_out to 0 and $current_batch to 1
    Log an audit entry: "Transformation started for {file.name}: {$batch_count} batches"

  STEP process_batches → $records_out:
    While $current_batch is at most $batch_count:
      Read the next batch of records from the file
      For each record in the batch:
        Trim whitespace from all string fields
        Convert date fields to ISO 8601 format (YYYY-MM-DD)
        Convert all number fields to standard decimal notation
        If any required field is missing or null:
          Skip this record and add a warning to the audit log:
            "Skipped record {record.row_number}: missing required field {field.name}"
        Otherwise:
          Add 1 to $records_out
      Add 1 to $current_batch

  STEP deduplicate → $records_out:
    Sort the transformed records by record.id
    Group the records by record.id
    For each group with more than one record:
      Keep only the first record in the group
      Subtract the number of removed duplicates from $records_out
      Log an audit entry: "Removed {duplicate_count} duplicate records from {file.name}"

  STEP finalize:
    Log an audit entry: "Transformation complete for {file.name}: {$records_out} of {$records_in} records ready to load"

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | batch_read_failure | a batch cannot be read from the file | critical | move the file from "transforming" to "failed", log the error with the batch number | "Failed to read batch {$current_batch} of {$batch_count} from {file.name}" |

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

  EXAMPLES:
    all_records_skipped: file={ "name": "corrupt_data.json", "records_in": 15 }, batch_size=500 → { "state": "transforming", "batch_count": 1, "records_out": 0 }


PROCEDURE load_to_warehouse: Load transformed records into the data warehouse
  with retry logic for transient failures

  STEP check_records:
    If $records_out equals 0:
      Log an audit entry: "No records to load for {file.name} -- skipping warehouse load"
      Move the file from "transforming" to "completed"
      Return the result
      -- Zero records is not an error -- transformation may have filtered everything out

  STEP connect → $connection:
    Move the file from "transforming" to "loading"
    Attempt to connect to the warehouse using warehouse_connection → $connection
    If $connection fails:
      Log the error and raise connection_failed error

  STEP load_batches → $loaded_count:
    Calculate the number of load batches using calculate_batch_count($records_out, batch_size) → $load_batch_count
    Set $loaded_count to 0 and $current_batch to 1
    While $current_batch is at most $load_batch_count:
      Take the next batch of transformed records
      Attempt to insert the batch into the warehouse:
        If it succeeds:
          Add the number of records in the batch to $loaded_count
        If it fails:
          Attempt the insert again up to max_retries times
          If all retries fail:
            Log the error with the batch number and raise load_failed error
      Add 1 to $current_batch

  STEP verify:
    Query the warehouse to count the records just inserted for this file → $warehouse_count
    If $warehouse_count does not equal $loaded_count:
      Log a warning: "Record count mismatch: expected {$loaded_count}, found {$warehouse_count}"
    Move the file from "loading" to "completed"
    Log an audit entry: "Load complete for {file.name}: {$loaded_count} records inserted"

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | connection_failed | the warehouse connection cannot be established after $config.warehouse.connection_retries attempts | critical | move the file from "loading" to "failed", notify the infrastructure team | "Cannot connect to warehouse: {connection_error}. File {file.name} load aborted." |
  | load_failed | a batch insert fails after max_retries attempts | critical | move the file from "loading" to "failed", record which batch failed, roll back any partially inserted records for this file | "Batch {$current_batch} failed after {max_retries} retries for {file.name}. Partial load rolled back." |

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

  EXAMPLES:
    retry_then_success: file={ "name": "products_20260301.json", "records_out": 800 }, batch_size=500, max_retries=3 → { "state": "completed", "loaded_count": 800, "retry_count": 1 }
    permanent_failure: file={ "name": "events_20260301.parquet", "records_out": 5000 }, batch_size=500, max_retries=3 → { "state": "failed", "loaded_count": 0, "retry_count": 3 }


PROCEDURE run_pipeline: Orchestrate the full ingestion pipeline from file
  discovery through warehouse loading

  STEP discover → $file_list:
    Read the list of files in the upload_directory → $file_list
    Keep only the files that have not been processed before
      -- check the audit log for previous completions
    Sort $file_list by uploaded_at, oldest first
    If $file_list is empty:
      Log an audit entry: "Pipeline run: no new files found"
      Return an empty result

  STEP initialize → $run_id, $started_at, $files_processed:
    Generate a new $run_id
    Record the $started_at timestamp
    Set $files_processed to 0

  STEP process_files → $file_results:
    Set $file_results to empty list
    For each file in $file_list:
      Add 1 to $files_processed
      Run quarantine_check on the file
      If the file is quarantined:
        Record the file result with state "quarantined" in $file_results and skip to the next file
      Run validate_file on the file
      If validation fails:
        Record the file result with state "failed" in $file_results and skip to the next file
      Run transform_records on the file
      If transformation produces zero records:
        Record the file result with state "completed" in $file_results and skip to the next file
      Run load_to_warehouse on the file
      Record the file result in $file_results

  STEP summarize → $pipeline_result:
    Calculate $pipeline_result using summarize_run($file_results)
    Record the $completed_at timestamp
    Log an audit entry: "Pipeline run {$run_id} complete: {$pipeline_result.files_succeeded} succeeded, {$pipeline_result.files_failed} failed, {$pipeline_result.total_records_loaded} records loaded"

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | pipeline_interrupted | an unexpected error halts the pipeline before all files are processed | critical | record partial results, log the interruption point, notify the data engineering team | "Pipeline run {$run_id} interrupted after processing {$files_processed} of {total_files} files" |

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
           huge_export.csv quarantined for exceeding $config.file_size_limit. products_20260301.json processed
           successfully (800 records after transformation). Total loaded = 1247 + 800 = 2047.

  EXAMPLES:
    empty_upload_directory: upload_directory="/data/uploads", files_in_directory=[] → { "status": "completed", "files_processed": 0, "total_records_loaded": 0 }

Precedence

PRECEDENCE:
  1. file_too_large (from BEHAVIOR quarantine_check)
  2. unsupported_format (from BEHAVIOR quarantine_check)
  3. duplicate_file (from BEHAVIOR quarantine_check)
  -- Quarantine checks run first. Processing PROCEDUREs follow in document order.

Constraints
* File state transitions MUST follow the lifecycle: queued -> validating ->
  transforming -> loading -> completed (or failed/quarantined at any point)
* A file MUST NOT move backward in the state lifecycle
* Batch size MUST be between $config.warehouse.batch_size_min and $config.warehouse.batch_size_max
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
* 4.0.0: 2026-03-01 - Migrated to SESF v4 hybrid notation. Added @config,
  $variable threading, compact ERRORS/EXAMPLES, Notation section, and fixed
  PRECEDENCE to reference only BEHAVIOR rules.
* 3.0.0: 2025-12-15 - Rewrote in SESF v3 procedural format. Added PROCEDURE
  blocks for validate_file, transform_records, load_to_warehouse, and
  run_pipeline. Added quarantine_check behavior with PRECEDENCE.
* 2.0.0: 2025-10-01 - Added retry logic and batch processing. Introduced
  state lifecycle tracking.
* 1.1.0: 2025-08-01 - Added parquet format support and deduplication step
* 1.0.0: 2025-06-01 - Initial version with CSV-only support
```

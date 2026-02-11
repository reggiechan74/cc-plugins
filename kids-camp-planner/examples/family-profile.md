---
# Kids Camp Planner - Family Profile
# This file lives in your research directory (e.g., camp-research/family-profile.md)
# It is created automatically during setup, or you can copy and fill it in manually.

# Children
kids:
  - name: "Child 1"
    dob: "2017-05-15"
    school:
      type: "public"
      board: "TDSB"
      name: "Example Public School"
    interests: ["swimming", "art", "robotics"]
    allergies: ["peanuts"]
    dietary: [""]
    medical_notes: ""
    special_accommodations: ""
  - name: "Child 2"
    dob: "2019-09-20"
    school:
      type: "public"
      board: "TDSB"
      name: "Example Public School"
    interests: ["soccer", "nature", "drama"]
    allergies: []
    dietary: [""]
    medical_notes: ""
    special_accommodations: ""

# School Information
# For private schools: board field is the nearest public board (for PA day program alignment)
# DEPRECATED - Top-level school block (backward compat: used when no per-child school)
# New profiles should put school under each child in the kids array above.
school:
  type: "public"  # public or private
  board: "TDSB"   # nearest public board (e.g., TDSB, YRDSB, PDSB, OCDSB, DPCDSB)
  name: "Example Public School"
  calendar_url: ""  # optional: URL to school calendar PDF or page
  # Private school specific (leave blank for public schools):
  private_calendar_url: ""   # URL to private school's parent calendar
  march_break_weeks: 1       # number of weeks (some private schools have 2-week break)
  notes: ""                  # e.g., "March break is 2 weeks", "School starts before Labour Day"

# Parents / Guardians
parents:
  - name: "Parent 1"
    role: "parent"
    work_address: "123 Bay St, Toronto, ON"
    work_schedule: "Mon-Fri 8:30am-5:00pm"
    can_do_pickup: true
    can_do_dropoff: true
    dropoff_earliest: "7:30am"
    pickup_latest: "6:00pm"
  - name: "Parent 2"
    role: "parent"
    work_address: "456 University Ave, Toronto, ON"
    work_schedule: "Mon-Fri 9:00am-5:30pm"
    can_do_pickup: true
    can_do_dropoff: true
    dropoff_earliest: "8:00am"
    pickup_latest: "5:30pm"

# Home Location
home_address: "789 Maple Ave, Toronto, ON M4E 1A1"
max_commute_minutes: 20

# Budget
budget:
  total_summer: 5000        # total summer budget across all kids
  per_child_per_week: 350   # target per child per week
  per_child_per_day: 70     # target per child per day (PA days, partial weeks, drop-ins)
  flexibility: "moderate"   # strict, moderate, flexible
  before_care_ok: true
  after_care_ok: true
  lunch_preference: "pack"  # pack, buy, either

# Vacation / Exclusion Dates
# Dates when camps are NOT needed (family trips, vacation, etc.)
vacation_dates:
  - start: "2025-07-14"
    end: "2025-07-18"
    note: "Family cottage trip"
  - start: "2025-08-11"
    end: "2025-08-15"
    note: "Camping trip"

# School Year Dates (override defaults if needed)
# IMPORTANT for private schools: fill these in since they likely differ from public board
school_dates:
  last_day: ""           # leave blank to use school board default
  first_day_fall: ""     # leave blank for day after Labour Day (private schools may start earlier!)
  march_break_start: ""  # leave blank for Ontario default; fill for private school dates
  march_break_end: ""    # leave blank for Ontario default; fill for private school dates
  fall_break_start: ""   # leave blank if no fall break (most public boards); fill for private schools
  fall_break_end: ""     # e.g., GIST has Nov 3-7 fall break
  early_dismissal_dates: []  # dates with early dismissal (e.g., ["2025-12-19", "2026-06-26"])
---

# Family Notes

Add any additional context here that may help with camp planning:

- Child 1 did YMCA day camp last year and loved it
- Child 2 is not yet comfortable with full-day swimming
- Prefer camps within walking distance if possible
- Grandparent available for pickup on Wednesdays

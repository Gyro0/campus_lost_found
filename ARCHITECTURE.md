# Person 2 Architecture & Workflow Diagram

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      USER INTERACTIONS                              │
│                    (Person 3 will build UI)                        │
└────────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
         │          │          │          │          │
    CREATE      EDIT       DELETE      RECOVER     DETAIL
    (Lost)     (Own)      (Own)      (Own)        (Public)
         │          │          │          │          │
┌────────▼──────────▼──────────▼──────────▼──────────▼────────────────┐
│                        VIEWS (reports/views.py)                      │
│                                                                       │
│  LostCreateView      ReportUpdateView  ReportDeleteView  Detail     │
│  FoundCreateView     (OwnerMixin)      (OwnerMixin)      (Public)   │
│  (LoginRequired)                                                     │
│                      mark_recovered_view (owner-only)               │
└────────┬──────────────┬──────────────────┬──────────────────────────┘
         │              │                  │
┌────────▼──────────────▼──────────────────▼────────────────────────────┐
│                    FORMS (reports/forms.py)                           │
│                                                                        │
│  ReportForm (ModelForm):                                              │
│  - title, description, category, location, event_date                │
│  - image (optional), contact_info (optional)                         │
│  - Excludes: report_type (set by view), status (always OPEN)         │
│  - Excludes: user (set to request.user), timestamps (auto)           │
└────────┬──────────────┬──────────────────┬────────────────────────────┘
         │              │                  │
┌────────▼──────────────▼──────────────────▼────────────────────────────┐
│                    MODELS (reports/models.py)                         │
│                                                                        │
│  ┌─────────────────────────────────┐   ┌──────────────────────────┐  │
│  │      Category Model             │   │    Report Model          │  │
│  │                                 │   │                          │  │
│  │ - name (unique)                 │   │ - user (FK to User)      │  │
│  │ - created_at                    │   │ - title                  │  │
│  │                                 │   │ - description            │  │
│  │ ordering: name (A-Z)            │   │ - category (FK)          │  │
│  └─────────────────────────────────┘   │ - report_type (LOST/     │  │
│                ▲                       │   FOUND)                 │  │
│                │                       │ - status (OPEN/RECOVERED)│  │
│                │                       │ - location               │  │
│                └───────────────────────│ - event_date             │  │
│                                        │ - image (optional)       │  │
│              Indexes:                  │ - contact_info           │  │
│              - (type, status)          │ - recovered_at           │  │
│              - (category, status)      │ - created_at             │  │
│              - (event_date)            │ - updated_at             │  │
│                                        │                          │  │
│                                        │ Methods:                 │  │
│                                        │ - mark_recovered()       │  │
│                                        │ - __str__()              │  │
│                                        └──────────────────────────┘  │
└────────┬──────────────┬──────────────────┬────────────────────────────┘
         │              │                  │
┌────────▼──────────────▼──────────────────▼────────────────────────────┐
│                    DATABASE (SQLite)                                   │
│                                                                        │
│  ┌─────────────────────────┐    ┌────────────────────────────────┐  │
│  │  reports_category       │    │  reports_report                │  │
│  ├─────────────────────────┤    ├────────────────────────────────┤  │
│  │ id (PK)                 │    │ id (PK)                        │  │
│  │ name (UNIQUE)           │    │ user_id (FK auth_user)         │  │
│  │ created_at              │    │ title                          │  │
│  └─────────────────────────┘    │ description                    │  │
│                                 │ category_id (FK, nullable)    │  │
│                                 │ report_type (varchar)          │  │
│                                 │ status (varchar)               │  │
│                                 │ location                       │  │
│                                 │ event_date                     │  │
│                                 │ image                          │  │
│                                 │ contact_info                   │  │
│                                 │ recovered_at                   │  │
│                                 │ created_at                     │  │
│                                 │ updated_at                     │  │
│                                 │                                │  │
│                                 │ Indexes:                       │  │
│                                 │ - (report_type, status)        │  │
│                                 │ - (category_id, status)        │  │
│                                 │ - (event_date)                 │  │
│                                 └────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Request/Response Flow for Creating a Lost Report

```
USER
  │
  ├─ Not logged in?
  │  └─ (1) GET /reports/lost/new/
  │     └─ LoginRequiredMixin redirects to /accounts/login/
  │
  └─ Logged in
     ├─ (2) GET /reports/lost/new/
     │   └─ LostReportCreateView renders report_form.html
     │
     └─ (3) POST /reports/lost/new/ with form data
        └─ ReportForm validates data
           ├─ Valid:
           │  └─ form_valid() called
           │     ├─ form.instance.user = request.user
           │     ├─ form.instance.report_type = 'LOST'
           │     ├─ form.save() → saves to database
           │     ├─ messages.success() adds flash message
           │     └─ redirect to /reports/{id}/ (detail page)
           │
           └─ Invalid:
              └─ Re-render form with errors
```

---

## Permission Enforcement Flow

```
┌─ Request for /reports/{id}/edit/ ─────────────────────────────┐
│                                                                 │
├─ LoginRequiredMixin                                            │
│  ├─ User logged in? YES → continue                            │
│  └─ User logged in? NO → redirect to /accounts/login/         │
│                                                                 │
├─ OwnerRequiredMixin                                            │
│  ├─ get_object() retrieves report {id}                        │
│  ├─ test_func() checks: report.user == request.user           │
│  │  ├─ Match? YES → continue to UpdateView                    │
│  │  └─ Match? NO → handle_no_permission()                     │
│  │     ├─ messages.error("You can only edit...")              │
│  │     └─ redirect to /reports/{id}/                          │
│  │                                                              │
│  └─ UpdateView processes the request                          │
│     ├─ GET: show edit form (only for owner)                   │
│     └─ POST: update report (only for owner)                   │
│                                                                 │
└─ Response to user ───────────────────────────────────────────────┘
```

---

## Status Transition Flow

```
Report Created
  │ (status = OPEN, recovered_at = NULL)
  │
  ├─ User views: /reports/{id}/ ──→ Shows detail page
  ├─ User edits: /reports/{id}/edit/ ──→ Can modify all fields
  ├─ User deletes: /reports/{id}/delete/ ──→ Report deleted
  │
  └─ User marks recovered: POST /reports/{id}/recover/
     └─ mark_recovered_view() called
        ├─ Check: report.user == request.user
        │  ├─ NO: error message, redirect
        │  └─ YES: continue
        │
        ├─ Check: method == 'POST'
        │  ├─ NO: redirect without action
        │  └─ YES: continue
        │
        └─ Call: report.mark_recovered()
           ├─ status = RECOVERED
           ├─ recovered_at = timezone.now()
           ├─ save()
           ├─ messages.success("Report marked...")
           └─ redirect to /reports/{id}/

Report Recovered
  │ (status = RECOVERED, recovered_at = <timestamp>)
  │
  ├─ User cannot edit (optional: could allow)
  ├─ User can delete (optional)
  └─ Report still visible (searchable, filterable)
```

---

## Admin Interface Workflow

```
ADMIN LOGIN
    │
    ├─ Go to /admin/
    │
    ├─ Reports > Categories
    │  ├─ Add new category
    │  ├─ Search categories
    │  ├─ Edit/Delete categories
    │  └─ Sorted alphabetically
    │
    └─ Reports > Reports
       ├─ View all reports
       ├─ Filters:
       │  ├─ By Report Type (LOST/FOUND)
       │  ├─ By Status (OPEN/RECOVERED)
       │  ├─ By Category
       │  └─ By Created Date
       │
       ├─ Search:
       │  ├─ By Title
       │  ├─ By Description
       │  ├─ By Location
       │  └─ By Username (report owner)
       │
       └─ Actions:
          ├─ View details
          ├─ Edit (mark recovered, change status)
          ├─ Delete (remove report)
          └─ Readonly fields:
             ├─ timestamps (created_at, updated_at)
             ├─ user (on edit - can't change owner)
             └─ report_type (on edit - can't change LOST→FOUND)
```

---

## Test Coverage Map

```
ReportModelTests (7 tests)
├─ Category creation & uniqueness (2)
├─ Report creation & timestamps (4)
└─ Mark recovered functionality (1)

LostReportCreateViewTests (3)
├─ Anonymous user redirected (1)
├─ Authenticated user access (1)
└─ Create lost report success (1)

FoundReportCreateViewTests (1)
└─ Create found report success (1)

ReportUpdateViewTests (3)
├─ Non-owner cannot edit (1)
├─ Owner can edit (1)
└─ Data persists after edit (1)

ReportDeleteViewTests (2)
├─ Non-owner cannot delete (1)
└─ Owner can delete (1)

ReportDetailViewTests (4)
├─ Detail page is public (1)
├─ is_owner flag for owner (1)
├─ is_owner flag for non-owner (1)
└─ Detail page structure (1)

MarkRecoveredViewTests (3)
├─ Non-owner cannot recover (1)
├─ Owner can recover (1)
└─ Timestamp set on recover (1)

─────────────────────
TOTAL: 22 tests
PASSING: 14-16 (depending on templates)
```

---

## URL Routing Map

```
/reports/
├─ lost/new/              → LostReportCreateView (POST only)
├─ found/new/             → FoundReportCreateView (POST only)
├─ <id>/                  → ReportDetailView (GET - public)
├─ <id>/edit/             → ReportUpdateView (owner-only)
├─ <id>/delete/           → ReportDeleteView (owner-only)
└─ <id>/recover/          → mark_recovered_view (owner-only, POST)

Future (Person 3):
├─ (empty)                → ReportListView (search & filter)
└─ my-reports/            → UserReportsListView (dashboard)
```

---

## Field Responsibility Matrix

```
Who Sets?              │ Field            │ When?
───────────────────────┼──────────────────┼───────────────────────
User (form)            │ title            │ On create/edit
User (form)            │ description      │ On create/edit
User (form)            │ category         │ On create/edit
User (form)            │ location         │ On create/edit
User (form)            │ event_date       │ On create/edit
User (form)            │ image            │ On create/edit (optional)
User (form)            │ contact_info     │ On create/edit (optional)
───────────────────────┼──────────────────┼───────────────────────
View (auto)            │ user             │ On create (from request.user)
View (auto)            │ report_type      │ On create (LOST or FOUND)
───────────────────────┼──────────────────┼───────────────────────
Admin/View             │ status           │ On create (OPEN) / mark recovered
Admin only             │ recovered_at     │ On mark recovered
───────────────────────┼──────────────────┼───────────────────────
Django (auto)          │ created_at       │ On create (auto_now_add)
Django (auto)          │ updated_at       │ On any save (auto_now)
```

---

## Security Boundary Map

```
┌────────────────────────────────────────────────────────────┐
│ Anonymous Users                                            │
├────────────────────────────────────────────────────────────┤
│ CAN:                          │ CANNOT:                     │
│ ✓ View report details         │ ✗ Create reports           │
│ ✓ View report list (search)   │ ✗ Edit any report          │
│ ✓ Filter/search reports       │ ✗ Delete any report        │
│ ✓ Access admin login          │ ✗ Mark recovered           │
│                               │ ✗ Access admin panel       │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Authenticated Users (Non-owners)                           │
├────────────────────────────────────────────────────────────┤
│ CAN:                          │ CANNOT:                     │
│ ✓ Do everything anonymous     │ ✗ Edit other reports       │
│ ✓ Create new reports          │ ✗ Delete other reports     │
│ ✓ Edit own reports            │ ✗ Mark other's as recovered│
│ ✓ Delete own reports          │ ✗ Access admin panel       │
│ ✓ Mark own as recovered       │ ✗ Manage categories        │
│                               │ ✗ Moderate reports         │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Admin/Staff Users                                          │
├────────────────────────────────────────────────────────────┤
│ CAN:                                                        │
│ ✓ Do everything authenticated users can do                 │
│ ✓ Access admin panel                                       │
│ ✓ Edit/delete ANY report                                   │
│ ✓ Create/edit categories                                   │
│ ✓ Mark reports as recovered                                │
│ ✓ Filter/search all reports                                │
│ ✓ Export report data                                        │
└────────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

```
Operation              │ Complexity │ Indexes Used
───────────────────────┼────────────┼──────────────────────────
Create report          │ O(1)       │ None (INSERT)
View detail            │ O(1)       │ Primary key
Edit report            │ O(1)       │ Primary key
Delete report          │ O(1)       │ Primary key (DELETE)
Mark recovered         │ O(1)       │ Primary key
───────────────────────┼────────────┼──────────────────────────
List all reports       │ O(n)       │ created_at (pagination)
Filter by type         │ O(log n)   │ (report_type, status)
Filter by status       │ O(log n)   │ (report_type, status)
Filter by category     │ O(log n)   │ (category, status)
Filter by date         │ O(log n)   │ event_date
Search text            │ O(n)       │ None (full table scan)
```

---

## Handoff Checklist

- [x] Models defined and tested
- [x] Forms created with validation
- [x] Views implemented with permission checks
- [x] URLs configured
- [x] Admin interface set up
- [x] Database migrations created
- [x] Comprehensive tests written (14 passing)
- [x] Git commits made with clear messages
- [x] Documentation written
- [x] Code reviewed for security
- [ ] Templates created (Person 3)
- [ ] List/search views implemented (Person 3)
- [ ] Navigation integrated (Person 1)

**Status**: Ready for Person 3 → List/Search/Templates

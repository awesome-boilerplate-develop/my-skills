# Master route & selector reference

## Environment domains

| Environment | Base Domain URL | Use Case |
|---|---|---|
| **SIT** | `https://sitmcare21.columbiaasia.com` | When user says "SIT" or "sau deploy". |
| **DEV** | `https://devmcare21.columbiaasia.com` | When user says "DEV", "devmcare21", or "môi trường dev". |

Environment is a required parameter — **always confirm SIT or DEV with the user before running
anything, even if the request already names one.** This skill is used by testers verifying real
environments; silently running against the wrong one (or a misheard/mistyped one) produces a
report that looks fine but checked nothing meaningful.

- **Country base prefix**: all authenticated routes require `#/MYS/` (Malaysia).
- **Target URL pattern**: `${BASE_URL}/#/MYS/dashboard/<master-slug>` or
  `${BASE_URL}/#/MYS/admincare/masters/<master-slug>`.

## Route mapping

- **Fluid Balance Shift**: `#/MYS/dashboard/fluid-balance-shift-master`
- **Braden Risk Assessment**: `#/MYS/dashboard/braden-risk-assessment-master`
- **Stock Master**: `#/MYS/admincare/masters/stock-master`
- **Blood Group Master**: `#/MYS/dashboard/blood-group-master`
- **Allergy Master**: `#/MYS/dashboard/allergy-master`
- **Antenatal Care Master**: `#/MYS/dashboard/antenatal-care-master`
- **EWS Parameter Master**: `#/MYS/dashboard/ews-parameter-master`
- **EWS Physiological Parameter**: `#/MYS/dashboard/ews-physiological-parameter-master`
- **Doctor Favorites / Prescription**: `#/MYS/patient-workspace`

If the user asks for a screen not listed here, ask them for the route, or find it through the
app's own menu (`browser_snapshot` the sidebar, `browser_click` into it) and note the resulting
`#/MYS/...` hash in the report so it can be added to this list.

## Key selectors

- Table container: `#table-wrapper`
- Table headers: `th` (text inside `.sorting-span`)
- Data rows: `tr.table-col-row`
- No-data row: `.table-no-data-row` (contains "No Record Found")
- Control-suite tables (Braden, Fluid Balance): `app-table-control` (`app-tc-header`,
  `app-tc-chip-filter`, `app-tc-table`, `app-tc-paginator`)
- Legacy master tables (Blood Group, etc.): `app-master-data-table`, `app-master-common-table`
- Dialog container: `.mat-mdc-dialog-container`, `.confirmation-dialog`
- Toast notifications: `.toast-message` (auto-dismisses in ~5s — read it immediately)
- Validation errors: `mat-error`, `.mat-mdc-form-field-error`

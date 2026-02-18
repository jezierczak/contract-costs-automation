# Commands

## Environment

### Test environment

```powershell
$env:APP_ENV='test'
```

### Production environment

```powershell
$env:APP_ENV='prod'
```

## CLI run format

```powershell
uv run python -m contract_costs.cli.main <command>
```

## Top-level commands

- `init` - Initialize application workspace.
- `run` - Run background/watcher workflows.
- `login` - Log in user session.
- `logout` - Log out current session.
- `whoami` - Show current session/user context.
- `prepare` - Generate editable inputs (mostly Excel).
- `apply` - Apply prepared inputs to domain state.
- `add` - Add domain entities directly.
- `edit` - Edit selected entities.
- `show` - Show current data snapshots/lists.
- `set` - Set statuses/actions on entities.
- `use` - Select active organization context.
- `remove` - Remove/deactivate membership links.
- `accept` - Accept organization invitation.
- `system` - Run system maintenance commands.
- `report` - Generate reports.
- `documents` - Document reprocess/delete utilities.

## Group commands

### `prepare`

- `prepare records for-assignment` (`ass`) - Prepare financial records for assignment/editing.
- `prepare records for-accountant` (`acc`) - Prepare financial records for accountant.
- `prepare records unpaid` (`unp`) - Prepare unpaid records for paid-status assignment.
- `prepare records for-review` (`rev`) - Prepare records for review flow.
- `prepare contract` - Prepare contract structure for editing.
- `prepare contract-progress` - Prepare contract progress file.
- `prepare companies` - Prepare companies file for editing.
- `prepare documents` - Prepare documents workflow file.

### `apply`

- `apply records to-processed` (`ass`, `pro`) - Apply prepared financial records import.
- `apply records to-accountant` (`acc`) - Mark records sent to accountant.
- `apply records paid` (`unp`) - Apply paid-status updates.
- `apply contract` - Apply contract changes from prepared file.
- `apply contract-progress` - Apply contract progress changes.
- `apply companies` - Apply company changes from prepared file.
- `apply documents` - Apply document assignment/management changes.

### `add`

- `add company` - Add company.
- `add contract` - Add contract.
- `add value-type` - Add value type.
- `add contract-snapshot` - Create contract snapshot.
- `add snapshot` - Alias/shortcut snapshot add flow.
- `add organization` - Add organization.
- `add organization-user` - Add user to organization.
- `add user` - Add user.

### `edit`

- `edit company` - Edit company.
- `edit value-type` - Edit value type.
- `edit value-type-code` - Change value type code.
- `edit organization-user` - Edit organization user role/status.

### `show`

- `show companies` - Show companies.
- `show contracts` - Show contracts.
- `show records` - Show financial records list.
- `show record` - Show single financial record details.
- `show value-types` - Show value types.
- `show snapshots` - Show contract snapshots list.
- `show snapshot` - Show single snapshot details.
- `show organizations` - Show organizations for current user.
- `show documents` - Show source documents.

### `set`

- `set contract-status` - Set contract status.
- `set record` - Set financial record action/state.

### `use`

- `use organization` - Set active organization context.

### `remove`

- `remove organization-user` - Remove user from organization.

### `accept`

- `accept organization` - Accept organization invitation.

### `system`

- `system backfill` - Ensure required system contracts exist.

### `report`

- `report costs` - Generate contract cost report.

### `documents`

- `documents reprocess` - Reprocess document.
- `documents delete` - Delete document.

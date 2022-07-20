# Update Linear labels action

This action allows to move issues to a workflow status and add a specified label.

## Inputs

### `linear_token`

**Required** Access token for Linear API.

### `from_status_name`

**Required** Status name (case insensitive) to filter issues.
### `to_status_name`

**Required** New status name (case insensitive) to move issues to.

### `label_name`

**Required** Name of the label to add.

## Example usage

```
uses:pieter-azumuta/update-linear-labels-action@v1
with:
  linear_token: ...
  from_status_name: Merged
  to_status_name: Released
  label_name ...
```

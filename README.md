# Update Linear labels action

This action allows to add specified labels to a linear issue.

## Inputs

## `label_name`

**Required** Name of the label to add.

## `branch_name`

**Required** Name of the branch assotiated with Linear issue.

## `linear_token`

**Required** Access token for Linear API.

## `error_exit_code`

**Required** Exit code to use when an error occurs. Default: 1. This can be set to 0 to make action pass even if label 
couldn't be set. Please check the stdout to see what went wrong.

## Example usage

uses: actions/update-linear-labels-action@v1
with:
  label_name: "Backend"
  branch_name: "${{ github.head_ref }}"
  linear_token: "${{ secrets.LINEAR_TOKEN }}"
  error_exit_code: 0

# Archived JSON Fixtures (PoC)

These JSON files are archived from the original Proof of Concept (PoC) implementation. They were previously used as the primary data store before the application transitioned to a database-backed solution.

**Note:** These files are kept for historical reference only. The application no longer reads from this location by default.

## Files

| File | Description |
|------|-------------|
| `incomes.json` | Sample income records from the PoC |
| `expenses.json` | Sample expense records from the PoC |

## Checksums (SHA256)

```
43d56a3bf2bdad30b86e418bb9e231b36860bf5a1c6bd1cabdfbe673eafc2a57  incomes.json
de78a246e908c026eb076d245b3789c8ea653c10032b32607e7e7dda942f56aa  expenses.json
```

To verify the integrity of these files, run:

```bash
sha256sum -c <<< "43d56a3bf2bdad30b86e418bb9e231b36860bf5a1c6bd1cabdfbe673eafc2a57  incomes.json
de78a246e908c026eb076d245b3789c8ea653c10032b32607e7e7dda942f56aa  expenses.json"
```

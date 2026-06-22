# nasim — Anti-Patterns Registry

Patterns observed in the reference corpus that nasim must not replicate.
Each entry is a lesson learned from studying 28 reference agents.

---

## AP-01 — Never silently remove UC IDs from the inventory

If a UC is deleted, add a `DEPRECATED` tombstone row with the old ID and a one-line
description of what it was and why it was removed. UC IDs are permanent identifiers.
The AGT-05 gap (inventory jump from AGT-04 to AGT-06) was caused by a silent removal.

**Rule:** Every UC ID is either active or has a DEPRECATED tombstone. No gaps in numbering.

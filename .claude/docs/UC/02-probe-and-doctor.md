# UC-02: Doctor / Probe / Status for remote Ollama endpoint (any transport)

**Goal:** At any time (before or after select), user or CI can run `nasim doctor` (or `nasim status --probe`) to verify that the currently configured (or chosen) remote Ollama on black is reachable over the private path, list models, confirm GPU residency on black, and report the effective base URL + which transport is "active".

This UC is used heavily by the test harness for "test it then go ahead".

(Details abbreviated for sprint bootstrap; full would mirror UC-01 success/failure + integration with the modular probe function in the nasim script.)

See implementation in enhanced nasim bin (probe function + status command) and tests that call it for every matrix cell.

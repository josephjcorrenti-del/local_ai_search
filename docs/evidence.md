local_search
  owns retrieval, indexing, artifacts, and evidence generation

local-ai-search inspect-evidence PATH
  calls: local-search evidence PATH --limit N --max-chars N
  validates retrieval_version and required fields
  enforces bounded evidence character count
  formats evidence for inspection
  logs evidence.inspect lifecycle events
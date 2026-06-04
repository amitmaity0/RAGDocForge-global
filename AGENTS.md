This repository contains an enterprise-grade Oracle EBS agentic support platform.

Prioritize:
- scalable architecture
- modular service boundaries
- observability
- deterministic orchestration
- security-first tool execution
- maintainability
- production readiness

Never generate simplistic demo-style implementations.

All implementations should:
- support future multi-agent orchestration
- support enterprise RBAC
- support observability/tracing
- support async execution
- support extensibility

Prefer:
- typed interfaces
- layered architecture
- domain-driven design
- dependency injection
- explicit contracts
- service isolation

Avoid:
- monolithic files
- tightly coupled logic
- hardcoded prompts
- inline SQL
- implicit state handling
- noisy retrieval metadata
- document-level Oracle objects copied into every chunk as chunk-local metadata

Metadata quality rules:
- prefer omission over false-positive Oracle object metadata
- keep document-level and chunk-level retrieval metadata separate
- preserve confidence/evidence for extracted Oracle objects
- cap quality scores when blocking issues or low metadata confidence exist
- keep markdown YAML front matter compact and put full metadata in sidecar exports
- extract PL/SQL functions only from strong signatures, not prose labels such as "Function Err Message"
- split error metadata into clean error codes and source context lines
- keep chunk JSONL compact by referencing `metadata_sidecar.json#{doc_id}` for full document-level metadata
- mark generic reference/community chunks low priority unless they contain local objects, error codes, SQL blocks, or action-oriented troubleshooting evidence
- keep LLM suggested-section grounding fields aligned with source evidence and SME confirmation needs
- keep Hugging Face Spaces startup lightweight and compatible with root `app.py`
- keep public demo mode safe by default: no required API keys, no external LLM calls unless explicitly selected, and clear privacy warnings
- enforce upload limits and sanitized filenames before parsing
- keep ZIP exports under `ragdocforge_outputs/` with `README_OUTPUTS.md`
- preserve bundled examples and `demo_outputs/` as non-confidential public-demo assets
- do not add embeddings, vector DBs, RAG chatbots, auth, persistent DBs, or heavy ML dependencies in packaging/demo slices

When uncertain:
- propose architecture first
- implementation second.

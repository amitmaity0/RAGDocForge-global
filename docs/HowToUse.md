# RAGDocForge User Guide

> **Professional Usage Guide**
>
> This guide explains how to use **RAGDocForge** to analyze enterprise
> documents, evaluate RAG readiness, generate governed knowledge packs,
> and validate them for production use.

------------------------------------------------------------------------

## Overview

RAGDocForge transforms enterprise documentation into structured,
retrieval-ready knowledge assets. The workflow is designed to be
deterministic, auditable, and suitable for enterprise AI platforms.

## End-to-End Workflow

``` mermaid
flowchart LR
    A[Upload Documents]
    -->B[Analyze]
    -->C[Review Results]
    -->D[Generate Knowledge Pack]
    -->E[Run Quality Gates]
    -->F[Export Approved Package]
```

------------------------------------------------------------------------

## Guide Contents

The remainder of this document contains the detailed operational
instructions, commands, validation procedures, and production
recommendations.

------------------------------------------------------------------------

# RAGDocForge Phase 9 Review and Live/Production Test Plan

I reviewed the `Phase9—QualityGatesandCIforKnowledgePacks` branch. The
implementation now looks like a full governed knowledge-pack pipeline,
not just a document converter. The README describes the current app as a
Gradio/Python toolkit that produces governed ERP retrieval assets with
metadata enrichment, retrieval simulation, SQL/PLSQL safety,
review/approval, platform integration packaging, and policy-as-code
quality gates.

## Current Capability Snapshot

  -------------------------------------------------------------------------------
  Area                    Status                  What to Test
  ----------------------- ----------------------- -------------------------------
  Document processing     Implemented             PDF/DOCX/MD/TXT/SQL/PLSQL
                                                  upload and parse

  ERP metadata enrichment Implemented             Modules, processes, objects,
                                                  error codes, ERP concepts

  Platform pack export    Implemented             platform/ artifacts and
                                                  platform_payload_preview.json

  Retrieval QA            Implemented             Hit@1/3/5, failed queries,
                                                  risky chunks

  SQL/PLSQL intelligence  Implemented             binds, safety, purpose,
                                                  entrypoints

  Human review            Implemented             queue, decisions, approved pack

  Platform integration    Implemented             file pack, API preview, guarded
  export                                          push

  Quality gates and CI    Implemented             profiles, CLI validation, batch
                                                  validation, baseline comparison
  -------------------------------------------------------------------------------

The exported ZIP contract is now large and production-like. It includes
`platform/`, `erp/`, `retrieval_qa/`, `sql_intelligence/`, `review/`,
`approved_pack/`, `platform_integration/`, and `quality_gates/` folders
under `ragdocforge_outputs/`.

------------------------------------------------------------------------

# 1. Local Setup Test

Run this first on a clean machine or clean virtual environment.

    git clone -b 'Phase9—QualityGatesandCIforKnowledgePacks' https://github.com/amitmaity0/RAGDocForge.git
    cd RAGDocForge

    python3.11 -m venv .venv
    source .venv/bin/activate

    pip install -r requirements.txt
    python -m pytest -q
    python scripts/verify_spaces_ready.py
    python scripts/verify_ci_config.py

The README explicitly lists Python 3.10/3.11 as supported and says
deterministic processing/tests do not require an external LLM, Ollama,
vector store, or API credentials.

Expected result:

    pytest passes
    verify_spaces_ready passes
    verify_ci_config passes

------------------------------------------------------------------------

# 2. Offline Sample Pack Test

This is the safest production-readiness smoke test because it uses the
deterministic bundled sample and does not require live services.

    rm -rf /tmp/ragdocforge_sample_outputs /tmp/gate_result.json /tmp/gate_report.md /tmp/ci_summary.md

    python scripts/build_sample_knowledge_pack.py \
      --output-dir /tmp/ragdocforge_sample_outputs \
      --profile standard \
      --llm-provider disabled

    python -m ragdocforge.cli validate-pack /tmp/ragdocforge_sample_outputs \
      --profile standard \
      --json-output /tmp/gate_result.json \
      --markdown-output /tmp/gate_report.md \
      --ci-summary-output /tmp/ci_summary.md

The sample builder is deterministic and offline. It uses bundled sample
content, disables external LLM by default, builds markdown, chunks,
metadata, retrieval QA, SQL intelligence, review artifacts, platform
pack, and manifest outputs.

Inspect:

    cat /tmp/ci_summary.md
    jq '.status, .profile_name, .metrics' /tmp/gate_result.json

Expected result for `standard`:

    pass
    or
    pass_with_warnings

A `fail` means the standard internal-quality contract is not currently
satisfied.

------------------------------------------------------------------------

# 3. CI Wrapper Test

Run the same wrapper used by GitHub Actions.

    QUALITY_GATE_PROFILE=experimental bash scripts/run_ci_quality_gates.sh
    QUALITY_GATE_PROFILE=standard bash scripts/run_ci_quality_gates.sh

The wrapper builds the bundled sample with LLM disabled and then calls
`validate-pack`; for the `standard` profile, it also applies
`baselines/sample_pack_quality_baseline.json`.

For strict enterprise:

    QUALITY_GATE_PROFILE=strict_enterprise bash scripts/run_ci_quality_gates.sh

Strict may fail until the sample has a fully approved enterprise-style
pack. That is expected behavior according to the CI documentation.

------------------------------------------------------------------------

# 4. Gradio End-to-End Test

Start the app with safe defaults.

    export RAGDOCFORGE_PUBLIC_DEMO_MODE=false
    export RAGDOCFORGE_LLM_PROVIDER=disabled
    export RAGDOCFORGE_PLATFORM_PUSH_ENABLED=false
    export RAGDOCFORGE_ALLOW_OLLAMA_PULL=false
    export RAGDOCFORGE_ALLOW_OLLAMA_DELETE=false

    python app.py

The README lists these as safe defaults, including LLM disabled,
platform push disabled, and Ollama mutation operations disabled.

In the UI:

1.  Click **Load All Samples**.
2.  Set:

-   ERP module: `GL`
-   Business process: `Journal Import`
-   Export target: `erp_agentic_platform`
-   Quality gate profile: `standard`
-   LLM provider: `disabled`

3.  Click **Analyze**.
4.  Inspect these tabs:

-   **Document Analysis**
-   **Platform Pack**
-   **Retrieval QA**
-   **SQL/PLSQL Intelligence**
-   **Human Review**
-   **Quality Gates**
-   **Export**

The UI tabs are documented in the README, including Platform Pack,
Quality Gates, ERP Coverage, Platform Integration, Retrieval QA,
SQL/PLSQL Intelligence, Human Review, Model Registry, Ollama Service,
and Export.

Download `all_outputs.zip`, unzip it, and validate it:

    mkdir -p /tmp/ragdocforge_live_test
    unzip -q ~/Downloads/all_outputs.zip -d /tmp/ragdocforge_live_test

    python -m ragdocforge.cli validate-pack /tmp/ragdocforge_live_test/ragdocforge_outputs \
      --profile standard \
      --json-output /tmp/live_gate_result.json \
      --markdown-output /tmp/live_gate_report.md \
      --ci-summary-output /tmp/live_ci_summary.md

    cat /tmp/live_ci_summary.md

------------------------------------------------------------------------

# 5. What to Inspect in the ZIP

After any production-like run, verify these files exist:

    ragdocforge_outputs/
      manifest.json
      chunks.jsonl
      quality_report.json
      metadata_sidecar.json

      platform/
        knowledge_pack_manifest.json
        platform_payload_preview.json
        evidence_catalog.json
        ingestion_profile.yaml

      retrieval_qa/
        retrieval_quality_report.json
        chunk_quality_report.json

      sql_intelligence/
        sql_intelligence_report.json
        sql_safety_report.json

      review/
        review_queue.json
        approval_report.json

      approved_pack/
        approved_knowledge_manifest.json

      platform_integration/
        platform_ingestion_payload.jsonl
        platform_validation_result.json

      quality_gates/
        quality_gate_result.json
        quality_gate_report.md
        ci_summary.md

This matches the current documented export contract.

Run quick checks:

    jq '.phase9_quality_gates_enabled, .quality_gate_status, .quality_gate_profile' \
      /tmp/ragdocforge_live_test/ragdocforge_outputs/manifest.json

    jq '.status, .metrics, .findings | length' \
      /tmp/ragdocforge_live_test/ragdocforge_outputs/quality_gates/quality_gate_result.json

    head -n 3 /tmp/ragdocforge_live_test/ragdocforge_outputs/chunks.jsonl

------------------------------------------------------------------------

# 6. Quality Gate Profile Testing

Use all three profiles deliberately.

## Experimental

Use for incomplete packs and exploratory testing.

    python -m ragdocforge.cli validate-pack ./ragdocforge_outputs \
      --profile experimental

Experimental requires only `manifest.json` and `chunks.jsonl`
structurally, and has permissive thresholds.

## Standard

Use for normal internal QA.

    python -m ragdocforge.cli validate-pack ./ragdocforge_outputs \
      --profile standard \
      --warnings-as-errors

Standard requires core artifacts plus platform and retrieval QA outputs,
including `quality_report.json`, `metadata_sidecar.json`,
`chunks.jsonl`, `platform/knowledge_pack_manifest.json`,
`platform/platform_payload_preview.json`,
`platform/evidence_catalog.json`, and
`retrieval_qa/retrieval_quality_report.json`.

## Strict Enterprise

Use only after SME approval and approved-pack export.

    python -m ragdocforge.cli validate-pack ./ragdocforge_outputs \
      --profile strict_enterprise \
      --warnings-as-errors

Strict requires all standard artifacts plus ingestion profile, chunk QA,
SQL intelligence, review approval report, and approved knowledge
manifest.

------------------------------------------------------------------------

# 7. Baseline Regression Testing

Once you have a reviewed pack that you trust, create a baseline:

    python -m ragdocforge.cli create-baseline ./ragdocforge_outputs \
      --profile standard \
      --output baselines/gl_journal_import_standard.json

Then validate future packs against it:

    python -m ragdocforge.cli validate-pack ./ragdocforge_outputs \
      --profile standard \
      --baseline baselines/gl_journal_import_standard.json \
      --json-output ./gate_result.json \
      --markdown-output ./gate_report.md \
      --ci-summary-output ./ci_summary.md

Baselines detect regressions even when policy thresholds still pass;
tracked metrics include quality score, metadata confidence, Hit@3/Hit@5,
metadata filter accuracy, unsupported answer risk, approval-required SQL
without review, not-for-agent-execution count, and blocking issues.

Do not update baselines just to make CI green. The docs explicitly
recommend reviewing every regression and committing baseline changes
only with evidence-backed approval.

------------------------------------------------------------------------

# 8. Batch Validation Test

Use this when you start producing multiple packs by module or process.

    mkdir -p /tmp/packs
    cp -R /tmp/ragdocforge_live_test/ragdocforge_outputs /tmp/packs/gl_journal_import

    python -m ragdocforge.cli validate-packs /tmp/packs \
      --profile standard \
      --output-dir /tmp/gate_reports \
      --json-output /tmp/aggregate_gate_result.json \
      --markdown-output /tmp/aggregate_gate_report.md

The batch command validates each qualifying child pack independently and
writes per-pack and aggregate reports.

------------------------------------------------------------------------

# 9. GitHub Actions Production Readiness

The branch includes a GitHub Actions workflow named `RAGDocForge CI`. It
runs `pytest`, then a quality-gate matrix on Python `3.10` and `3.11`
for `experimental` and `standard` profiles. Manual dispatch supports
`strict_enterprise`.

The workflow uploads artifacts named like:

    quality-gate-3.10-experimental
    quality-gate-3.10-standard
    quality-gate-3.11-experimental
    quality-gate-3.11-standard

and includes `gate_result.json`, `gate_report.md`, `ci_summary.md`, and
`/tmp/ragdocforge_sample_outputs`.

To test CI:

1.  Open a PR from the Phase 9 branch into `main`.
2.  Verify the `tests` job passes.
3.  Verify all standard/experimental matrix legs pass.
4.  Download at least one artifact and inspect `gate_report.md`.
5.  Manually dispatch `strict_enterprise` and confirm expected strict
    findings.

------------------------------------------------------------------------

# 10. Optional Ollama / LLM Live Test

Use this only on a private/local environment.

    export RAGDOCFORGE_LLM_PROVIDER=ollama
    export RAGDOCFORGE_OLLAMA_BASE_URL=http://localhost:11434
    export RAGDOCFORGE_OLLAMA_MODEL=qwen2.5:7b
    python app.py

The README documents local Ollama settings and makes clear that model
output is advisory, while deterministic extraction, SQL safety
classification, quality metrics, and human decisions remain
authoritative.

Recommended live test:

    python -m ragdocforge.cli ollama health --profile default --json
    python -m ragdocforge.cli ollama models --profile default --json
    python -m ragdocforge.cli ollama probe --profile default --model qwen2.5:7b --json

Then run Gradio with:

-   LLM enabled
-   Ollama provider
-   Manual or registry-based task routing
-   Quality gate profile: `standard`

Validate that LLM suggestions appear but remain review items, not
automatically approved content.

------------------------------------------------------------------------

# 11. Platform Integration Dry Run

For production-like testing, stay in file-pack or dry-run mode first.

    python -m ragdocforge.cli export-platform-integration \
      --platform-pack-dir ./ragdocforge_outputs/platform \
      --retrieval-qa-dir ./ragdocforge_outputs/retrieval_qa \
      --output-dir ./platform_integration_test \
      --mode file_pack

    python -m ragdocforge.cli validate-platform-integration \
      --integration-dir ./platform_integration_test

The CLI has `export-platform-integration`,
`validate-platform-integration`, and `platform-health` commands.

Do not test direct push as "production" until these are true:

    standard profile passes
    strict profile reviewed or expected findings accepted
    approval-required SQL is reviewed
    approved_pack exists
    platform validation result passes
    dry-run API push preview passes
    RAGDOCFORGE_PLATFORM_PUSH_ENABLED=true is intentionally set

The README states direct push is disabled by default and governed by
dry-run, confirmation, public-demo, review, and configuration
guardrails.

------------------------------------------------------------------------

# 12. Production Acceptance Checklist

Use this before calling a pack production-ready.

  -----------------------------------------------------------------------
  Check                               Required for Production
  ----------------------------------- -----------------------------------
  pytest passes                       Yes

  verify_ci_config.py passes          Yes

  Gradio sample run succeeds          Yes

  Real private document run succeeds  Yes

  ZIP contains all expected folders   Yes

  validate-pack --profile standard    Recommended
  --warnings-as-errors passes         

  validate-pack --profile             For governed release
  strict_enterprise passes            

  Retrieval QA Hit@5 meets policy     Yes

  No not_for_agent_execution chunks   Yes

  No approval-required SQL without    Yes
  review                              

  Review queue has no pending         Yes
  critical items                      

  Approved pack exists                For strict

  Baseline comparison passes          For regression-controlled release

  Platform integration validation     Yes
  passes                              

  Direct push remains disabled unless Yes
  explicitly approved                 
  -----------------------------------------------------------------------

The strict and standard profile thresholds are defined in
`configs/knowledge_pack_quality_gates.yaml`, including quality score,
metadata confidence, Hit@3/Hit@5, metadata filter accuracy, unsupported
answer risk, tiny/duplicate chunk ratio, SQL safety, and review
requirements.

------------------------------------------------------------------------

# 13. My Recommended Live Test Sequence

Run this exact order:

    # 1. Repository verification
    python -m pytest -q
    python scripts/verify_spaces_ready.py
    python scripts/verify_ci_config.py

    # 2. Deterministic sample
    python scripts/build_sample_knowledge_pack.py \
      --output-dir /tmp/ragdocforge_sample_outputs \
      --profile standard \
      --llm-provider disabled

    # 3. Validate sample
    python -m ragdocforge.cli validate-pack /tmp/ragdocforge_sample_outputs \
      --profile standard \
      --json-output /tmp/gate_result.json \
      --markdown-output /tmp/gate_report.md \
      --ci-summary-output /tmp/ci_summary.md

    # 4. CI wrapper
    QUALITY_GATE_PROFILE=standard bash scripts/run_ci_quality_gates.sh

    # 5. Gradio live run
    python app.py

    # 6. Validate downloaded ZIP output
    python -m ragdocforge.cli validate-pack ./ragdocforge_outputs \
      --profile standard \
      --warnings-as-errors

After that, test one real private EBS document set locally with
`LLM_PROVIDER=disabled`. Only after deterministic outputs look good
should you enable Ollama or OpenAI-compatible assistance.

------------------------------------------------------------------------

# 14. Important Boundary

RAGDocForge is production-useful as a **knowledge-pack preparation and
validation tool**, not as a live ERP agent or vector ingestion service.
The README explicitly states it does not execute SQL, connect to ERP
databases, create embeddings, write to a vector database, or provide a
production RAG chatbot.

That boundary is good. For your `erp_agentic_platform`, RAGDocForge
should be the governed upstream factory:

    EBS docs → RAGDocForge analysis → approved knowledge pack → quality gate → platform ingestion

Do not bypass the review, SQL-safety, retrieval QA, and quality-gate
layers for "live" testing.

# For your ERP Agentic Platform architecture, I would simplify it like this

Your final architecture should be:

    flowchart LR

    A[EBS Documents] --> B[RAGDocForge Gradio]

    B --> C[Knowledge Pack Generation]

    C --> D[Quality Gate Engine]

    D --> E{Pass?}

    E -->|No| F[SME Review / Fix Content]

    E -->|Yes| G[Approved Knowledge Pack]

    G --> H[ERP Agentic Platform Ingestion]

    H --> I[Qdrant / Vector Store]

    H --> J[Agent Runtime]

------------------------------------------------------------------------

# One improvement Needed For Future

Currently you have duplicate validation paths:

    Gradio Analyze
            |
            v
    Quality Gate

    CLI validate-pack
            |
            v
    Quality Gate

That is okay, but I would expose the CLI functionality inside the UI:

Add a button:

    Quality Gate

    [Run Validation Again]
    [Compare Against Baseline]
    [Generate Release Report]

Then the SME workflow becomes:

    Analyze
     ↓
    Review Findings
     ↓
    Approve
     ↓
    Run Release Gate
     ↓
    Export Approved Pack

No terminal required.

------------------------------------------------------------------------

# Best Practices

-   Prefer **deterministic mode** for production knowledge packs.
-   Enable LLM-assisted analysis only for qualitative recommendations.
-   Always review SQL safety findings before approving a pack.
-   Validate exported packages using the appropriate Quality Gate
    profile.
-   Establish and maintain baselines for regression detection.
-   Treat approved knowledge packs as immutable release artifacts.

------------------------------------------------------------------------

# Recommended Production Workflow

``` text
Enterprise Documents
        │
        ▼
RAGDocForge Analysis
        │
        ▼
Quality Gate Validation
        │
        ▼
SME Review & Approval
        │
        ▼
Approved Knowledge Pack
        │
        ▼
ERP Agentic Platform
```

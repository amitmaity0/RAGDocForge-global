# Chapter 06 --- Installation, Validation & Production Workflow

> Enterprise Documentation Series

This chapter expands the installation and operational guidance using the
current Phase 9 production workflow. It is based on the project's
implementation guide and reorganized into a user-focused handbook.
Source reference: fileciteturn2file0

------------------------------------------------------------------------

# Who Should Read This

-   Platform Administrators
-   Oracle EBS Support Engineers
-   DevOps Engineers
-   Knowledge Engineers

------------------------------------------------------------------------

# Installation Workflow

## 1. Clone the repository

``` bash
git clone <repository>
cd RAGDocForge
```

## 2. Create a Python virtual environment

``` bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Verify the installation

Run:

``` bash
pytest -q
python scripts/verify_spaces_ready.py
python scripts/verify_ci_config.py
```

All verification steps should pass before processing enterprise
documents.

------------------------------------------------------------------------

# Recommended Enterprise Workflow

``` text
Prepare Documents
        ↓
Analyze in Gradio
        ↓
Review Findings
        ↓
Run Quality Gates
        ↓
Approve Knowledge Pack
        ↓
Export
        ↓
Deploy to ERP Agentic Platform
```

------------------------------------------------------------------------

# Enterprise Validation Matrix

  ------------------------------------------------------------------------
  Stage          Objective              Expected Result
  -------------- ---------------------- ----------------------------------
  Environment    Verify installation    All verification scripts pass
  Validation                            

  Sample Pack    Confirm deterministic  PASS or PASS WITH WARNINGS
                 processing             

  Real Document  Validate enterprise    Successful knowledge pack
  Analysis       documents              

  Quality Gate   Validate release       Meets selected profile
                 readiness              

  Human Review   SME approval           Approved pack

  Platform       Generate deployment    Platform package created
  Export         artifacts              
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# Oracle EBS Example --- General Ledger Journal Import

## Recommended Source Documents

-   Functional Design
-   Technical Design
-   Journal Import Guide
-   Interface Table Documentation
-   Error Resolution Guide
-   SQL Validation Scripts

### Recommended Metadata

  Field                Example
  -------------------- -----------------------------
  Module               General Ledger
  Process              Journal Import
  Tables               GL_INTERFACE, GL_JE_HEADERS
  Concurrent Program   Journal Import
  Version              Oracle EBS 12.2.x

------------------------------------------------------------------------

# Production Readiness Checklist

-   Environment verified
-   Sample knowledge pack generated
-   Quality Gate passed
-   Retrieval QA reviewed
-   SQL findings reviewed
-   Human approval completed
-   Export validated
-   Platform integration verified

------------------------------------------------------------------------

# Best Practices

-   Validate every knowledge pack before release.
-   Keep SQL scripts separate from procedural documentation.
-   Organize documents by business process rather than by project.
-   Treat the approved knowledge pack as a versioned release artifact.
-   Use the Standard profile during development and Strict Enterprise
    for governed releases.

------------------------------------------------------------------------

# CLI Operations

The project provides command-line validation, sample pack generation,
batch validation, baseline comparison, and platform integration
commands. Use the CLI in CI/CD pipelines, while business users can
perform the same lifecycle through the Gradio interface where available.
fileciteturn2file0

------------------------------------------------------------------------

# Practical Recommendation

For day-to-day work, the preferred workflow is:

1.  Load enterprise documents in the Gradio UI.
2.  Analyze and review findings.
3.  Resolve quality issues.
4.  Run Quality Gates.
5.  Approve the knowledge pack.
6.  Export the approved package.
7.  Deploy into the ERP Agentic Platform.

This minimizes manual command-line work while preserving governance.

------------------------------------------------------------------------

# Appendix

The original implementation guide contains detailed command examples
for: - Offline sample pack generation - Batch validation - Baseline
regression testing - GitHub Actions validation - Ollama integration -
Platform integration dry-run - Production acceptance criteria

Refer to the original guide for the complete command reference.
fileciteturn2file0

## Next Chapter

**Chapter 07 --- Gradio User Interface Walkthrough**

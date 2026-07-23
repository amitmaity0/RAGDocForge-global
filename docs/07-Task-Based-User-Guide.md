# Chapter 07 --- Task-Based User Guide

> **Enterprise Documentation Series**

This chapter teaches users how to accomplish common tasks in
RAGDocForge. Rather than describing every screen, it follows real
enterprise workflows.

------------------------------------------------------------------------

# Typical User Journey

``` text
Prepare Documents
      ↓
Upload Files
      ↓
Analyze
      ↓
Review Findings
      ↓
Run Quality Gates
      ↓
Approve
      ↓
Export Knowledge Pack
```

------------------------------------------------------------------------

# Scenario 1 --- Analyze an Oracle GL Interface Guide

## Objective

Prepare General Ledger implementation documentation for an ERP Agentic
AI Platform.

### Recommended Inputs

  Document                          Required
  ------------------------------- -------------
  Functional Design                    ✅
  Technical Design                     ✅
  Interface Table Documentation        ✅
  SQL Validation Scripts           Recommended
  Troubleshooting Guide            Recommended
  Error Catalog                    Recommended

### Steps

1.  Open the Gradio application.
2.  Upload all related documents together.
3.  Select:
    -   ERP Module: **General Ledger**
    -   Business Process: **Journal Import**
    -   Quality Profile: **Standard**
4.  Click **Analyze**.
5.  Review metadata, retrieval QA, SQL Intelligence, and Quality Gates.
6.  Export the approved knowledge pack.

### Expected Outputs

-   Structured Markdown
-   Retrieval-ready chunks
-   ERP metadata
-   SQL intelligence reports
-   Quality reports
-   Platform integration package

------------------------------------------------------------------------

# Scenario 2 --- Review SQL Intelligence

Use SQL Intelligence to verify database artifacts.

Review for:

-   Table names
-   Packages
-   Procedures
-   Views
-   Bind variables
-   Safety classifications

## Best Practice

Treat SQL findings as engineering evidence requiring SME review before
release.

------------------------------------------------------------------------

# Scenario 3 --- Run Quality Gates

Quality Gates determine whether a knowledge pack is ready for
production.

Recommended workflow:

1.  Review warnings.
2.  Correct documentation issues.
3.  Re-run validation.
4.  Approve only when policy requirements are satisfied.

------------------------------------------------------------------------

# Scenario 4 --- Export an Approved Knowledge Pack

Before exporting, verify:

  Check                   Status
  ----------------------- --------
  Metadata complete       ✓
  Retrieval QA reviewed   ✓
  Human review complete   ✓
  Quality Gate passed     ✓

Export only approved packs into downstream AI platforms.

------------------------------------------------------------------------

# Common Mistakes

  -----------------------------------------------------------------------
  Mistake                    Better Practice
  -------------------------- --------------------------------------------
  Upload unrelated projects  Keep one business process per analysis
  together                   

  Mix functional and         Use current, authoritative sources
  obsolete documentation     

  Ignore retrieval warnings  Improve document structure first

  Skip SME review            Require approval for production packs
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Enterprise Tips

-   Analyze documentation by Oracle module.
-   Keep implementation guides, SOPs, and SQL scripts organized.
-   Version approved knowledge packs alongside application releases.
-   Maintain a baseline for critical business processes such as Journal
    Import or AutoInvoice.

------------------------------------------------------------------------

# Daily Workflow Checklist

-   Environment ready
-   Documents organized
-   Analysis completed
-   Findings reviewed
-   Quality Gates passed
-   Knowledge Pack exported

------------------------------------------------------------------------

# Next Chapter

**Chapter 08 --- Preparing Enterprise Documentation for AI**

Learn how to transform Oracle EBS implementation guides, SOPs, runbooks,
and legacy documentation into high-quality retrieval-ready knowledge.

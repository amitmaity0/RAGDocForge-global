---
app_file: app.py
colorFrom: blue
colorTo: indigo
emoji: 📄
license: apache-2.0
pinned: false
sdk: gradio
sdk_version: 5.0.0
title: RAGDocForge
---

::: {align="center"}
# 📄 RAGDocForge

### Enterprise Document Preparation Toolkit for Retrieval-Augmented Generation (RAG)

Transform enterprise documents into **production-ready knowledge packs**
with deterministic parsing, Oracle EBS intelligence, quality scoring,
retrieval validation, and governed export.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gradio](https://img.shields.io/badge/Gradio-5.x-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-green)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Pack-indigo)
:::

------------------------------------------------------------------------

# Overview

RAGDocForge is an enterprise-grade document preparation toolkit that
converts business and technical documentation into structured,
retrieval-optimized knowledge assets for Retrieval-Augmented Generation
(RAG).

Unlike traditional document converters, RAGDocForge performs
deterministic parsing, Oracle EBS-aware metadata extraction, SQL &
PL/SQL intelligence, document quality analysis, chunk optimization, and
governed knowledge-pack generation.

It is designed for enterprise support organizations, solution
architects, and Agentic AI platforms that require trustworthy,
repeatable, and auditable knowledge preparation pipelines.

------------------------------------------------------------------------

# ✨ Key Features

-   📄 Multi-format document ingestion
-   🏛 Oracle EBS metadata extraction
-   🧠 SQL & PL/SQL intelligence
-   📊 RAG Readiness scoring
-   🧩 Intelligent chunk generation
-   📝 Markdown normalization
-   🤖 Optional LLM-assisted qualitative review
-   🔍 Retrieval quality simulation
-   📦 Governed Knowledge Pack export
-   ✅ Quality Gates & CI validation
-   🌐 Hugging Face Spaces ready

------------------------------------------------------------------------

# Supported File Types

  Format     Supported
  ---------- -----------
  PDF        ✅
  DOCX       ✅
  Markdown   ✅
  TXT        ✅
  SQL        ✅
  PL/SQL     ✅

------------------------------------------------------------------------

# Architecture

``` mermaid
flowchart LR

A[Enterprise Documents]
-->B[Deterministic Parsing]
-->C[Metadata Extraction]
-->D[RAG Readiness]
-->E[Chunk Generation]
-->F[Knowledge Pack]
-->G[Quality Gates]
-->H[Platform Export]
```

------------------------------------------------------------------------

# Quick Start

## Clone Repository

``` bash
git clone https://github.com/<your-org>/RAGDocForge.git
cd RAGDocForge
```

## Create Virtual Environment

``` bash
python -m venv .venv
source .venv/bin/activate
```

## Install

``` bash
pip install -r requirements.txt
```

## Launch

``` bash
python app.py
```

------------------------------------------------------------------------

# Run Tests

``` bash
python -m pytest -q
python scripts/verify_spaces_ready.py
```

------------------------------------------------------------------------

# Configuration

  -----------------------------------------------------------------------
  Environment Variable                         Description
  -------------------------------------------- --------------------------
  `RAGDOCFORGE_LLM_PROVIDER`                   disabled, mock, ollama,
                                               openai_compatible

  `RAGDOCFORGE_PUBLIC_DEMO_MODE`               Enable public demo
                                               safeguards

  `RAGDOCFORGE_OLLAMA_BASE_URL`                Local Ollama endpoint

  `RAGDOCFORGE_OLLAMA_MODEL`                   Local model

  `RAGDOCFORGE_OPENAI_BASE_URL`                OpenAI-compatible endpoint

  `RAGDOCFORGE_OPENAI_MODEL`                   Remote model
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Privacy

> **Never upload confidential enterprise documents to a public
> deployment.**

For sensitive workloads, deploy locally or within a private environment.
When LLM-assisted analysis is enabled, document content may be
transmitted to the configured provider.

------------------------------------------------------------------------

# Sample Workflow

1.  Upload one or more documents.
2.  Extract Oracle EBS metadata.
3.  Generate normalized Markdown.
4.  Produce retrieval-ready JSONL chunks.
5.  Evaluate RAG readiness.
6.  Export a governed Knowledge Pack.

------------------------------------------------------------------------

# Output Structure

``` text
ragdocforge_outputs/
├── markdown/
├── chunks.jsonl
├── metadata_sidecar.json
├── quality_report.json
├── llm_analysis_report.json
├── manifest.json
├── README_OUTPUTS.md
└── suggested_sections.md
```

------------------------------------------------------------------------

# Public Demo Mode

``` bash
RAGDOCFORGE_PUBLIC_DEMO_MODE=true
```

Features include:

-   Privacy banner
-   Safe default LLM provider
-   Hidden API keys
-   Upload limits
-   No persistent document storage
-   Sanitized logging

------------------------------------------------------------------------
## 📚 Documentation

Comprehensive documentation is available in the **docs** directory.

➡️ **[Open the Documentation Home](docs/README.md)**

The documentation covers:

- Getting Started
- Enterprise Workflows
- Oracle EBS Examples
- AI-Ready Documentation
- Knowledge Pack Engineering
- Production Best Practices
- Governance
------------------------------------------------------------------------

# Current Limitations

-   OCR not yet supported
-   No embedding generation
-   No vector database ingestion
-   No chatbot interface
-   PDF quality depends on embedded text
-   Human review recommended for LLM suggestions

------------------------------------------------------------------------

# Roadmap

-   [x] Deterministic parsing
-   [x] Oracle EBS intelligence
-   [x] SQL & PL/SQL analysis
-   [x] Quality Gates
-   [x] Knowledge Pack export
-   [ ] OCR support
-   [ ] Embedding generation
-   [ ] Vector database connectors
-   [ ] Enterprise REST API
-   [ ] Knowledge Pack Registry

------------------------------------------------------------------------

# Contributing

Contributions, issues, and feature requests are welcome. Please open an
issue before submitting significant changes.

------------------------------------------------------------------------

# License

Licensed under the Apache License 2.0.

------------------------------------------------------------------------

::: {align="center"}
**Built for Enterprise AI • Oracle EBS • Retrieval-Augmented
Generation**
:::

# contract-costs-automation

Automates contract cost tracking by processing invoices, managing hierarchical cost structures, and generating budget-aware Excel reports.

## Overview

This project is a backend-oriented system for managing **contract-level costs** based on real-world construction workflows.

It supports:
- multi-level cost structures per contract
- budget tracking and comparison (planned vs actual)
- invoice processing with multiple cost positions per document
- manual and automated cost intake
- Excel-based workflows for configuration and reporting

The system is designed with a **clean domain core**, where business logic is independent of storage, Excel, or external services.

## Core Concepts

- **Pending documents** – raw scans or PDFs waiting for processing
- **Contracts** – cost containers with hierarchical cost structures
- **Cost nodes** – arbitrary-depth cost hierarchy (cost estimate structure)
- **Contexts** – budget perspectives (e.g. base contract, additional works)
- **Invoice lines** – individual cost entries derived from invoice positions
- **Global dictionaries** – shared cost types and classifications

## Goals

- Reflect real contract cost control practices
- Keep the core domain simple and explicit
- Avoid ERP-like complexity
- Use Excel as a practical interface, not a database
- Support gradual automation without forcing it

## Status

🚧 Work in progress  
Currently focusing on **domain core implementation**.

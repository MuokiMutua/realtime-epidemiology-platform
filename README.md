# Sentinel-Epi: Geospatial Outbreak Detection Engine
<img width="1744" height="850" alt="image" src="https://github.com/user-attachments/assets/64ca54f1-8adc-4bc1-bca3-361389dc1191" />

An end-to-end spatial data lakehouse and machine learning pipeline built to detect epidemiological anomalies in real-time using Community Health Worker (CHW) telemetry.

## The Problem Statement
Traditional epidemiological surveillance suffers from critical latency. Community health workers collect patient symptom data at the village or clinic level, but this data is often siloed, manually processed, or batched weekly. By the time human analysts aggregate the data and notice a geographic cluster of symptoms (e.g., a cholera spike), the outbreak has already spread, leading to unmanageable epidemics and loss of life within the 48 to 72-hour delay window.

## Objectives
1. **Zero-Latency Ingestion:** Build a gateway capable of handling thousands of asynchronous, concurrent telemetric pings from mobile apps in the field.
2. **Spatial-Temporal Aggregation:** Compress raw patient logs into structured, region-based time-series data without relying on slow, out-of-memory Python transformations.
3. **Automated Anomaly Detection:** Replace hardcoded human thresholds with unsupervised machine learning to detect statistical deviations in symptom rates based on local baselines.
4. **Operational Visibility:** Deploy a real-time, geospatial command center for health officials to track containment zones.

## The Solution
Sentinel-Epi shifts outbreak monitoring from human-in-the-loop querying to machine-driven proactive alerting. The system ingests raw health worker reports, immediately stores them in a spatial data warehouse, dynamically compiles weekly symptom rates using SQL transformations, and runs an Isolation Forest algorithm to flag geographic coordinates that statistically deviate from the national baseline. Results are instantly streamed to a dark-mode, low-latency map interface.

## Technology Stack & Architectural Decisions

* **FastAPI (The Gateway):** Used to build the asynchronous REST API. FastAPI prevents blocking during massive spikes in data ingestion, acting as a highly scalable receiver for CHW mobile applications.
* **PostgreSQL & PostGIS (The Spatial Warehouse):** Standard databases lack native geographic intelligence. By utilizing the PostGIS extension, the database inherently understands geographic coordinates, counties, and sub-counties, allowing for future advanced geospatial querying.
* **dbt - Data Build Tool (The Transformation Engine):** Instead of writing brittle Pandas scripts for data aggregation, dbt is used to write modular SQL. It pushes the compute down into the Postgres database to transform raw event logs into clean, aggregated analytical marts (weekly symptom rates).
* **scikit-learn / Isolation Forest (The AI Underwriter):** An unsupervised machine learning model chosen because disease baselines vary by region. The Isolation Forest does not need to know what a specific disease looks like; it simply isolates geographical data points that behave wildly differently from the historical norm, making it highly robust against shifting data.
* **Streamlit & Plotly (The Command Center):** Used to bypass the need for a heavy frontend JavaScript framework. Streamlit rapidly connects the ML outputs to a live web interface, while Plotly renders the geospatial risk matrix to visualize active containment zones.
* **Docker:** Used to containerize the PostGIS database infrastructure for reproducible, instant deployment across different environments.


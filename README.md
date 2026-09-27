```markdown
# Urban Logistics Risk Intelligence Pipeline

An automated data engineering pipeline orchestrated by **Apache Airflow 3 (Task SDK)** that monitors real-time environmental and infrastructure friction indicators, persists operational telemetry into a **PostgreSQL** warehouse, and generates actionable, AI-driven dispatch advisories using **Google Gemini**.

```

---

## 1. Problem Statement

Last-mile urban delivery fleets operate in unpredictable, dynamic environments. Weather shifts (heavy rain, wind gusts), traffic congestion, hazardous air quality index (AQI) levels, and public holiday volume spikes frequently trigger delivery delays, increase courier safety risks, and frustrate customers.

Most logistics operations react to these issues after delays happen. This pipeline proactively unifies multi-source urban telemetry in real time, validates strict contracts on the incoming data, stores the normalized metrics, and uses an LLM to generate tactical fleet recommendations and customer-facing advisories before deliveries are impacted.

---

## 2. What We Ingest & Store

The system captures multi-source data and persists it across two relational tables:

### `fact_delivery_risks` (Operational Telemetry)

Stores the normalized facts and metrics fetched across the APIs:

* **Spatial & Temporal:** `timestamp_utc`, `city`, `lat`, `lon`
* **Weather (OpenWeatherMap):** `weather_condition`, `temp_c`, `humidity_pct`, `wind_speed_mps`, `wind_gust_mps`, `precipitation_mm`
* **Traffic (TomTom Traffic):** `current_speed_kmh`, `free_flow_speed_kmh`, `delay_pct`, `speed_ratio`, `is_road_closed`, `traffic_confidence`
* **Air Quality (WAQI):** `aqi`, `primary_pollutant`, `pm25_value`
* **Calendar:** `is_holiday`, `holiday_name`

### `delivery_risk_insights` (LLM Dispatch Intelligence)

Stores the structured AI advisories linked directly to the parent fact record via a foreign key (`risk_record_id`):

* **`urgency_level`**: Operational severity (`LOW`, `MODERATE`, `CRITICAL`)
* **`headline`**: Executive summary of current road/weather friction
* **`dispatch_recommendation`**: Concrete fleet directives (e.g., adjust SLA buffers, switch to vans, require courier masks)
* **`customer_advisory`**: Customer-friendly SMS/push notification explaining realistic delivery expectations without technical jargon
* **`structured_output`**: Complete raw JSON payload (`JSONB`)
* **Observability Metadata**: `model_name`, `prompt_tokens`, `completion_tokens`, `total_tokens`, and `execution_duration_ms`

---

## 3. Tech Stack

* **Orchestration**: Apache Airflow 3 (Task SDK / TaskFlow API)
* **Language & Package Manager**: Python 3.13, `uv`
* **Data Contracts & Validation**: Pydantic v2
* **Storage & Warehouse**: PostgreSQL, SQLAlchemy 2.0 ORM
* **LLM Engine**: Google GenAI SDK (`gemini-3.8-flash` with automatic fallback to `gemini-3-flash`)
* **Infrastructure**: Docker & Docker Compose

---

## 4. Setup & Running Locally

### Step 1: Clone & Configure Environment

Create your `.env` file in the project root:

```bash
cp .env.example .env

```

Populate the required keys and settings:

```env
# Google Gemini API
GEMINI_API_KEY="AIzaSy..."

# Telemetry API Keys
TOMTOM_API_KEY="your_tomtom_api_key"
OPENWEATHER_API_KEY="your_openweather_api_key"
WAQI_API_TOKEN="your_waqi_api_token"

# Location (Centroid Coordinates)
DEFAULT_LAT=40.7128
DEFAULT_LON=-74.0060

# Warehouse Credentials
WAREHOUSE_DB=delivery_risk_db
WAREHOUSE_USER=delivery_risk_user
WAREHOUSE_PASSWORD=DeliveryRiskPass123
WAREHOUSE_HOST=localhost
WAREHOUSE_PORT=5433

```

### Step 2: Install Local Dependencies

```bash
uv sync

```

### Step 3: Initialize Database Schema

Start the warehouse PostgreSQL container:

```bash
docker compose up -d warehouse-postgres

```

Run the initialization script to create tables (`fact_delivery_risks` and `delivery_risk_insights`):

```bash
uv run python -m scripts.init_db

```

### Step 4: Launch Airflow

Start the Airflow 3 services:

```bash
docker compose up -d

```

Open the Airflow UI at **`http://localhost:8080`**.

---

## 5. Pipeline Execution Flow

Once you unpause and trigger the `delivery_risk` DAG:

1. **Extraction (Parallel)**:
* `fetch_weather` -> calls OpenWeatherMap API
* `fetch_traffic` -> calls TomTom Traffic API
* `fetch_aqi` -> calls WAQI API
* `fetch_holidays` -> checks public holiday schedules


2. **Contract Validation**: `validate_data` validates all raw payloads against strict Pydantic schemas.
3. **Transformation**: `transform_task` normalizes and merges all metrics into a clean flat schema.
4. **Warehouse Load**: `load_task` inserts the telemetry row into `fact_delivery_risks` and passes downstream the generated record UUID.
5. **AI Insights Generation**: `generate_insights_task` sends the telemetry to Gemini, validates the structured output, measures execution latency/tokens, and persists the advisory into `delivery_risk_insights`.

---

## 6. Verifying Insights

### Query PostgreSQL Directly

Inspect the telemetry and generated advice side-by-side:

```bash
docker compose exec warehouse-postgres psql -U delivery_risk_user -d delivery_risk_db -x -c "
SELECT 
    f.city,
    f.temp_c,
    f.delay_pct,
    f.aqi,
    i.urgency_level,
    i.headline,
    i.dispatch_recommendation,
    i.customer_advisory,
    i.model_name,
    i.execution_duration_ms
FROM fact_delivery_risks f
JOIN delivery_risk_insights i ON f.id = i.risk_record_id
ORDER BY i.created_at DESC
LIMIT 1;
"

```

### In Airflow UI

Click the completed `generate_insights_task` node in the Grid view and check the **Storage / XCom** tab to view the validated JSON payload.

```

```
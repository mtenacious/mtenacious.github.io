# Technical Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CIVIC BRIDGE STACK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Data Layer  │───▶│  ML Pipeline │───▶│  Optimizer   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  PostgreSQL  │    │  Model Store │    │  Solution DB │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│                    ┌──────────────┐                              │
│                    │   REST API   │                              │
│                    └──────────────┘                              │
│                             │                                   │
│                    ┌──────────────┐                              │
│                    │  Dashboard   │                              │
│                    └──────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Data Layer
- **Sources**: Weather APIs, Census Data, Event Calendars, Historical Records
- **Storage**: PostgreSQL 15 with TimescaleDB extension
- **Ingestion**: Apache Kafka for real-time, Airflow for batch

### ML Pipeline
- **Models**: Prophet (seasonality), XGBoost (features), LSTM (sequences)
- **Training**: Daily incremental, weekly full retrain
- **Serving**: TorchServe with model versioning
- **Bias Removal**: Orthogonal projection pre-processing

### Optimizer
- **Solver**: PuLP + CBC (open-source MILP)
- **Problem Formulation**: Multi-objective with fairness constraints
- **Solve Time**: <5s for daily planning, <30s for weekly
- **Reoptimization**: Event-triggered on demand shock

### API Layer
- **Framework**: FastAPI (Python)
- **Auth**: JWT with municipal SSO integration
- **Rate Limiting**: 1000 req/min per municipality
- **Versioning**: URL-based (/api/v1/)

## Hardware Requirements

### Minimum Deployment
- Raspberry Pi 4 (8GB RAM)
- 256GB NVMe SSD
- Ethernet connection
- UPS battery backup

### Recommended Deployment
- Intel NUC 12
- 32GB RAM
- 1TB NVMe SSD
- Redundant power
- 4G failover modem

## Security Model

- All data encrypted at rest (AES-256)
- All API calls over TLS 1.3
- No PII stored in prediction models
- Audit logging for all resource allocations
- Quarterly security reviews

## Monitoring

- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Alerting**: PagerDuty integration
- **Logging**: ELK Stack

---

*The Civic Bridge Initiative — Technical Reference*

# Deployment Runbook

## Prerequisites

- Raspberry Pi 4 (8GB) or equivalent
- Ubuntu Server 22.04 LTS flashed to SD card
- Ethernet connection or WiFi configured
- SSH access enabled

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/civic-bridge.git
cd civic-bridge

# 2. Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Configure your municipality
cp config/example.yaml config/municipality.yaml
nano config/municipality.yaml

# 4. Start the services
docker-compose up -d

# 5. Verify deployment
curl http://localhost:8000/api/v1/status
```

## Configuration

### municipality.yaml

```yaml
municipality:
  name: "Your City Name"
  timezone: "America/New_York"
  population: 150000

data_sources:
  weather:
    provider: "openweathermap"
    api_key: "${WEATHER_API_KEY}"
    update_interval: 3600
  
  events:
    provider: "manual"
    calendar_url: ""

resources:
  shelters:
    - name: "Main Shelter"
      capacity: 150
      location: [40.7128, -74.0060]
    
    - name: "Overflow Shelter"
      capacity: 75
      location: [40.7580, -73.9855]

  food_banks:
    - name: "Central Food Bank"
      capacity: 5000
      location: [40.7484, -73.9857]

optimization:
  solver: "cbc"
  time_limit: 300
  fairness_constraint: 0.8
  
alerts:
  twilio:
    account_sid: "${TWILIO_SID}"
    auth_token: "${TWILIO_TOKEN}"
    from_number: "+1234567890"
  
  recipients:
    - "+1987654321"
    - "+1122334455"
```

## Operations

### Daily Check

```bash
# Check service status
docker-compose ps

# View recent predictions
curl http://localhost:8000/api/v1/forecast/all?horizon=24h

# Check optimization status
curl http://localhost:8000/api/v1/status
```

### Manual Reoptimization

```bash
# Trigger immediate reoptimization
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual", "reason": "demand_update"}'
```

### Log Access

```bash
# Application logs
docker-compose logs -f api

# Optimization solver logs
docker-compose logs -f optimizer

# Database logs
docker-compose logs -f postgres
```

## Troubleshooting

### Problem: Solver timeout

**Symptom**: Optimization takes >300 seconds

**Solution**:
1. Check problem size: `curl http://localhost:8000/api/v1/problem/stats`
2. Reduce time horizon if >7 days
3. Increase solver time limit in config

### Problem: Prediction accuracy drop

**Symptom**: Demand forecasts consistently off by >20%

**Solution**:
1. Check data freshness: `curl http://localhost:8000/api/v1/data/status`
2. Retrain models: `./scripts/retrain.sh`
3. Review feature importance: `curl http://localhost:8000/api/v1/models/features`

### Problem: Database connection errors

**Symptom**: API returns 500 errors

**Solution**:
1. Check PostgreSQL status: `docker-compose ps postgres`
2. Restart if needed: `docker-compose restart postgres`
3. Check disk space: `df -h`

## Backup & Recovery

### Automated Backups

```bash
# Backups run daily at 2 AM via cron
# Location: /backups/civic-bridge/

# Manual backup
./scripts/backup.sh

# List backups
ls -la /backups/civic-bridge/
```

### Recovery

```bash
# Stop services
docker-compose down

# Restore from backup
./scripts/restore.sh /backups/civic-bridge/backup_20260701.sql

# Restart services
docker-compose up -d
```

## Monitoring

### Grafana Dashboard

Access at: `http://localhost:3000`

Default credentials:
- Username: admin
- Password: (set during first login)

### Key Metrics

- **Prediction Accuracy**: MAE < 10% target
- **Solver Time**: <5s for daily, <30s for weekly
- **API Latency**: p99 < 500ms
- **Uptime Target**: 99.9%

---

*The Civic Bridge Initiative — Operations Manual*

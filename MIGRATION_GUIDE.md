# Migration Guide: Old Structure to Production-Ready Structure

## Overview
This guide helps you migrate from the current `src/` structure to the production-ready structure.

## Current Structure (src/)
```
src/
├── usermanagement_service/
├── flightbooking_service/
├── notification_service/
├── tokenmanagement_service/
└── pyportal_common/
```

## New Structure (services/)
```
services/
├── usermanagement/
├── booking/
├── notification/
└── auth/
common/
└── pyportal_common/
```

## Migration Steps

### Step 1: Copy Service Code
```bash
# User Management
cp -r src/usermanagement_service/* services/usermanagement/app/

# Booking
cp -r src/flightbooking_service/* services/booking/app/

# Notification
cp -r src/notification_service/* services/notification/app/

# Auth
cp -r src/tokenmanagement_service/* services/auth/app/

# Common
cp -r src/pyportal_common common/
```

### Step 2: Update Imports
Update all imports in service code:
- `from src.pyportal_common...` → `from common.pyportal_common...`
- `from src.usermanagement_service...` → `from app...` (within service)

### Step 3: Create Service Entry Points
Each service needs a `main.py`:
```python
# services/usermanagement/app/main.py
from app import usermanager_app, user_management_logger

if __name__ == "__main__":
    usermanager_app.run(
        host=usermanager_app.config["SERVER_HOST"],
        port=usermanager_app.config["SERVER_PORT"]
    )
```

### Step 4: Update Dockerfiles
Update Dockerfiles to use new paths:
- `COPY app/ ./app/`
- `COPY ../common/ ./common/`

### Step 5: Update Docker Compose
Update `docker-compose.yml` to use new build contexts:
```yaml
usermanagement-service:
  build:
    context: ../../services/usermanagement
    dockerfile: Dockerfile
```

## Automated Migration

Run the migration script:
```bash
./scripts/migrate_to_production_structure.sh
```

Then manually:
1. Copy files to new locations
2. Update imports
3. Test each service

## Testing After Migration

1. Build each service:
   ```bash
   cd services/usermanagement
   docker build -t usermanagement-service .
   ```

2. Test locally:
   ```bash
   docker run -p 9091:9091 usermanagement-service
   ```

3. Run integration tests:
   ```bash
   pytest tests/integration/
   ```

## Rollback

If needed, the old structure in `src/` is preserved. You can:
1. Keep both structures during transition
2. Use old structure by updating docker-compose paths
3. Remove old structure after successful migration


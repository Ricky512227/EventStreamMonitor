#!/bin/bash
# Migration script to reorganize codebase into production-ready structure

set -e

echo "Starting migration to production-ready structure..."

# Create directories
echo "Creating directory structure..."
mkdir -p services/usermanagement/app/{models,views,services,schemas,grpc,kafka}
mkdir -p services/usermanagement/{migrations,tests}
mkdir -p services/booking/app/{models,views,services,schemas,kafka}
mkdir -p services/booking/{migrations,tests}
mkdir -p services/notification/app/{models,services,kafka}
mkdir -p services/notification/{migrations,tests}
mkdir -p services/auth/app/{models,views,services,schemas,tokens,utils}
mkdir -p services/auth/{migrations,tests}
mkdir -p common/pyportal_common
mkdir -p infrastructure/docker
mkdir -p infrastructure/kubernetes/{usermanagement,booking,notification,auth}
mkdir -p config/{development,staging,production}
mkdir -p tests/{integration,e2e}
mkdir -p scripts
mkdir -p docs/{api,architecture,deployment}
mkdir -p proto

echo "Directory structure created successfully!"


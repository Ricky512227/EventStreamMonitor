# HashiCorp Vault Setup Guide

## Quick Start

### 1. Start Vault (Development Mode)

```bash
# Using the provided docker-compose file
docker-compose -f docker-compose.vault.yml up -d vault

# Or start Vault standalone
docker run -d --name vault \
 -p 8200:8200 \
 -e VAULT_DEV_ROOT_TOKEN_ID=dev-root-token \
 hashicorp/vault:1.15.0
```

### 2. Access Vault UI

Open browser: http://localhost:8200

Token: `dev-root-token` (or the token you set)

### 3. Store Secrets

Using Vault CLI:
```bash
# Access Vault container
docker exec -it vault sh

# Set a secret
vault kv put secret/usermanagement/db \
 username=airlineradmin \
 password="testeventstreammonitor#123" \
 host=registration-db \
 port=5432 \
 database=REGISTRATIONS
```

Using HTTP API:
```bash
curl \
 --header "X-Vault-Token: dev-root-token" \
 --request POST \
 --data '{"data": {"username": "airlineradmin", "password": "testeventstreammonitor#123"}}' \
 http://localhost:8200/v1/secret/data/usermanagement/db
```

Using Vault UI:
1. Navigate to http://localhost:8000 (Vault UI)
2. Login with token
3. Go to "Secrets" → "Create Secret"
4. Path: `secret/usermanagement/db`
5. Add key-value pairs

### 4. Use Secrets in Your Services

```python
# In your service code (e.g., services/usermanagement/app/app_configs.py)
from app.vault_helper import get_secret

# Get database password from Vault
try:
 db_config = get_secret('secret/data/usermanagement/db')
 DATABASE_URL = (
 f"postgresql://{db_config['username']}:{db_config['password']}"
 f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
 )
except Exception as e:
 # Fallback to environment variable if Vault is unavailable
 DATABASE_URL = os.getenv('DATABASE_URL')
```

## Production Setup

For production, use file storage backend:

1. Create `vault/config/vault.hcl`:
```hcl
storage "file" {
 path = "/vault/data"
}

listener "tcp" {
 address = "0.0.0.0:8200"
 tls_disable = 0
 tls_cert_file = "/vault/config/vault.crt"
 tls_key_file = "/vault/config/vault.key"
}

api_addr = "http://0.0.0.0:8200"
ui = true
```

2. Update docker-compose for production:
```yaml
vault:
 image: hashicorp/vault:1.15.0
 volumes:
 - ./vault/config:/vault/config
 - vault-data:/vault/data
 command: vault server -config=/vault/config/vault.hcl
```

## Secret Paths Convention

Recommended structure:
```
secret/
 data/
 usermanagement/
 db # Database credentials
 jwt # JWT secret key
 kafka # Kafka credentials
 booking/
 db
 external-api
 notification/
 db
 smtp
```

## Security Best Practices

1. **Never use dev mode in production**
2. **Enable TLS** for all Vault communication
3. **Use proper access policies** (least privilege)
4. **Rotate tokens** regularly
5. **Enable audit logging**
6. **Use environment variables** for tokens, never hardcode
7. **Set up high availability** for production

## Alternative: Environment Variables

If Vault is not available, fallback to environment variables:

```python
import os
from app.vault_helper import get_secret

def get_database_url():
 try:
 # Try Vault first
 db_config = get_secret('secret/data/usermanagement/db')
 return (
 f"postgresql://{db_config['username']}:{db_config['password']}"
 f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
 )
 except:
 # Fallback to environment variable
 return os.getenv('DATABASE_URL', 'postgresql://localhost/db')
```


"""
Helper module for HashiCorp Vault integration
"""
import os
import requests
from typing import Optional, Dict, Any


class VaultClient:
    """Simple Vault client for retrieving secrets"""
    
    def __init__(self, vault_addr: Optional[str] = None, vault_token: Optional[str] = None):
        """
        Initialize Vault client
        
        Args:
            vault_addr: Vault server address (default: from VAULT_ADDR env var)
            vault_token: Vault authentication token (default: from VAULT_TOKEN env var)
        """
        self.vault_addr = vault_addr or os.getenv('VAULT_ADDR', 'http://localhost:8200')
        self.vault_token = vault_token or os.getenv('VAULT_TOKEN')
        
        if not self.vault_token:
            raise ValueError("Vault token not provided. Set VAULT_TOKEN environment variable.")
        
        self.base_url = self.vault_addr.rstrip('/')
        self.headers = {
            'X-Vault-Token': self.vault_token,
            'Content-Type': 'application/json'
        }
    
    def get_secret(self, secret_path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve a secret from Vault
        
        Args:
            secret_path: Path to the secret (e.g., 'secret/data/usermanagement/db')
            key: Optional key to retrieve specific value from secret
        
        Returns:
            Secret value(s). If key is specified, returns that value. Otherwise returns dict.
        
        Example:
            # Get entire secret
            secret = vault.get_secret('secret/data/usermanagement/db')
            
            # Get specific key
            password = vault.get_secret('secret/data/usermanagement/db', 'password')
        """
        url = f"{self.base_url}/v1/{secret_path}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()['data']['data']
            
            if key:
                return data.get(key)
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve secret from Vault: {e}")
    
    def list_secrets(self, path: str) -> list:
        """
        List secrets at a given path
        
        Args:
            path: Path to list (e.g., 'secret/metadata/usermanagement')
        
        Returns:
            List of secret keys
        """
        url = f"{self.base_url}/v1/{path}?list=true"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()['data']['keys']
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list secrets from Vault: {e}")


# Convenience function for quick secret retrieval
def get_secret(secret_path: str, key: Optional[str] = None, 
               vault_addr: Optional[str] = None, 
               vault_token: Optional[str] = None) -> Any:
    """
    Quick function to get a secret from Vault
    
    Args:
        secret_path: Path to the secret
        key: Optional key to retrieve specific value
        vault_addr: Optional Vault address (uses env var if not provided)
        vault_token: Optional Vault token (uses env var if not provided)
    
    Returns:
        Secret value(s)
    """
    client = VaultClient(vault_addr=vault_addr, vault_token=vault_token)
    return client.get_secret(secret_path, key)


# Example usage:
if __name__ == "__main__":
    # Initialize client
    vault = VaultClient()
    
    # Get database password (DO NOT print passwords in production!)
    db_password = vault.get_secret('secret/data/usermanagement/db', 'password')
    # Security: Never log or print passwords
    if db_password:
        print("DB Password: ***MASKED*** (retrieved successfully)")
    
    # Get entire secret object (sanitize before logging)
    db_config = vault.get_secret('secret/data/usermanagement/db')
    # Security: Mask sensitive keys before printing
    if db_config:
        sanitized_config = {k: "***MASKED***" if 'password' in k.lower() or 'secret' in k.lower() else v 
                           for k, v in db_config.items()}
        print(f"DB Config: {sanitized_config}")


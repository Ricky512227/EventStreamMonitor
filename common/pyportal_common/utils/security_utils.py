"""
Security utility functions for masking sensitive data in logs
"""
from typing import Dict, Any, Union
import re


def mask_ip_address(ip_address: str) -> str:
    """
    Mask IP address for security in logs.
    Masks the last octet for IPv4 (e.g., 192.168.1.100 -> 192.168.1.xxx)
    Masks the last segment for IPv6 (e.g., 2001:db8::1 -> 2001:db8::xxx)
    
    Args:
        ip_address: IP address to mask
        
    Returns:
        Masked IP address string
    """
    if not ip_address or ip_address == "unknown":
        return "unknown"
    
    # Handle IPv4 addresses
    if "." in ip_address:
        parts = ip_address.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
    
    # Handle IPv6 addresses
    if ":" in ip_address:
        # For IPv6, mask the last segment
        if "::" in ip_address:
            # Handle compressed IPv6 (e.g., 2001:db8::1)
            parts = ip_address.split("::")
            if len(parts) == 2:
                return f"{parts[0]}::xxx"
        else:
            # Handle full IPv6 (e.g., 2001:0db8:85a3:0000:0000:8a2e:0370:7334)
            parts = ip_address.split(":")
            if len(parts) > 0:
                return ":".join(parts[:-1]) + ":xxx"
    
    # If format is unrecognized, return masked version
    return "xxx.xxx.xxx.xxx"


def mask_request_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask IP addresses in request headers for security.
    Masks X-Forwarded-For, X-Real-IP, and other IP-related headers.
    
    Args:
        headers: Dictionary of request headers
        
    Returns:
        Dictionary with masked IP addresses in headers
    """
    if not headers:
        return headers
    
    # Headers that may contain IP addresses
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Forwarded',
        'Forwarded-For',
        'Forwarded',
        'Client-IP',
        'Remote-Addr',
        'X-Originating-IP',
        'X-Remote-IP',
        'X-Remote-Addr'
    ]
    
    masked_headers = headers.copy()
    
    for header_name in ip_headers:
        if header_name in masked_headers:
            ip_value = masked_headers[header_name]
            if isinstance(ip_value, str):
                # X-Forwarded-For can contain multiple IPs separated by commas
                if ',' in ip_value:
                    ips = [ip.strip() for ip in ip_value.split(',')]
                    masked_ips = [mask_ip_address(ip) for ip in ips]
                    masked_headers[header_name] = ', '.join(masked_ips)
                else:
                    masked_headers[header_name] = mask_ip_address(ip_value)
    
    return masked_headers


def sanitize_sensitive_data(data: Union[Dict, str, Any], sensitive_keys: list = None) -> Union[Dict, str, Any]:
    """
    Sanitize sensitive data from dictionaries, strings, or objects for logging.
    Masks passwords, tokens, secrets, and other sensitive fields.
    
    Args:
        data: Data to sanitize (dict, str, or object)
        sensitive_keys: List of keys to mask (default: common sensitive keys)
        
    Returns:
        Sanitized data with sensitive values masked
    """
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'pwd', 'passwd', 'secret', 'token', 'api_key', 'apikey',
            'access_token', 'accessToken', 'refresh_token', 'refreshToken',
            'jwt', 'jwt_secret', 'jwt_secret_key', 'credential', 'credentials',
            'auth_token', 'authToken', 'bearer_token', 'bearerToken',
            'db_password', 'dbPassword', 'database_password', 'databasePassword',
            'vault_token', 'vaultToken', 'api_secret', 'apiSecret',
            'private_key', 'privateKey', 'secret_key', 'secretKey'
        ]
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            # Check if key contains any sensitive keyword
            is_sensitive = any(sensitive_key in key_lower for sensitive_key in sensitive_keys)
            
            if is_sensitive:
                sanitized[key] = "***MASKED***"
            elif isinstance(value, dict):
                sanitized[key] = sanitize_sensitive_data(value, sensitive_keys)
            elif isinstance(value, list):
                sanitized[key] = [
                    sanitize_sensitive_data(item, sensitive_keys) if isinstance(item, (dict, str)) else item
                    for item in value
                ]
            elif isinstance(value, str) and any(sensitive_key in value.lower()[:50] for sensitive_key in ['password', 'token', 'secret']):
                # Mask if string contains sensitive keywords
                sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = value
        return sanitized
    
    elif isinstance(data, str):
        # Mask sensitive patterns in strings
        patterns = [
            (r'password["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', r'password": "***MASKED***'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', r'token": "***MASKED***'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', r'secret": "***MASKED***'),
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', r'api_key": "***MASKED***'),
        ]
        sanitized = data
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized
    
    # For objects, try to convert to dict
    elif hasattr(data, '__dict__'):
        return sanitize_sensitive_data(data.__dict__, sensitive_keys)
    
    return data


def sanitize_log_message(message: str) -> str:
    """
    Sanitize a log message string to remove sensitive data.
    
    Args:
        message: Log message string
        
    Returns:
        Sanitized log message
    """
    if not isinstance(message, str):
        return str(message)
    
    # Mask common sensitive patterns
    patterns = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', 'password": "***MASKED***'),
        (r'pwd["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', 'pwd": "***MASKED***'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', 'token": "***MASKED***'),
        (r'secret["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', 'secret": "***MASKED***'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\',\s}]+)', 'api_key": "***MASKED***'),
        (r'DB Password:\s*([^\s]+)', 'DB Password: ***MASKED***'),
    ]
    
    sanitized = message
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized


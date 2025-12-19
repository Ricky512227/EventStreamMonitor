# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email security details to: [your-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- Initial response: Within 48 hours
- Status update: Within 7 days
- Fix timeline: Depends on severity

## Security Best Practices

When using EventStreamMonitor:

- Keep Docker and dependencies updated
- Use strong passwords for databases
- Secure your Kafka brokers
- Regularly review access logs
- Use environment variables for secrets (never commit secrets)

## Known Security Considerations

- Database passwords should be changed from defaults
- Kafka should be secured in production
- Redis should have authentication enabled in production
- Use HTTPS in production environments


# Security Policy

## Supported Versions
| Version | Supported          |
| ------- | ------------------ |
| v3.0    | :white_check_mark: |
| v2.x    | :x:                |
| < v2.0  | :x:                |

## Reporting Vulnerabilities
This tool is for **EDUCATIONAL AND AUTHORIZED USE ONLY**. 
If you discover a security vulnerability in H-Dex, please document it and report it to the developer immediately.

## active Security Features
### 1. Authorization
- **Dashboard Access**: Protected by `DASHBOARD_TOKEN`. Ensure this token is strong and kept secret.
- **Discord Bot**: Restrict bot usage to specific Channel IDs and Role IDs in `config.json`.

### 2. Network Security
- **Encryption**: Production deployments MUST use `wss://` (WebSocket Secure) with a valid SSL certificate.
- **Traffic**: All traffic is JSON-encoded. Sensitive data (passwords, keystrokes) should be handled over encrypted channels.

### 3. Client Protection
- **Geofencing**: Prevents execution in unauthorized geographic regions.
- **Anti-VM**: Prevents analysis in virtual environments / sandboxes.
- **Stealth**: Operates silently to avoid detection by casual users.

### 4. Best Practices
- **Do not use default ports** (8765) in production.
- **Use a Reverse Proxy** (Nginx/Caddy) to terminate SSL and protect the Python server.
- **Monitor Audit Logs** regularly for unauthorized access attempts.

## Disclaimer
The developer assumes no liability and is not responsible for any misuse or damage caused by this program. You are responsible for ensuring you have permission to access any system you install this software on.

# SSL/TLS Certificate Setup & HTTPS Configuration

## Overview

This guide covers obtaining, installing, and renewing SSL/TLS certificates for DocPro using Let's Encrypt on Nginx.

---

## Prerequisites

- Domain name registered and pointing to your server
- Nginx installed
- Access to server (SSH)
- Port 80 and 443 accessible from internet
- Sudo or root privileges

---

## Step 1: Install Certbot

Certbot is the official Let's Encrypt client.

### On Ubuntu/Debian

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### On CentOS/RHEL

```bash
sudo yum install certbot python3-certbot-nginx
```

### On macOS

```bash
brew install certbot
```

### Using Docker

```bash
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly --standalone -d docpro.example.com
```

---

## Step 2: Obtain Initial Certificate

### Method 1: Automatic (Nginx Plugin - Recommended)

```bash
sudo certbot --nginx -d docpro.example.com -d api.docpro.example.com
```

This will:
1. Present ACME challenge
2. Verify domain ownership
3. Download certificate
4. Update Nginx config automatically
5. Reload Nginx

### Method 2: Standalone (For initial setup)

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Request certificate
sudo certbot certonly --standalone -d docpro.example.com -d api.docpro.example.com

# Restart Nginx
sudo systemctl start nginx
```

### Method 3: DNS Challenge (For wildcard certificates)

```bash
# Request wildcard certificate
sudo certbot certonly --dns-cloudflare \
  -d docpro.example.com \
  -d *.api.docpro.example.com
```

Requires DNS provider plugin (cloudflare, route53, etc.)

---

## Step 3: Certificate Location

After obtaining, certificates are stored in:

```bash
# Certificate chain
/etc/letsencrypt/live/docpro.example.com/fullchain.pem

# Private key
/etc/letsencrypt/live/docpro.example.com/privkey.pem

# Additional files
/etc/letsencrypt/live/docpro.example.com/cert.pem        # Just certificate
/etc/letsencrypt/live/docpro.example.com/chain.pem       # Intermediate chain
/etc/letsencrypt/live/docpro.example.com/README          # Information
```

---

## Step 4: Configure Nginx

Update your Nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name docpro.example.com api.docpro.example.com;
    
    # SSL/TLS Configuration
    ssl_certificate /etc/letsencrypt/live/docpro.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docpro.example.com/privkey.pem;
    
    # SSL Protocols
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Ciphers (strong)
    ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305";
    
    # Prefer server ciphers
    ssl_prefer_server_ciphers on;
    
    # Session caching
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # ... rest of Nginx config
}

# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name docpro.example.com api.docpro.example.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

### Verify Configuration

```bash
# Test syntax
sudo nginx -t

# Reload if valid
sudo systemctl reload nginx
```

---

## Step 5: Set Up Auto-Renewal

Let's Encrypt certificates expire after 90 days. Certbot can auto-renew.

### Enable Auto-Renewal

```bash
# Enable renewal timer (systemd)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check status
sudo systemctl status certbot.timer
```

### Manual Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Actual renewal
sudo certbot renew

# Renewal for specific domain
sudo certbot renew --cert-name docpro.example.com
```

### Renewal Hooks

Run custom commands on renewal (e.g., reload Nginx):

```bash
# Create renewal hook
sudo mkdir -p /etc/letsencrypt/renewal-hooks/post/

# Create script
sudo tee /etc/letsencrypt/renewal-hooks/post/nginx.sh > /dev/null <<EOF
#!/bin/bash
systemctl reload nginx
EOF

# Make executable
sudo chmod +x /etc/letsencrypt/renewal-hooks/post/nginx.sh
```

---

## Step 6: OCSP Stapling

OCSP stapling improves verification performance.

```nginx
server {
    listen 443 ssl http2;
    
    ssl_certificate /etc/letsencrypt/live/docpro.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docpro.example.com/privkey.pem;
    
    # OCSP stapling
    ssl_trusted_certificate /etc/letsencrypt/live/docpro.example.com/chain.pem;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Resolver for OCSP (use system resolver or public DNS)
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
}
```

---

## Step 7: Certificate Monitoring

### Check Expiry Date

```bash
# View expiry date
sudo certbot certificates

# or direct SSL check
echo | openssl s_client -servername docpro.example.com -connect docpro.example.com:443 | openssl x509 -noout -dates
```

### Set Up Expiry Alerts

Create a cron job to warn before expiry:

```bash
# Add to crontab
sudo crontab -e

# Add this line (check 30 days before expiry)
0 0 * * * /usr/local/bin/check-cert-expiry.sh
```

Checking script:

```bash
#!/bin/bash
# /usr/local/bin/check-cert-expiry.sh

DOMAIN="docpro.example.com"
DAYS_UNTIL_EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2 | xargs -I{} date -d {} +%s | awk '{print int(($1 - ($(date +%s))) / 86400)}')

if [ $DAYS_UNTIL_EXPIRY -lt 30 ]; then
    echo "Alert: Certificate for $DOMAIN expires in $DAYS_UNTIL_EXPIRY days" | \
    mail -s "Certificate Expiry Warning" admin@example.com
fi
```

---

## Step 8: Security Headers

Add HSTS and other security headers:

```nginx
server {
    listen 443 ssl http2;
    
    # HSTS (Strict-Transport-Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Certificate Transparency
    add_header Public-Key-Pins "pin-sha256=\"...=\"; pin-sha256=\"...=\"; max-age=2592000; includeSubDomains" always;
    
    # X-Frame-Options
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # X-Content-Type-Options
    add_header X-Content-Type-Options "nosniff" always;
    
    # X-XSS-Protection
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Referrer-Policy
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

---

## Step 9: Certificate Chaining

Ensure proper certificate chain:

```bash
# Verify certificate chain
openssl s_client -connect docpro.example.com:443 -showcerts

# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/docpro.example.com/fullchain.pem -text -noout

# Verify private key matches certificate
openssl md5 <(openssl x509 -noout -modulus -in /etc/letsencrypt/live/docpro.example.com/fullchain.pem) <(openssl rsa -noout -modulus -in /etc/letsencrypt/live/docpro.example.com/privkey.pem)
```

---

## Step 10: Testing & Validation

### SSL/TLS Test

```bash
# Quick check
curl -I https://docpro.example.com

# Detailed check
openssl s_client -connect docpro.example.com:443 -tls1_2

# Grade your configuration
# Use: https://www.ssllabs.com/ssltest/
```

### Certificate Transparency

```bash
# Check CT logs (required by modern browsers)
echo | openssl s_client -connect docpro.example.com:443 | openssl x509 -noout -text | grep -A5 "CT Precertificate"
```

---

## Step 11: Multi-Domain & SAN Certificates

Add alternative domain names (SANs):

```bash
# Single command for multiple domains
sudo certbot certonly --nginx -d docpro.example.com -d api.docpro.example.com -d www.docpro.example.com
```

Or edit renewal configuration:

```bash
# Edit renewal config
sudo nano /etc/letsencrypt/renewal/docpro.example.com.conf

# Add to [docpro.example.com] section:
# domains = docpro.example.com, api.docpro.example.com, www.docpro.example.com

# Renew
sudo certbot renew --cert-name docpro.example.com --force-renewal
```

---

## Step 12: Wildcard Certificate

For subdomains:

```bash
# DNS challenge required for wildcard
sudo certbot certonly --dns-cloudflare -d *.api.docpro.example.com

# Requires DNS provider configuration
# See: https://certbot.eff.org/docs/plugins.html
```

---

## Troubleshooting

### Certificate Renewal Failing

```bash
# Check renewal logs
cat /var/log/letsencrypt/letsencrypt.log

# Force renewal with verbose output
sudo certbot renew --cert-name docpro.example.com --force-renewal -v

# Common causes:
# 1. Port 80/443 blocked
# 2. DNS not resolving
# 3. Rate limiting (5 per hour per domain)
```

### ACME Challenge Failing

```bash
# Verifyexample.com resolves to server
nslookup docpro.example.com

# Check port 80 is accessible
curl -I http://docpro.example.com/.well-known/acme-challenge/test
```

### Permission Issues

```bash
# Ensure Nginx can read certificate
sudo chown -R root:root /etc/letsencrypt/
sudo chmod -R 755 /etc/letsencrypt/
sudo chmod -R 644 /etc/letsencrypt/live/*/cert.pem
sudo chmod -R 644 /etc/letsencrypt/live/*/chain.pem
sudo chmod -R 644 /etc/letsencrypt/live/*/fullchain.pem
sudo chmod -R 600 /etc/letsencrypt/live/*/privkey.pem
```

---

## Certificate Rotation

### For Kubernetes

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: docpro-cert
  namespace: default
spec:
  secretName: docpro-tls
  duration: 2160h  # 90 days
  renewBefore: 720h  # 30 days
  commonName: docpro.example.com
  dnsNames:
  - docpro.example.com
  - api.docpro.example.com
  isCA: false
  privateKey:
    algorithm: RSA
    encoding: PKCS1
    size: 2048
  usages:
  - digital signature
  - key encipherment
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

### For Docker Composeuence

```yaml
version: '3.8'

services:
  certbot:
    image: certbot/certbot
    volumes:
      - ./letsencrypt:/etc/letsencrypt
      - ./certs:/var/www/certbot
    entrypoint: /bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./letsencrypt:/etc/letsencrypt
      - ./certs:/var/www/certbot
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - certbot
```

---

## Security Best Practices

1. **Always use HTTPS** - Redirect all HTTP to HTTPS
2. **HSTS** - Enable and test carefully (can lock you out if misconfigured)
3. **Keep certs updated** - Set up auto-renewal
4. **Monitor expiry** - Get alerts 30 days before
5. **Strong ciphers** - Use TLS 1.2+ only
6. **OCSP stapling** - Improve performance and privacy
7. **Regular audits** - Run SSL Labs tests monthly
8. **Backup certificates** - Keep copies in secure location

---

## Monitoring Checklist

- [ ] Certificate validity checked monthly
- [ ] HSTS header present
- [ ] TLS 1.2+ enabled
- [ ] Strong ciphers configured
- [ ] OCSP stapling working
- [ ] Renewal automation tested
- [ ] Expiry alerts set up
- [ ] SSL Labs grade A or A+

---

**Last Updated**: 2024-01-15
**Review Schedule**: Monthly
**Emergency Support**: Certbot docs at certbot.eff.org

# BeeMind DNS Configuration Guide

This guide helps you configure DNS records for your `beemind.dev` domain to point to your production server.

## Required DNS Records

### A Records (IPv4)
Point these subdomains to your server's IPv4 address:

```
beemind.dev           A    YOUR_SERVER_IP
www.beemind.dev       A    YOUR_SERVER_IP  
api.beemind.dev       A    YOUR_SERVER_IP
mlflow.beemind.dev    A    YOUR_SERVER_IP
monitoring.beemind.dev A   YOUR_SERVER_IP
```

### AAAA Records (IPv6) - Optional
If your server has IPv6, add these records:

```
beemind.dev           AAAA  YOUR_SERVER_IPv6
www.beemind.dev       AAAA  YOUR_SERVER_IPv6
api.beemind.dev       AAAA  YOUR_SERVER_IPv6
mlflow.beemind.dev    AAAA  YOUR_SERVER_IPv6
monitoring.beemind.dev AAAA YOUR_SERVER_IPv6
```

### CNAME Records - Alternative Approach
Instead of multiple A records, you can use CNAME records:

```
www.beemind.dev       CNAME  beemind.dev
api.beemind.dev       CNAME  beemind.dev
mlflow.beemind.dev    CNAME  beemind.dev
monitoring.beemind.dev CNAME beemind.dev
```

## Domeneshop Configuration

Since you're using Domeneshop, follow these steps:

1. **Login to Domeneshop Control Panel**
   - Go to https://domene.shop
   - Login with your credentials

2. **Navigate to DNS Management**
   - Select your `beemind.dev` domain
   - Click on "DNS" or "Navneserver"

3. **Add DNS Records**
   ```
   Type: A
   Name: @
   Value: YOUR_SERVER_IP
   TTL: 3600
   
   Type: A  
   Name: www
   Value: YOUR_SERVER_IP
   TTL: 3600
   
   Type: A
   Name: api
   Value: YOUR_SERVER_IP
   TTL: 3600
   
   Type: A
   Name: mlflow
   Value: YOUR_SERVER_IP
   TTL: 3600
   
   Type: A
   Name: monitoring
   Value: YOUR_SERVER_IP
   TTL: 3600
   ```

4. **Email Configuration (Optional)**
   ```
   Type: MX
   Name: @
   Value: mail.beemind.dev
   Priority: 10
   TTL: 3600
   ```

## Verification Commands

After configuring DNS, verify the records are working:

```bash
# Check main domain
dig beemind.dev A
nslookup beemind.dev

# Check subdomains
dig api.beemind.dev A
dig www.beemind.dev A
dig mlflow.beemind.dev A
dig monitoring.beemind.dev A

# Check from different DNS servers
dig @8.8.8.8 beemind.dev A
dig @1.1.1.1 beemind.dev A
```

## DNS Propagation

- **Local DNS**: 5-15 minutes
- **Global Propagation**: 24-48 hours
- **TTL Impact**: Lower TTL = faster updates

Check propagation status:
- https://dnschecker.org
- https://whatsmydns.net

## SSL Certificate Notes

The deployment script will automatically request SSL certificates for:
- beemind.dev
- www.beemind.dev  
- api.beemind.dev

Make sure DNS is working before running the deployment script!

## Troubleshooting

### Common Issues

1. **DNS Not Resolving**
   - Check if records are correctly added
   - Wait for propagation (up to 48 hours)
   - Try different DNS servers

2. **SSL Certificate Fails**
   - Ensure DNS points to correct server
   - Check if port 80 is accessible
   - Verify domain ownership

3. **Subdomain Not Working**
   - Verify A/CNAME records for subdomains
   - Check nginx configuration
   - Ensure firewall allows traffic

### Testing Commands

```bash
# Test HTTP connectivity
curl -I http://beemind.dev
curl -I http://api.beemind.dev

# Test HTTPS after SSL setup
curl -I https://beemind.dev
curl -I https://api.beemind.dev

# Check certificate details
openssl s_client -connect beemind.dev:443 -servername beemind.dev
```

## Security Recommendations

1. **Enable DNSSEC** (if supported by Domeneshop)
2. **Set appropriate TTL values**
   - Short TTL (300-600s) during setup
   - Longer TTL (3600s+) for production
3. **Monitor DNS changes**
4. **Use CAA records** for certificate authority authorization

## Example CAA Record

```
beemind.dev  CAA  0 issue "letsencrypt.org"
beemind.dev  CAA  0 issuewild "letsencrypt.org"
beemind.dev  CAA  0 iodef "mailto:admin@beemind.dev"
```

## Next Steps

1. Configure DNS records as shown above
2. Wait for DNS propagation (check with dig/nslookup)
3. Update your server's IP in the deployment configuration
4. Run the deployment script: `./deploy.sh`
5. Verify all services are accessible via HTTPS

## Support

If you encounter issues:
- Check Domeneshop documentation
- Verify server firewall settings
- Test DNS resolution from multiple locations
- Contact your hosting provider if needed

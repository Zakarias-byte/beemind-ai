# 🔐 GitHub Secrets Setup for BeeMind Deployment

## 📋 Required Secrets

For the GitHub Actions workflows to work properly, you need to set up the following secrets in your GitHub repository:

### 🔑 How to Add Secrets

1. Go to your GitHub repository: `https://github.com/Zakarias-byte/beemind-ai`
2. Click on **Settings** tab
3. In the left sidebar, click on **Secrets and variables** → **Actions**
4. Click **New repository secret** for each secret below

---

## 🎯 Required Secrets

### 1. `EC2_HOST`
**Description**: Your EC2 instance public IP address

**Value**: `16.16.73.195`

### 2. `EC2_USER`
**Description**: SSH username for your EC2 instance

**Value**: `ubuntu`

### 3. `EC2_SSH_KEY`
**Description**: Your private SSH key for connecting to the EC2 instance

**Value**: The contents of your `cybersecurity-key.pem` private key file
```bash
# Get the contents of your private key
cat ~/.ssh/cybersecurity-key.pem
```

**Example**:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
...
-----END OPENSSH PRIVATE KEY-----
```

### 4. `BEE_MIND_SECRET_KEY`
**Description**: Secret key for the BeeMind application

**Value**: A secure random string (at least 32 characters)

**Generate with**:
```bash
# Generate a secure secret key
openssl rand -hex 32
# or
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Example**: `a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234`

### 5. `BEE_MIND_JWT_SECRET`
**Description**: Secret key for JWT token signing

**Value**: A secure random string (at least 32 characters)

**Generate with**:
```bash
# Generate a secure JWT secret
openssl rand -hex 32
# or
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Example**: `f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba1234`

---

## 🔧 Optional Secrets

### 4. `SLACK_WEBHOOK_URL` (Optional)
**Description**: Slack webhook URL for deployment notifications

**Value**: Your Slack webhook URL
**Example**: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`

### 5. `DISCORD_WEBHOOK_URL` (Optional)
**Description**: Discord webhook URL for deployment notifications

**Value**: Your Discord webhook URL
**Example**: `https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz`

---

## 🚀 Quick Setup Script

You can use this script to generate the required secrets:

```bash
#!/bin/bash

echo "🔐 Generating BeeMind GitHub Secrets..."
echo "========================================"

# Generate secret keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

echo "Generated Secrets:"
echo "=================="
echo "EC2_HOST: 16.16.73.195"
echo "EC2_USER: ubuntu"
echo "BEE_MIND_SECRET_KEY: $SECRET_KEY"
echo "BEE_MIND_JWT_SECRET: $JWT_SECRET"
echo ""
echo "EC2_SSH_KEY: (Copy the contents of ~/.ssh/cybersecurity-key.pem)"
echo ""
echo "Add these to your GitHub repository secrets:"
echo "1. Go to: https://github.com/Zakarias-byte/beemind-ai/settings/secrets/actions"
echo "2. Click 'New repository secret' for each"
echo "3. Use the values above"
```

---

## ✅ Verification

After setting up the secrets, you can verify they're working by:

1. **Trigger a manual deployment**:
   - Go to **Actions** tab in your repository
   - Click on **Deploy BeeMind to Production**
   - Click **Run workflow**
   - Select **main** branch
   - Click **Run workflow**

2. **Check the logs**:
   - The workflow should start without authentication errors
   - Look for successful SSH connections to your EC2 instance

---

## 🔒 Security Notes

- **Never commit secrets to your repository**
- **Rotate secrets regularly** (every 90 days)
- **Use different secrets for different environments**
- **Limit access to repository secrets**

---

## 🚨 Troubleshooting

### Common Issues:

1. **SSH Connection Failed**:
   - Verify your `EC2_SSH_KEY` is correct
   - Ensure the key has the right permissions
   - Check that the EC2 instance is running

2. **Permission Denied**:
   - Verify the SSH key is added to the EC2 instance
   - Check that the `ubuntu` user exists on the server

3. **Secret Not Found**:
   - Double-check the secret names (case-sensitive)
   - Ensure secrets are added to the correct repository

---

## 📞 Support

If you encounter issues:

1. Check the GitHub Actions logs for detailed error messages
2. Verify all secrets are correctly set
3. Test SSH connection manually: `ssh -i ~/.ssh/cybersecurity-key ubuntu@16.16.73.195`

---

**Once secrets are configured, your GitHub Actions will automatically deploy BeeMind to beemind.dev! 🚀**

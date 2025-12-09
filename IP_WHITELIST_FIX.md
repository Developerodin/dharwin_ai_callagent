# IP Whitelist Fix for ngrok

## 🔍 Issue

You're seeing this error:
```
❌ Unauthorized webhook request from IP: 13.232.85.9
127.0.0.1 - - [09/Dec/2025 15:54:29] "POST / HTTP/1.1" 403 -
```

## 📋 What's Happening

When using **ngrok** to expose your local server, the webhook requests appear to come from **ngrok's IP addresses**, not Bolna's original IPs. This causes the IP whitelist validation to fail.

## ✅ Fix Applied

The code now:
1. **Detects ngrok** - Checks for ngrok headers
2. **Checks original IP** - Looks at `X-Forwarded-For` header to find the original Bolna IP
3. **Allows ngrok requests** - If ngrok is detected, allows the request (since ngrok is a proxy)

## 🔧 Options

### Option 1: Add IP to Whitelist (If confirmed from Bolna)

If `13.232.85.9` is confirmed to be a new Bolna webhook IP, add it to the whitelist:

```python
BOLNA_WEBHOOK_IPS = [
    '13.200.45.61',
    '65.2.44.157',
    # ... existing IPs ...
    '13.232.85.9',  # Add this
]
```

### Option 2: Use Development Mode (Temporary)

Set environment variable to allow all IPs:
```bash
export FLASK_ENV=development
# or
set FLASK_ENV=development  # Windows
```

### Option 3: Disable IP Validation (Not Recommended)

Only for testing - remove the `@validate_bolna_ip` decorator (security risk).

## 🧪 Testing

After the fix:
1. The code will detect ngrok and allow requests
2. It will log the IP for review
3. If you see the same IP repeatedly, consider adding it to whitelist

## 📊 Current Status

The updated code will:
- ✅ Allow requests through ngrok
- ✅ Log IP information for verification
- ✅ Check original IP in X-Forwarded-For header
- ⚠️ Warn about unknown IPs but allow them when ngrok is detected

## 🔒 Security Note

The fix allows requests when ngrok is detected. Make sure:
- You're only exposing ngrok URL to Bolna
- You verify the IPs in logs
- You add confirmed Bolna IPs to the whitelist

---

**The webhook should now work with ngrok!** ✅


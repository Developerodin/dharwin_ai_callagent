# Webhook Setup Guide

This guide explains how to set up the webhook endpoint to receive real-time call execution data from Bolna Voice AI and automatically update candidate data.

## Overview

The webhook endpoint receives POST requests from Bolna AI whenever a call execution status changes. This allows for real-time updates to candidate statuses without polling.

## Webhook Endpoint

The webhook endpoint is available at:
- **Local Development**: `http://localhost:5000/api/webhook` or `http://localhost:5000/webhook`
- **Production**: `https://your-domain.com/api/webhook` or `https://your-domain.com/webhook`

## IP Whitelist

The webhook endpoint validates that requests come from Bolna AI's authorized IP addresses:

- `13.200.45.61`
- `65.2.44.157`
- `34.194.233.253`
- `13.204.98.4`
- `43.205.31.43`
- `107.20.118.52`

**Important**: In production, ensure your server/firewall allows incoming requests from these IPs.

## Setup Instructions

### 1. Start the Flask Server

Make sure your Flask API server is running:

```bash
python api_server.py
```

The server will start on `http://localhost:5000` by default.

### 2. Expose Your Webhook Endpoint (Production)

For production use, you'll need to expose your webhook endpoint publicly. Options include:

- **ngrok** (for testing):
  ```bash
  ngrok http 5000
  ```
  This will give you a public URL like `https://abc123.ngrok.io`. Use `https://abc123.ngrok.io/api/webhook` as your webhook URL.

- **Deploy to a cloud service** (AWS, Heroku, Railway, etc.):
  - Deploy your Flask app
  - Use the public URL: `https://your-app.com/api/webhook`

### 3. Configure Webhook in Bolna AI Dashboard

1. Log in to [Bolna AI Platform](https://platform.bolna.ai/)
2. Navigate to your agent settings
3. Find the "Webhook" or "Push all execution data to webhook" section
4. Enter your webhook URL:
   - For testing: `https://your-ngrok-url.ngrok.io/api/webhook`
   - For production: `https://your-domain.com/api/webhook`
5. Save the configuration

### 4. Test the Webhook

1. Initiate a test call from your application
2. Monitor the Flask server logs for webhook requests
3. Check that candidate status updates automatically when the call completes

## How It Works

### Execution ID Mapping

When a call is initiated:
1. The system stores a mapping between `execution_id` and `candidate_id` in `execution_mapping.json`
2. This mapping is used by the webhook to identify which candidate to update

### Webhook Processing Flow

1. **Receive Webhook**: Bolna AI sends POST request with execution data
2. **Validate IP**: Check that request comes from authorized Bolna IP
3. **Extract Execution ID**: Get `execution_id` from payload
4. **Find Candidate**: Look up candidate using execution_id mapping or phone number
5. **Parse Outcome**: Extract call status, transcript, and extracted_data
6. **Update Candidate**: Update candidate status based on call outcome:
   - `confirmed` - Candidate confirmed the interview
   - `declined` - Candidate declined the interview
   - `rescheduled` - Candidate requested a new time slot
   - `pending` - Could not determine outcome or call failed

### Webhook Payload Structure

The webhook receives execution data in the following format (structure may vary):

```json
{
  "execution_id": "exec_1234567890",
  "status": "completed",
  "transcript": "Full conversation transcript...",
  "extracted_data": {
    "status": "confirmed",
    "user_interested": true
  },
  "recipient_phone_number": "+918755887760",
  "telephony_data": {
    "duration": 120,
    "recording_url": "https://..."
  }
}
```

## Development Mode

In development mode (`FLASK_ENV=development`), the IP whitelist is bypassed for localhost requests. This allows you to test webhooks locally using tools like ngrok or Postman.

## Troubleshooting

### Webhook Not Receiving Requests

1. **Check IP Whitelist**: Ensure your server allows requests from Bolna IPs
2. **Verify URL**: Make sure the webhook URL in Bolna dashboard is correct
3. **Check Server Logs**: Look for incoming requests in Flask logs
4. **Test with ngrok**: Use ngrok to expose local server and test webhook delivery

### Candidate Not Updating

1. **Check Execution Mapping**: Verify `execution_mapping.json` contains the mapping
2. **Check Logs**: Look for error messages in Flask server logs
3. **Verify Payload**: Check webhook payload structure matches expected format
4. **Test Manually**: Try updating candidate status manually via API

### IP Validation Errors

If you see "Unauthorized IP address" errors:
- In development: Set `FLASK_ENV=development` in your `.env` file
- In production: Ensure requests are coming from Bolna IPs (check proxy/load balancer configuration)

## API Endpoints

### Webhook Endpoint
- **POST** `/api/webhook` or `/webhook`
- Receives webhook payloads from Bolna AI
- Updates candidate data automatically

### Manual Status Update (Alternative)
- **PUT** `/api/candidate/<candidate_id>/status`
- Manually update candidate status if webhook fails

## Security Considerations

1. **IP Whitelist**: Always validate webhook requests come from authorized IPs
2. **HTTPS**: Use HTTPS in production to encrypt webhook payloads
3. **Authentication**: Consider adding webhook signature validation if Bolna AI supports it
4. **Rate Limiting**: Implement rate limiting to prevent abuse

## Example Webhook Payload Processing

The webhook handler:
- Extracts `execution_id` from payload
- Looks up candidate using execution mapping
- Parses call outcome from transcript and extracted_data
- Updates candidate status in `data/candidates.json`
- Returns success response to Bolna AI

## Support

For issues or questions:
- Check Flask server logs for detailed error messages
- Review `execution_mapping.json` to verify execution mappings
- Test webhook endpoint manually using Postman or curl


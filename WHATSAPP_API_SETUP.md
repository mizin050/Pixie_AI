# WhatsApp Business API Setup Guide

## Why Use WhatsApp Business API?

### GUI Automation (Current)

- ❌ Unreliable (depends on UI changes)
- ❌ Requires WhatsApp Desktop to be open
- ❌ Can break with updates
- ❌ Slow (needs to find elements)
- ❌ Can't send to unsaved numbers easily

### WhatsApp Business API (Recommended)

- ✅ Official and reliable
- ✅ Works without WhatsApp Desktop
- ✅ Never breaks with updates
- ✅ Fast (direct API calls)
- ✅ Send to any number
- ✅ Supports images, documents, templates
- ✅ Free tier available

## Setup Steps

### 1. Create a Meta (Facebook) Developer Account

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click "Get Started" and create an account
3. Verify your email

### 2. Create a WhatsApp Business App

1. Go to [Meta App Dashboard](https://developers.facebook.com/apps)
2. Click "Create App"
3. Select "Business" as app type
4. Fill in app details:
   - App Name: "Pixie AI WhatsApp"
   - Contact Email: Your email
5. Click "Create App"

### 3. Add WhatsApp Product

1. In your app dashboard, find "WhatsApp" in the products list
2. Click "Set Up"
3. Select "Business Account" or create a new one

### 4. Get Your Credentials

#### Phone Number ID

1. Go to WhatsApp > API Setup
2. Copy the "Phone number ID" (looks like: `123456789012345`)
3. Add to `.env`:
   ```
   WHATSAPP_PHONE_NUMBER_ID=123456789012345
   ```

#### Access Token

1. In the same API Setup page
2. Copy the "Temporary access token" (starts with `EAA...`)
3. Add to `.env`:
   ```
   WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxx
   ```

**Note:** Temporary tokens expire in 24 hours. For production, generate a permanent token:

- Go to Settings > Basic
- Generate a System User token with `whatsapp_business_messaging` permission

### 5. Test Your Setup

Run the test script:

```bash
python test_whatsapp_api.py
```

Or test in Python:

```python
from src.integrations.whatsapp_api import send_whatsapp_message

result = send_whatsapp_message(
    to="1234567890",  # Your phone number (no + or -)
    message="Hello from Pixie AI!"
)

print(result)
```

## Usage Examples

### Send Text Message

```python
from src.integrations.whatsapp_api import send_whatsapp_message

result = send_whatsapp_message(
    to="1234567890",
    message="Hello! This is Pixie AI."
)

if result["success"]:
    print(f"✅ Message sent! ID: {result['message_id']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Send Image

```python
from src.integrations.whatsapp_api import send_whatsapp_image

result = send_whatsapp_image(
    to="1234567890",
    image_url="https://example.com/image.jpg",
    caption="Check out this image!"
)
```

### Send Document

```python
from src.integrations.whatsapp_api import send_whatsapp_document

result = send_whatsapp_document(
    to="1234567890",
    document_url="https://example.com/report.pdf",
    filename="report.pdf",
    caption="Here's your report"
)
```

## Integration with Pixie

Once configured, Pixie will automatically use the WhatsApp API when you say:

```
"Send a WhatsApp message to John saying hello"
"Send this screenshot to 1234567890 on WhatsApp"
"WhatsApp the report to my boss"
```

Pixie will:

1. Check if WhatsApp API is configured
2. If yes: Use API (fast and reliable)
3. If no: Fall back to GUI automation

## Phone Number Format

WhatsApp API requires phone numbers in international format WITHOUT the `+`:

- ✅ Correct: `1234567890` (US)
- ✅ Correct: `919876543210` (India)
- ❌ Wrong: `+1234567890`
- ❌ Wrong: `(123) 456-7890`

## Free Tier Limits

Meta provides a free tier for WhatsApp Business API:

- ✅ 1,000 free conversations per month
- ✅ Unlimited messages within 24-hour window
- ✅ All message types (text, image, document)

After free tier:

- ~$0.005 - $0.09 per conversation (varies by country)

## Troubleshooting

### Error: "Phone number not registered"

- Solution: Add your phone number to the test numbers list in Meta dashboard

### Error: "Invalid access token"

- Solution: Token expired. Generate a new one or create a permanent System User token

### Error: "Recipient phone number not in allowed list"

- Solution: In development mode, you can only send to registered test numbers
- Add numbers in WhatsApp > API Setup > "To" field

### Error: "Message failed to send"

- Check phone number format (no + or spaces)
- Verify recipient has WhatsApp installed
- Check your API quota

## Production Deployment

For production use:

1. **Verify Your Business**
   - Submit business verification in Meta Business Manager
   - Required for higher message limits

2. **Get Permanent Token**
   - Create a System User in Business Settings
   - Generate permanent token with `whatsapp_business_messaging` permission

3. **Set Up Webhooks** (Optional)
   - Receive incoming messages
   - Get delivery status updates

4. **Apply for Higher Limits**
   - Start with 250 unique recipients/day
   - Increases automatically based on quality

## Comparison: API vs GUI Automation

| Feature          | WhatsApp API | GUI Automation |
| ---------------- | ------------ | -------------- |
| Reliability      | 99.9%        | ~60%           |
| Speed            | <1 second    | 5-10 seconds   |
| Setup            | 10 minutes   | None           |
| Cost             | Free tier    | Free           |
| Maintenance      | None         | Frequent fixes |
| Scalability      | High         | Low            |
| Official Support | Yes          | No             |

## Recommendation

**Use WhatsApp Business API for:**

- ✅ Production applications
- ✅ Automated notifications
- ✅ High-volume messaging
- ✅ Critical communications

**Use GUI Automation for:**

- ✅ Quick testing
- ✅ Personal use
- ✅ When API setup isn't possible

## Resources

- [WhatsApp Cloud API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Get Started Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)
- [Pricing](https://developers.facebook.com/docs/whatsapp/pricing)

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review Meta's [error codes](https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes)
3. Test with the official [API Explorer](https://developers.facebook.com/tools/explorer/)

---

**Status: Ready to use!** 🚀

Once configured, Pixie will automatically use the WhatsApp API for all WhatsApp-related tasks.

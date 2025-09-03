# SendGrid Email Setup Guide

This guide will help you set up SendGrid for email notifications when contact forms are submitted.

## Step 1: Create a SendGrid Account

1. Go to [SendGrid.com](https://sendgrid.com)
2. Sign up for a free account (100 emails/day)
3. Verify your email address

## Step 2: Get Your SendGrid API Key

1. Log into your SendGrid dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it something like "Tetralto Website"
5. Choose **Restricted Access** and select:
   - **Mail Send** (Full Access)
6. Click **Create & View**
7. **Copy the API key** (you won't see it again!)

## Step 3: Configure Environment Variables

Add these environment variables to your Railway project:

### Required Variables:
- `SENDGRID_FORM_API_KEY` - Your SendGrid API key for form notifications
- `SENDGRID_FORM_TO_EMAIL` - Your email address for receiving form notifications

### Optional Variables:
- `SENDGRID_FORM_FROM_EMAIL` - Email address that sends form notifications (default: noreply@tetralto.com)

## Step 4: Set Up Domain Authentication (Recommended)

For better deliverability, authenticate your domain:

1. In SendGrid dashboard, go to **Settings** → **Sender Authentication**
2. Choose **Domain Authentication**
3. Follow the setup wizard
4. Add the required DNS records to your domain
5. Wait for verification (can take up to 48 hours)

## Step 5: Test the Configuration

Run this command to test your email setup:

```bash
python manage.py test_email
```

## Step 6: Verify It's Working

1. Submit a contact form on your website
2. Check your email for the notification
3. Check the Django logs for any errors

## Troubleshooting

### Common Issues:

1. **"API Key not configured"**
   - Make sure `SENDGRID_FORM_API_KEY` is set in Railway environment variables

2. **"To email not configured"**
   - Make sure `SENDGRID_FORM_TO_EMAIL` is set to your email address

3. **Emails going to spam**
   - Set up domain authentication
   - Use a professional from email address
   - Avoid spam trigger words

4. **Rate limiting**
   - Free tier: 100 emails/day
   - Upgrade to paid plan for more

## Email Format

When someone submits a contact form, you'll receive an email like:

```
Subject: New Lead: John Doe - 2024-01-15 14:30

New lead submitted on Tetralto Roofing website:

Name: John Doe
Phone: (555) 123-4567
Email: john@example.com
Address: 123 Main St, Anytown, USA

Description: Need roof replacement, shingles are curling and leaking

Submitted: 2024-01-15 14:30:00

Internal Notes: reCAPTCHA: 0.9 | Campaign: GCLID: abc123, Source: google

---
This is an automated notification from your website contact form.
```

## Future Enhancements

Once this is working, you can:

1. **Add HTML email templates** for better formatting
2. **Set up marketing campaigns** for existing customers
3. **Add email analytics** to track open rates
4. **Create automated follow-up sequences**

## Support

If you need help:
- Check SendGrid documentation
- Review Django logs for errors
- Test with the management command
- Contact SendGrid support if needed

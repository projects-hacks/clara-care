# ClaraCare — Email & Domain Infrastructure

## Domain

- **Domain**: `claracare.me`
- **Registrar**: Namecheap (GitHub Student Developer Pack)
- **DNS**: Cloudflare (nameservers pointed from Namecheap for faster propagation)

---

## Inbound Email (Receiving)

- **Service**: Cloudflare Email Routing
- **Address**: `support@claracare.me`
- **Routing**: Auto-forwards to personal Gmail
- **Purpose**: Professional contact address for judges/users — no mail server needed

---

## Outbound Email (Sending Alerts & Digests)

- **Service**: Brevo (formerly Sendinblue) SMTP Relay — Free Tier
- **SMTP Server**: `smtp-relay.brevo.com`
- **Port**: `587`
- **Sender Identity**: `ClaraCare Alerts <alerts@claracare.me>`
- **Daily Limit**: 300 transactional emails/day (free tier)

### DNS Authentication (Anti-Spam)

Three TXT records added to Cloudflare to authorize Brevo:

| Record | Purpose |
|--------|---------|
| **SPF** (`v=spf1`) | Tells email providers Brevo is allowed to send for `claracare.me` |
| **DKIM** (`mail._domainkey`) | Digital signature proving email wasn't tampered with |
| **Brevo verification code** | Confirms domain ownership to Brevo |

### Backend Environment Variables

```bash
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=<brevo-smtp-login>
SMTP_PASSWORD=<brevo-smtp-key>
FROM_EMAIL=alerts@claracare.me
```

### What This Enables

- Cognitive decline alert emails to family members
- Daily wellness digest emails
- PDF report delivery (via Foxit integration)
- All emails land in **primary inbox**, not spam (thanks to SPF + DKIM)

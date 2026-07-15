#!/bin/bash
# ─── PULSE SES Setup Script ──────────────────────────────────────────────────
# Configures Amazon SES for email delivery
# Usage: ./setup-ses.sh sender@email.com recipient@email.com
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SENDER_EMAIL="${1:-}"
RECIPIENT_EMAIL="${2:-}"
REGION="${AWS_REGION:-us-east-1}"

if [ -z "${SENDER_EMAIL}" ] || [ -z "${RECIPIENT_EMAIL}" ]; then
    echo "Usage: ./setup-ses.sh sender@email.com recipient@email.com"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          PULSE - SES Configuration                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Verify sender email
echo "📧 Verifying sender email: ${SENDER_EMAIL}"
aws ses verify-email-identity \
    --email-address ${SENDER_EMAIL} \
    --region ${REGION}
echo "✅ Verification email sent to ${SENDER_EMAIL}"

# Verify recipient email (required in sandbox mode)
echo "📧 Verifying recipient email: ${RECIPIENT_EMAIL}"
aws ses verify-email-identity \
    --email-address ${RECIPIENT_EMAIL} \
    --region ${REGION}
echo "✅ Verification email sent to ${RECIPIENT_EMAIL}"

# Create configuration set
echo "⚙️  Creating SES configuration set..."
aws ses create-configuration-set \
    --configuration-set Name=pulse-delivery-config \
    --region ${REGION} 2>/dev/null || echo "  Configuration set already exists"

echo ""
echo "✅ SES setup complete!"
echo ""
echo "IMPORTANT: Check your email inboxes and click the verification links."
echo "While in sandbox mode, both sender and recipient must be verified."
echo ""
echo "To move out of sandbox mode:"
echo "  aws ses put-account-details --production-access-enabled"
echo ""

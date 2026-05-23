/**
 * mail.js - HQ Secure Email Utility
 * Placeholder for future email integration (SMTP/SendGrid/NodeMailer)
 */

async function sendHQMail(to, subject, body) {
    console.log(`[MAIL_LOG] Sending to: ${to} | Subject: ${subject}`);
    // Setup SMTP transport here
    return { success: true, message: "MAIL_QUEUED" };
}

module.exports = { sendHQMail };

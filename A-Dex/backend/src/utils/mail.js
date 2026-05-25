const nodemailer = require('nodemailer');

/**
 * mail.js - HQ Secure Email Utility
 * Integrates with SMTP providers for real-time operator notifications.
 */

async function sendHQMail(to, subject, body) {
    console.log(`[MAIL_LOG] Initializing secure dispatch to: ${to}`);
    
    try {
        // Use environment variables for secure SMTP configuration
        const transporter = nodemailer.createTransport({
            host: process.env.SMTP_HOST || 'smtp.gmail.com',
            port: parseInt(process.env.SMTP_PORT || '587'),
            secure: false, // true for 465, false for other ports
            auth: {
                user: process.env.SMTP_USER, 
                pass: process.env.SMTP_PASS, 
            },
        });

        const info = await transporter.sendMail({
            from: `"RealHackers HQ" <${process.env.SMTP_USER}>`,
            to: to,
            subject: `[HQ_ALERT] ${subject}`,
            text: body,
            html: `
                <div style="background: #000; color: #fff; padding: 20px; font-family: monospace; border: 1px solid #333;">
                    <h2 style="color: #e74c3c; border-bottom: 1px solid #222; padding-bottom: 10px;">SYSTEM_NOTIFICATION</h2>
                    <p style="font-size: 14px; line-height: 1.6;">${body.replace(/\n/g, '<br>')}</p>
                    <div style="margin-top: 30px; font-size: 10px; color: #444;">
                        GEN_TIMESTAMP: ${new Date().toISOString()}<br>
                        ORIGIN: HQ_COMMAND_CENTER
                    </div>
                </div>
            `,
        });

        console.log(`[MAIL_SUCCESS] Message ID: ${info.messageId}`);
        return { success: true, messageId: info.messageId };
    } catch (error) {
        console.error(`[MAIL_ERROR] Dispatch failed: ${error.message}`);
        return { success: false, error: error.message };
    }
}

module.exports = { sendHQMail };

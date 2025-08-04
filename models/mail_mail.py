import logging
from odoo import models, tools

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        """Override to modify reply-to header before sending."""
        # Get the configured reply-to email to intercept
        intercept_email = self.env['ir.config_parameter'].sudo().get_param(
            'mail_reply_to_interceptor.reply_to_intercept_email', ''
        )
        
        # Process each mail record to modify reply-to if needed
        for mail in self:
            if mail.reply_to and intercept_email:
                # Extract email from reply-to (might be in "Name <email>" format)
                reply_to_email = self._extract_email_address(mail.reply_to)
                
                if reply_to_email == intercept_email.strip():
                    # Extract sender email from email_from
                    sender_email = self._extract_email_address(mail.email_from)
                    
                    if sender_email:
                        # Add sender email to reply-to
                        modified_reply_to = self._add_sender_to_reply_to(mail.reply_to, sender_email)
                        mail.write({'reply_to': modified_reply_to})
                        
                        _logger.debug(
                            'Modified reply-to for mail ID %s: %s -> %s (intercept email: %s)',
                            mail.id, mail.reply_to, modified_reply_to, intercept_email
                        )
        
        return super()._send(auto_commit=auto_commit, raise_exception=raise_exception, smtp_session=smtp_session)
    
    def _extract_email_address(self, email_string):
        """Extract email address from a string that might be in 'Name <email>' format."""
        if not email_string:
            return ''
        
        # Use email normalization to extract just the email part
        normalized = tools.mail.email_normalize(email_string)
        return normalized or ''
    
    def _add_sender_to_reply_to(self, reply_to, sender_email):
        """Add sender email to reply-to if it's not already present."""
        if not sender_email:
            return reply_to
        
        # Normalize existing reply-to emails
        existing_emails = tools.mail.email_normalize_all(reply_to)
        
        # Check if sender email is already in reply-to
        if sender_email not in existing_emails:
            # Add sender email to reply-to
            return f"{reply_to},{sender_email}"
        
        return reply_to
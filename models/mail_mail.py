import logging
from odoo import models, tools

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        """Override to modify reply-to header before sending."""
        _logger.info("DEBUG: mail_reply_to_interceptor _send method called with %d mails", len(self))
        
        # Get the configured reply-to email to intercept
        intercept_email = self.env['ir.config_parameter'].sudo().get_param(
            'mail_reply_to_interceptor.reply_to_intercept_email', ''
        )
        _logger.info("DEBUG: intercept_email configured as: '%s'", intercept_email)
        
        # Process each mail record to modify reply-to if needed
        for mail in self:
            _logger.info("DEBUG: Processing mail ID %s, reply_to='%s', email_from='%s'", 
                        mail.id, mail.reply_to, mail.email_from)
            
            if mail.reply_to and intercept_email:
                # Extract email from reply-to (might be in "Name <email>" format)
                reply_to_email = self._extract_email_address(mail.reply_to)
                _logger.info("DEBUG: Extracted reply_to_email: '%s'", reply_to_email)
                
                if reply_to_email == intercept_email.strip():
                    # Extract sender email from email_from
                    sender_email = self._extract_email_address(mail.email_from)
                    _logger.info("DEBUG: Extracted sender_email: '%s'", sender_email)
                    
                    if sender_email:
                        # Add sender email to reply-to
                        modified_reply_to = self._add_sender_to_reply_to(mail.reply_to, sender_email)
                        _logger.info("DEBUG: About to call _add_sender_to_reply_to with reply_to='%s', sender_email='%s'", 
                                   mail.reply_to, sender_email)
                        mail.write({'reply_to': modified_reply_to})
                        
                        _logger.info(
                            'Modified reply-to for mail ID %s: %s -> %s (intercept email: %s)',
                            mail.id, mail.reply_to, modified_reply_to, intercept_email
                        )
                else:
                    _logger.info("DEBUG: Reply-to email '%s' does not match intercept email '%s'", 
                               reply_to_email, intercept_email.strip())
            else:
                if not mail.reply_to:
                    _logger.info("DEBUG: No reply_to field in mail ID %s", mail.id)
                if not intercept_email:
                    _logger.info("DEBUG: No intercept_email configured")
        
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
        _logger.info("DEBUG: _add_sender_to_reply_to called with reply_to='%s', sender_email='%s'", 
                   reply_to, sender_email)
        
        if not sender_email:
            _logger.info("DEBUG: No sender_email provided, returning original reply_to")
            return reply_to
        
        # Parse existing reply-to emails (email_normalize_all doesn't exist in v13)
        existing_emails = []
        if reply_to:
            # Split by comma and normalize each email
            for email in reply_to.split(','):
                normalized = tools.mail.email_normalize(email.strip())
                if normalized:
                    existing_emails.append(normalized)
        
        _logger.info("DEBUG: Existing emails in reply_to: %s", existing_emails)
        
        # Normalize sender email for comparison
        normalized_sender = tools.mail.email_normalize(sender_email)
        _logger.info("DEBUG: Normalized sender email: '%s'", normalized_sender)
        
        # Check if sender email is already in reply-to
        if normalized_sender and normalized_sender not in existing_emails:
            # Add sender email to reply-to
            result = f"{reply_to},{sender_email}"
            _logger.info("DEBUG: Adding sender to reply-to, result: '%s'", result)
            return result
        else:
            _logger.info("DEBUG: Sender email already present in reply-to, not adding")
        
        return reply_to
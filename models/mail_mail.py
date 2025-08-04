import re
import logging
from odoo import models, tools

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _prepare_outgoing_list(self, mail_server=False, recipients_follower_status=None):
        """Override to modify reply-to header when needed."""
        results = super()._prepare_outgoing_list(
            mail_server=mail_server,
            recipients_follower_status=recipients_follower_status
        )
        print("Intercepting reply-to emails... {}".format(results))
        # Get the configured reply-to email to intercept
        intercept_email = self.env['ir.config_parameter'].sudo().get_param(
            'mail_reply_to_interceptor.reply_to_intercept_email', ''
        )
        
        # Process each result to modify reply-to if needed
        for result in results:
            original_reply_to = result.get('reply_to', '')
            email_from = result.get('email_from', '')
            
            # Only modify if reply-to contains the configured intercept email
            # Extract email from reply-to (might be in "Name <email>" format)
            reply_to_email = self._extract_email_address(original_reply_to)
            if original_reply_to and intercept_email and reply_to_email == intercept_email.strip():
                # Extract sender email from email_from (in case it's in "Name <email>" format)
                sender_email = self._extract_email_address(email_from)
                
                if sender_email:
                    # Add sender email to reply-to
                    modified_reply_to = self._add_sender_to_reply_to(original_reply_to, sender_email)
                    result['reply_to'] = modified_reply_to
                    
                    _logger.debug(
                        'Modified reply-to for mail ID %s: %s -> %s (intercept email: %s)',
                        self.id, original_reply_to, modified_reply_to, intercept_email
                    )
        
        return results
    
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
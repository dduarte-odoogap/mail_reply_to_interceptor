from odoo.tests import TransactionCase


class TestMailReplyToInterceptor(TransactionCase):

    def setUp(self):
        super().setUp()
        self.mail_mail = self.env['mail.mail']
        
    def test_extract_email_address(self):
        """Test email address extraction from different formats."""
        mail = self.mail_mail.browse()
        
        # Test simple email
        result = mail._extract_email_address('test@example.com')
        self.assertEqual(result, 'test@example.com')
        
        # Test name with email format
        result = mail._extract_email_address('John Doe <john@example.com>')
        self.assertEqual(result, 'john@example.com')
        
        # Test empty string
        result = mail._extract_email_address('')
        self.assertEqual(result, '')
        
    def test_add_sender_to_reply_to(self):
        """Test adding sender email to reply-to header."""
        mail = self.mail_mail.browse()
        
        # Test adding sender to existing reply-to
        result = mail._add_sender_to_reply_to('admin@example.com', 'sender@example.com')
        self.assertEqual(result, 'admin@example.com,sender@example.com')
        
        # Test not adding duplicate sender
        result = mail._add_sender_to_reply_to('admin@example.com,sender@example.com', 'sender@example.com')
        self.assertEqual(result, 'admin@example.com,sender@example.com')
        
        # Test empty sender
        result = mail._add_sender_to_reply_to('admin@example.com', '')
        self.assertEqual(result, 'admin@example.com')
        
    def test_send_integration(self):
        """Test the complete reply-to modification integration."""
        # Set the intercept email parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'mail_reply_to_interceptor.reply_to_intercept_email', 
            'catchall@domain1.local'
        )
        
        # Create a test mail record with the intercept email as reply-to
        mail = self.mail_mail.create({
            'email_from': 'Test Sender <sender@example.com>',
            'email_to': 'recipient@example.com',
            'reply_to': 'catchall@domain1.local',
            'subject': 'Test Email',
            'body_html': '<p>Test content</p>',
            'state': 'outgoing',  # Required for _send to process
        })
        
        # Mock the parent _send method to avoid actual email sending
        original_reply_to = mail.reply_to
        
        # Call _send method (this will modify reply_to)
        with self.assertRaises(Exception):
            # _send will fail due to missing mail server, but reply_to should be modified first
            mail._send()
        
        # Refresh the record to get updated values
        mail.refresh()
        
        # Check that reply-to was modified before the send attempt
        self.assertEqual(mail.reply_to, 'catchall@domain1.local,sender@example.com')
        
    def test_send_no_reply_to(self):
        """Test that emails without reply-to are not modified."""
        # Set the intercept email parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'mail_reply_to_interceptor.reply_to_intercept_email', 
            'catchall@domain1.local'
        )
        
        mail = self.mail_mail.create({
            'email_from': 'sender@example.com',
            'email_to': 'recipient@example.com',
            'subject': 'Test Email',
            'body_html': '<p>Test content</p>',
            'state': 'outgoing',
        })
        
        original_reply_to = mail.reply_to  # Should be False/empty
        
        # Call _send method 
        with self.assertRaises(Exception):
            # Will fail due to missing mail server, but should not modify reply_to
            mail._send()
        
        # Refresh and check that reply-to was not modified
        mail.refresh()
        self.assertEqual(mail.reply_to, original_reply_to)
    
    def test_send_non_matching_reply_to(self):
        """Test that emails with non-matching reply-to are not modified."""
        # Set the intercept email parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'mail_reply_to_interceptor.reply_to_intercept_email', 
            'catchall@domain1.local'
        )
        
        # Create a test mail record with a different reply-to
        mail = self.mail_mail.create({
            'email_from': 'Test Sender <sender@example.com>',
            'email_to': 'recipient@example.com',
            'reply_to': 'different@example.com',
            'subject': 'Test Email',
            'body_html': '<p>Test content</p>',
            'state': 'outgoing',
        })
        
        original_reply_to = mail.reply_to
        
        # Call _send method
        with self.assertRaises(Exception):
            # Will fail due to missing mail server, but should not modify reply_to
            mail._send()
        
        # Refresh and check that reply-to was NOT modified
        mail.refresh()
        self.assertEqual(mail.reply_to, original_reply_to)
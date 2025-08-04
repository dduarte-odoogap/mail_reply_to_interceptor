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
        
    def test_prepare_outgoing_list_integration(self):
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
        })
        
        # Call _prepare_outgoing_list
        results = mail._prepare_outgoing_list()
        
        # Check that reply-to was modified
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result['reply_to'], 'catchall@domain1.local,sender@example.com')
        
    def test_prepare_outgoing_list_no_reply_to(self):
        """Test that emails without reply-to are not modified."""
        mail = self.mail_mail.create({
            'email_from': 'sender@example.com',
            'email_to': 'recipient@example.com',
            'subject': 'Test Email',
            'body_html': '<p>Test content</p>',
        })
        
        results = mail._prepare_outgoing_list()
        
        # Check that reply-to is either empty or only contains sender (which is the default behavior)
        self.assertEqual(len(results), 1)
        result = results[0]
        reply_to = result.get('reply_to', '')
        # If reply-to is set, it should be the sender's email (Odoo's default behavior)
        if reply_to:
            self.assertEqual(reply_to, 'sender@example.com')
    
    def test_prepare_outgoing_list_non_matching_reply_to(self):
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
        })
        
        # Call _prepare_outgoing_list
        results = mail._prepare_outgoing_list()
        
        # Check that reply-to was NOT modified
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result['reply_to'], 'different@example.com')
# Testing the Mail Reply-To Interceptor Module

## Manual Testing

To manually test the functionality:

1. **Start Odoo with the module installed:**
   ```bash
   python3 src/18.0/odoo-bin --addons-path ~/git/oe/18.0/,~/git/odoo/18.0/addons,~/my/xplore/odoo18.0/addons_dduarte -d v18_test_intercept
   ```

2. **Configure the intercept email (optional - default is catchall@domain1.local):**
   ```python
   # In Odoo shell
   env['ir.config_parameter'].sudo().set_param(
       'mail_reply_to_interceptor.reply_to_intercept_email', 
       'your-catchall@yourdomain.com'
   )
   ```

3. **Create test mail records:**
   ```python
   # Test 1: Mail with matching reply-to (should be intercepted)
   mail1 = env['mail.mail'].create({
       'email_from': 'Test Sender <sender@example.com>',
       'email_to': 'recipient@example.com',
       'reply_to': 'catchall@domain1.local',  # This matches the configured intercept email
       'subject': 'Test Email',
       'body_html': '<p>Test content</p>',
   })
   
   results1 = mail1._prepare_outgoing_list()
   print(results1[0]['reply_to'])  # Should show: catchall@domain1.local,sender@example.com
   
   # Test 2: Mail with different reply-to (should NOT be intercepted)
   mail2 = env['mail.mail'].create({
       'email_from': 'Test Sender <sender@example.com>',
       'email_to': 'recipient@example.com',
       'reply_to': 'different@example.com',  # This does NOT match
       'subject': 'Test Email 2',
       'body_html': '<p>Test content</p>',
   })
   
   results2 = mail2._prepare_outgoing_list()
   print(results2[0]['reply_to'])  # Should show: different@example.com (unchanged)
   ```

4. **Test scenarios:**
   - Mail with matching reply-to: Sender gets added
   - Mail with non-matching reply-to: No modification
   - Mail without reply-to: No modification

## Automated Testing

Run the test suite:
```bash
python3 src/18.0/odoo-bin --addons-path ~/git/oe/18.0/,~/git/odoo/18.0/addons,~/my/xplore/odoo18.0/addons_dduarte -d v18_test_intercept --test-enable --test-tags=mail_reply_to_interceptor --stop-after-init
```

All tests should pass with output:
```
0 failed, 0 error(s) of 5 tests when loading database 'v18_test_intercept'
```
# Mail Reply-To Interceptor

This Odoo module intercepts outgoing emails with specific reply-to addresses and adds the sender's email address.

## Functionality

The module only intercepts emails when the reply-to matches a configured email address:
- Configure the target email via system parameter: `mail_reply_to_interceptor.reply_to_intercept_email`
- Default value: `catchall@domain1.local`
- When an email has reply-to matching this configured address, the sender is added
- Result: `reply-to=catchall@domain1.local,sender@example.com`

## Features

- Automatically extracts email addresses from "Name <email>" format
- Prevents duplicate email addresses in reply-to
- Only modifies emails that already have a reply-to value
- Includes comprehensive test coverage

## Installation

1. Place the module in your Odoo addons directory
2. Update the addon list
3. Install the module from Apps menu

## Dependencies

- `mail` (Odoo core mail module)

## Technical Details

The module extends the `mail.mail` model and overrides the `_send` method to modify the reply-to header before emails are sent.

**Note:** This is the Odoo 13.0 version. For Odoo 18.0, see the v18 branch which uses `_prepare_outgoing_list` method.

## Testing

The module includes unit tests that can be run with:
```bash
odoo-bin -u mail_reply_to_interceptor --test-tags=mail_reply_to_interceptor --stop-after-init
```
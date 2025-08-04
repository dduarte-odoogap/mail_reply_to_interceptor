{
    'name': 'Mail Reply-To Interceptor',
    'version': '13.0.1.0.0',
    'summary': 'Intercept specific reply-to emails and add sender address',
    'description': """
        This module intercepts outgoing emails with a specific reply-to address
        and adds the sender's email address to the reply-to header.
        
        Configure the email to intercept via system parameter:
        mail_reply_to_interceptor.reply_to_intercept_email
        
        Example: if reply-to=catchall@domain1.local and sender=user@company.com
        Result: reply-to=catchall@domain1.local,user@company.com
    """,
    'author': 'DD Uarte',
    'license': 'LGPL-3',
    'depends': ['mail'],
    'demo': [
        'data/ir_config_parameter_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
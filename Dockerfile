FROM odoo:13

# Switch to root to install dependencies and copy files
USER root

# Copy the custom module and configuration
COPY . /mnt/extra-addons/mail_reply_to_interceptor/
COPY odoo.conf /etc/odoo/odoo.conf

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons/mail_reply_to_interceptor
RUN chown odoo:odoo /etc/odoo/odoo.conf

# Switch back to odoo user
USER odoo

# Set environment variables for testing
ENV ODOO_RC /etc/odoo/odoo.conf
ENV ADDONS_PATH /mnt/extra-addons

# Expose Odoo port
EXPOSE 8069

# Default command will be inherited from base odoo:13 image
# Which runs: odoo --addons-path=/mnt/extra-addons
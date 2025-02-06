from odoo import models
from markupsafe import Markup

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        # Update the record and capture changes
        message = self._post_changes_in_chatter(self, vals)
        res = super(ProductTemplate, self).write(vals)
        # Post a message to the chatter about the changes
        if message:
            message = Markup('<ul>%s</ul>') % (message)
            self.message_post(body=message)
        return res

    def _post_changes_in_chatter(self, record, vals=None):
        """
        Post a message in the chatter when fields are created or updated.
        """
        messages = []
        fields_metadata = self.fields_get()
        # Track changes to fields during updates
        for field, new_value in vals.items():
            old_value = getattr(record, field)
            if old_value != new_value:
                messages.append("{}: {} => {}".format(fields_metadata[field]['string'], old_value, new_value))

        message = Markup().join(Markup('<li>%s</li>') % description for description in messages)
        return message


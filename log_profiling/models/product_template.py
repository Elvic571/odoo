from odoo import models, fields
from markupsafe import Markup

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        for rec in self:
            # Update the record and capture changes
            # message = self._post_changes_in_chatter(self, vals)
            old_values = {}
            for field, new_value in vals.items():
                if field not in old_values:
                    old_values[field] = None
                old_values[field] = getattr(rec, field)

            res = super(ProductTemplate, rec).write(vals)

            message = rec._post_changes_in_chatter(old_values, rec, vals)
            # Post a message to the chatter about the changes
            if message:
                message = Markup('<ul>%s</ul>') % (message)
                rec.message_post(body=message)
            return res

    def _post_changes_in_chatter(self, record, latest_rec, vals=None):
        """
        Post a message in the chatter when fields are created or updated.
        """
        for rec in self:
            messages = []
            fields_metadata = rec.fields_get()
            # Track changes to fields during updates
            for field, new_value in vals.items():
                old_value = record[field]
                if isinstance(old_value, models.Model):
                    if isinstance(new_value, list):
                        if sorted([rec.id for rec in old_value]) != sorted([rec[1] for rec in new_value]):
                            messages.append("{}: {} => {}".format(fields_metadata[field]['string'], [rec.name for rec in old_value], [tag.name for rec in latest_rec for tag in rec.product_tag_ids]))
                            continue
                    else:
                        if [rec.id for rec in old_value] != [new_value]:
                            messages.append("{}: {} => {}".format(fields_metadata[field]['string'], [rec.name for rec in old_value], [tag.name for rec in latest_rec for tag in rec.categ_id]))
                            continue
                if old_value != new_value:
                    messages.append("{}: {} => {}".format(fields_metadata[field]['string'], old_value, new_value))

            message = Markup().join(Markup('<li>%s</li>') % description for description in messages)
            return message


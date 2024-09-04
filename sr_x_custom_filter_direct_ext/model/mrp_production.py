from odoo import models, fields, api


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    attribute_values = fields.Char(string='Attribute Values', compute='_compute_attribute_values', store=True)
    Product_internal_reference = fields.Char(related='product_id.default_code', string="Product Internal Reference")

    @api.depends('product_id')
    def _compute_attribute_values(self):
        for rec in self:
            list_ = []
            list2 = []
            for attribute in rec.product_id.product_template_variant_value_ids:
                if 'Merv' in attribute.name:
                    list_.append(attribute.name)
                else:
                    list2.append(attribute.name)
            list_main = list_ + list2
            rec.attribute_values = ', '.join(list_main)
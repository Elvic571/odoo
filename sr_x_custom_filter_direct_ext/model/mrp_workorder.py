from odoo import models, fields, api


class work_order(models.Model):
    _inherit = 'mrp.workorder'

    attribute_values = fields.Char(string='Attribute Values', compute='_compute_attribute_values', store=True)
    Product_internal_reference = fields.Char(related='product_id.default_code', string="Product Internal Reference")

    # @api.depends('product_id')
    # def _compute_attribute_values(self):
    #     for rec in self:
    #         attribute_names = []
    #         if rec.product_id:
    #             for attribute in rec.product_id.product_template_variant_value_ids:
    #                 attribute_names.append(attribute.name)
    #         rec.attribute_values = ', '.join(attribute_names)

    def action_open_label_type(self):
        # Map finished move lines from the work order
        move_line_ids = self.production_id.move_finished_ids.mapped('move_line_ids')

        # Check if the user belongs to the required group and lots exist
        if self.user_has_groups('stock.group_production_lot') and move_line_ids.lot_id:
            view = self.env.ref('stock.picking_label_type_form')
            return {
                'name': _('Choose Type of Labels To Print'),
                'type': 'ir.actions.act_window',
                'res_model': 'picking.label.type',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {'default_production_ids': self.production_id.ids},
            }

        # Fallback to the label layout action
        return self.production_id.action_open_label_layout()

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
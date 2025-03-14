from odoo import models, fields, api

class MrpReport(models.Model):
    _inherit = "mrp.report"

    product_tmpl_id = fields.Many2one("product.template", string="Product Template")

    def _select(self):
        select_str = super()._select()
        select_str += ", pp.product_tmpl_id AS product_tmpl_id"
        return select_str

    def _from(self):
        from_str = super()._from()
        from_str += """
            LEFT JOIN product_product pp ON pp.id = mo.product_id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        """
        return from_str

    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ", pp.product_tmpl_id"
        return group_by_str

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

    # a temporary patch to fix the issue described here https://github.com/odoo/odoo/pull/194325
    def write(self, vals):
        if 'date_start' in vals:
            vals['date_start'] = fields.Datetime.to_datetime(vals['date_start'])
        return super(mrp_production, self).write(vals)

    def _log_downside_manufactured_quantity(self, moves_modification, cancel=False):

        def _keys_in_groupby(move):
            """ Group by picking and the responsible for the product in the move. """
            return (move.picking_id, move.product_id.responsible_id)

        def _render_note_exception_quantity_mo(rendering_context):
            values = {
                'production_order': self,
                'order_exceptions': rendering_context,
                'impacted_pickings': False,
                'cancel': cancel
            }
            return self.env['ir.qweb']._render('mrp.exception_on_mo', values)

        # Get the documents related to the modified moves
        documents = self.env['stock.picking']._log_activity_get_documents(
            moves_modification,
            'move_dest_ids',
            'DOWN',
            _keys_in_groupby
        )

        # Add additional documents where quantities are less than expected
        documents = self.env['stock.picking']._less_quantities_than_expected_add_documents(
            moves_modification,
            documents
        )

        # ✅ Filter out pickings that are already in "done" state
        # filtered_documents = {key: value for key, value in documents.items() if key[0].state != 'done'}

        # updated version of the filter
        current_user = self.env.user
        filtered_documents = {
            key: value for key, value in documents.items()
            if key[0].state != 'done' and key[1] != current_user  # key[1] is the responsible_id
        }

        # Log activity only for pickings that are NOT done
        self.env['stock.picking']._log_activity(_render_note_exception_quantity_mo, filtered_documents)

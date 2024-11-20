import time

from odoo import models, fields, api, _


class Stock_Picking_Type(models.Model):
    _inherit = 'stock.picking.type'

    activate_manufacturing_bot = fields.Boolean(string='Activate Manufacturing Bot')


class Mrp_production(models.Model):
    _inherit = 'mrp.production'

    # override for bot2.1 working, conditions and domain will be triggered from automation rule
    def button_mark_done(self):
        if len(self) > 1:
            return super().button_mark_done()

        if self.picking_type_id.activate_manufacturing_bot == True:
            try:
                res = super().button_mark_done()
                return res
            finally:
                new_order_number = self.name.split('-')[0] + '-' + str(self.backorder_sequence + 1).zfill(3)
                new_production = self.env['mrp.production'].search([('name', '=', new_order_number)], limit=1)
                if new_production:
                    new_production.bot2_1()
        else:
            res = super().button_mark_done()
            return res

    def bot2_1(self):
        current_user = self.env.user
        for production in self:
            if production.workorder_ids and production.workorder_ids[0].state != 'progress':
                if current_user.employee_id:
                    production.workorder_ids[0].with_user(current_user.id).button_start()
                    production.message_post(
                        body="The work order in this manufacturing order has been automatically started by Manufacturing Bot (an extra app called manufacturing_bot_2) to make MO Readiness parameter to be set as Ready so that from under Barcode application the MO gets visible")
                else:
                    production.message_post(
                        body="Manufacturing Bot (an extra app called manufacturing_bot_2) failed to start the work order because there is no employee assigned to a current user")

        self.sudo()._compute_reservation_state()
from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    mf_vendor_no = fields.Char('MervFilters Vendor Number')
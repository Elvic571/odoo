# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Manufacturing Bot',
    'version': '1.0',
    'sequence': 160,
    'category': 'Productivity',
    'depends': ['base', 'mrp', 'mrp_workorder'],

    'data': [
        'views/stock_picking_type_view.xml',

    ],
    'license': 'LGPL-3',


}

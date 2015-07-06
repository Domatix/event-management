# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Analytic Quotation',
    'version': '0.1',
    'author': 'Domatix',
    'summary': 'Analytic Quotation',
    'website': 'http://www.domatix.com',
    'images': [],
    'depends': ['analytic_attendees', 'stock_account'],
    'category': 'Event Management',
    'description': """
        Analytic Quotation provides a group of concept for manage the Quotation
    associated  whit the Analytic.
    """,
    'data': [
             'security/ir.model.access.csv',
             'wizard/account_invoice_view.xml',
             'data/product_data.xml',
             'views/quotation_item_view.xml',
             'views/analytic_view.xml',
             'views/product_view.xml',
             'report/crm_quotation_report.xml',
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

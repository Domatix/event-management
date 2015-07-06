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

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class CreateInvoice(models.TransientModel):
    _name = "create.invoice"
    _description = "Create Invoice"

    @api.depends('invoice_mode')
    @api.onchange('invoice_mode')
    @api.multi
    @api.model
    def onchange_invoice_mode(self):
        analytic = self.env['account.analytic.account']
        contract = analytic.browse(self._context.get('active_ids'))
        invoice_amount = 0.0
        self.quotation_amount = 0.0
        self.percent = 0.0
        quotation_amount = contract.total_price or contract.total_item_price
        if self.invoiced_amount == quotation_amount:
            raise ValidationError(_("The amount total was be invoiced"))
        if self.invoice_mode:
            if self.invoice_mode == 'advance':
                m_data = self.env['ir.model.data']
                product_id = \
                    m_data.xmlid_to_res_id('analytic_quotation.product_advance'
                                           )
                product = self.env['product.product'].browse(product_id)
                invoice_amount = product.list_price
            elif self.invoice_mode == 'percent':
                self.quotation_amount = quotation_amount
            elif self.invoice_mode == 'rest':
                if self.invoiced_amount == 0:
                    raise ValidationError(_("Please, before create "
                                            "the advance invoice."))
                invoice_amount = quotation_amount - self.invoiced_amount
            if invoice_amount > quotation_amount:
                raise ValidationError(_("The amount to invoice cannot "
                                        "be more than quotation amount."))
            else:
                self.invoice_amount = invoice_amount

    @api.depends('quotation_amount', 'percent')
    @api.onchange('quotation_amount', 'percent')
    @api.multi
    def onchange_percent(self):
        invoice_amount = 0
        if self.invoice_mode == 'percent':
            result = self.quotation_amount - self.invoiced_amount
            if self.quotation_amount and self.percent:
                invoice_amount = self.quotation_amount * self.percent / 100
            if invoice_amount > result:
                raise ValidationError(_('The amount to invoice cannot ' +
                                        'be more than: "%d"') % (result))
        self.invoice_amount = invoice_amount

    @api.multi
    def _compute_invoiced(self):
        analytic = self.env['account.analytic.account']
        contract = analytic.browse(self._context.get('active_ids'))
        model_data = self.env['ir.model.data']
        product_advance = \
            model_data.xmlid_to_res_id('analytic_quotation.product_advance')
        product_event = \
            model_data.xmlid_to_res_id('analytic_quotation.product_event')
        product_id = [product_advance, product_event]
        invoice_line = self.env['account.invoice.line']
        lines = invoice_line.search([('origin', '=', contract.name),
                                     ('product_id', 'in', product_id),
                                     ('account_analytic_id', '=', contract.id)
                                     ])
        invoiced = 0
        for line in lines:
            invoiced += line.price_subtotal
        self.invoiced_amount = invoiced

    date = fields.Date(string='Invoice Date', required=True,
                       default=fields.date.today())
    invoice_mode = fields.Selection([('advance', 'Invoice advance'),
                                     ('percent', 'Invoice percent'),
                                     ('rest', 'Invoice rest')
                                     ], 'Show Mode', defaul='advance',
                                    required=True)
    invoice_amount = fields.Float('Amount')
    quotation_amount = fields.Float('Quotation Amount')
    invoiced_amount = fields.Float('Invoiced Amount',
                                   compute='_compute_invoiced')
    percent = fields.Float('Percent (%)')

    @api.multi
    def create_invoice(self):
        analytic = self.env['account.analytic.account']
        contract = analytic.browse(self._context.get('active_ids'))
        if not contract.quotation_item_ids:
            raise ValidationError(_("Please, add quotation items"))
        total_price = contract.total_price or contract.total_item_price
        if self.invoiced_amount == total_price:
            raise ValidationError(_("The amount total was be invoiced"))
        if self.invoice_mode == 'rest':
            model_data = self.env['ir.model.data']
            product_id = \
                model_data.xmlid_to_res_id('analytic_quotation.product_event')
        else:
            model_data = self.env['ir.model.data']
            product_id = \
                model_data.xmlid_to_res_id('analytic_quotation.product_advance'
                                           )
        values = contract._prepare_invoice(product_id, self.invoice_amount,
                                           self.date)
        self.env['account.invoice'].create(values)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

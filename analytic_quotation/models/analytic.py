from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class Analytic(models.Model):
    _inherit = "account.analytic.account"

    @api.one
    @api.onchange('template_id')
    def onchange_compute_items(self):
        quotation_item_ids = []
        if self.template_id:
            values = self.on_change_template(self.template_id.id)
            if 'value' in values:
                if 'parent_id' in values['value']:
                    self.parent_id = values['value']['parent_id']
                if 'date_start' in values['value']:
                    self.date_start = values['value']['date_start']
                if 'quantity_max' in values['value']:
                    self.quantity_max = values['value']['quantity_max']
                if 'description' in values['value']:
                    self.description = values['value']['description']
            self.html_description = self.template_id.html_description
            self.attendees_qty = self.template_id.attendees_qty
            self.price_by_attendee = self.template_id.price_by_attendee
            self.event_type = self.template_id.event_type
            self.service_type = self.template_id.service_type
            self.partner_id = self.template_id.partner_id.id
            for item in self.template_id.quotation_item_ids:
                concept_list = []
                for concept in item.concept_ids:
                    concept_values = {'name': concept.name,
                                      'recoverable': concept.recoverable,
                                      'description': concept.description,
                                      'product_id': concept.product_id.id,
                                      'price_sale_unit':
                                      concept.price_sale_unit,
                                      'price_cost': concept.price_cost,
                                      'margin': concept.margin,
                                      'quantity': concept.quantity
                                      }
                    concept_list.append((0, 0, concept_values))
                item_values = {'name': item.name,
                               'type': item.type,
                               'description': item.description,
                               'show': item.show,
                               'show_mode': item.show_mode,
                               'settled_price': item.settled_price,
                               'composed_price': item.composed_price,
                               'price_cost_total': item.price_cost_total,
                               'margin': item.margin,
                               'concept_ids': concept_list
                               }
                quotation_item_ids.append((0, 0, item_values))
        self.quotation_item_ids = quotation_item_ids

    @api.one
    @api.onchange('quotation_item_ids')
    @api.depends('quotation_item_ids')
    def _compute_total_item_price(self):
        total_item_price = 0
        for item in self.quotation_item_ids:
            if item.type == 'settled':
                total_item_price += item.settled_price or 0.0
            if item.type == 'composed':
                total_item_price += item.composed_price or 0.0
        self.total_item_price = total_item_price

    @api.one
    @api.onchange('quotation_item_ids')
    @api.depends('quotation_item_ids')
    def _compute_total_cost(self):
        cost = 0
        for item in self.quotation_item_ids:
            cost += item.price_cost_total
        self.total_cost = cost

    html_description = fields.Html('HTML Description')
    quotation_item_ids = fields.One2many(
        'analytic.quotation.item', 'analytic_id',
        string='Quotation Items', required=True)
    total_price = fields.Float(
        string='Total Price')
    total_item_price = fields.Float(
        string='Total Item Price',
        compute='_compute_total_item_price')
    total_cost = fields.Float(
        string='Total cost', required=True,
        store=True, readonly=True, compute='_compute_total_cost')

    @api.model
    def _prepare_invoice(self, product_id, amount, date):
        """
        Prepare the dict of values to create the new invoice
        """
        account_journal = self.env['account.journal']
        journal_ids = account_journal.search([('type', '=', 'sale'),
                                              ('company_id', '=',
                                               self.company_id.id)])
        if not journal_ids:
            name = self.company_id.name
            raise ValidationError(_("Please define sales journal "
                                    "for this company: %s.") % (name))

        lines = self._prepare_invoice_line(product_id, amount)
        invoice_vals = {'name': self.name or '',
                        'origin': self.name,
                        'type': 'out_invoice',
                        'reference': self.name,
                        'account_id':
                                self.partner_id.property_account_receivable.id,
                        'partner_id': self.partner_id.id,
                        'journal_id': journal_ids[0].id,
                        'invoice_line': [(0, 0, lines)],
                        'currency_id': self.currency_id.id,
                        'fiscal_position':
                                self.partner_id.property_account_position.id,
                        'date_invoice': date,
                        'company_id': self.company_id.id,
                        'user_id': self.user_id.id,
                        }

        return invoice_vals

    @api.model
    def _prepare_invoice_line(self, product_id, amount):
        """
        Prepare the dict of values to create the new invoice line
        """
        product = self.env['product.product'].browse(product_id)
        account_id = product.categ_id.property_account_income_categ.id
        res = {
            'name': product.name,
            'origin': self.name,
            'account_id': account_id,
            'price_unit': amount,
            'quantity': 1,
            'uom_id': product.uom_id.id,
            'uom_po_id': product.uom_po_id.id,
            'product_id': product.id,
            'account_analytic_id': self.id
        }

        return res

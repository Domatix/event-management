from openerp import models, fields, api, _, tools


class AnalyticQuotationItem(models.Model):
    _name = 'analytic.quotation.item'

    @api.one
    @api.onchange('concept_ids')
    @api.depends('concept_ids')
    def _compute_composed_price(self):
        composed_price = 0
        for concept in self.concept_ids:
            composed_price += concept.price_total
        self.composed_price = composed_price

    @api.one
    @api.onchange('concept_ids')
    @api.depends('concept_ids')
    def _compute_price_cost_total(self):
        price_cost_total = 0
        for concept in self.concept_ids:
            price_cost_total += concept.price_cost
        self.price_cost_total = price_cost_total

    @api.one
    @api.onchange('composed_price', 'settled_price', 'price_cost_total',
                  'type')
    @api.depends('composed_price', 'settled_price', 'price_cost_total', 'type')
    def _compute_margin(self):
        price_total = 0
        if self.type == 'settled':
            price_total = self.settled_price or 0.0
        if self.type == 'composed':
            price_total = self.composed_price or 0.0
        price_cost_total = self.price_cost_total or 0.0
        self.margin = price_total - price_cost_total

    @api.one
    @api.onchange('quotation_item_template_id')
    def onchange_item_template(self):
        if self.quotation_item_template_id:
            item_template = self.quotation_item_template_id
            concept_list = []
            for concept in item_template.concept_ids:
                concept_values = {'name': concept.name,
                                  'recoverable': concept.recoverable,
                                  'product_id': concept.product_id.id,
                                  'price_sale_unit':
                                  concept.price_sale_unit,
                                  'price_cost': concept.price_cost,
                                  'margin': concept.margin,
                                  'quantity': concept.quantity
                                  }
                concept_list.append((0, 0, concept_values))
            self.name = item_template.name
            self.type = item_template.type
            self.description = item_template.description
            self.show = item_template.show
            self.show_mode = item_template.show_mode
            self.settled_price = item_template.settled_price
            self.composed_price = item_template.composed_price
            self.price_cost_total = item_template.price_cost_total
            self.concept_ids = concept_list

    name = fields.Char(string='Description', required=True)
    description = fields.Html('HTML Description')
    show = fields.Boolean('Show')
    show_mode = fields.Selection([('grouped', 'Grouped'),
                                  ('detailed', 'Detailed')], 'Show Mode')
    type = fields.Selection([('settled', 'Settled'),
                             ('composed', 'Composed')],
                            'Type', default="composed", required=True)
    settled_price = fields.Float(string='Settled Price',
                                 help="It is settled by the user")
    composed_price = fields.Float(string='Composed Price', readonly=True,
                                  store=True,
                                  compute='_compute_composed_price',
                                  help="Sum of sale price concept")
    price_cost_total = fields.Float(string='Total Price Cost', required=True,
                                    store=True,
                                    compute='_compute_price_cost_total')
    margin = fields.Float(string='Margin', required=True, store=True,
                          readonly=True, compute='_compute_margin')
    quotation_item_template_id = fields.Many2one('analytic.quotation.item',
                                                 string='Item Template')
    concept_ids = fields.One2many('analytic.quotation.item.concept',
                                  'quotation_item_id',
                                  string='Concepts', required=True)
    analytic_id = fields.Many2one('account.analytic.account',
                                  string='Analytic')


class AnalyticQuotationItemConcept(models.Model):
    _name = 'analytic.quotation.item.concept'

    @api.one
    @api.onchange('price_sale_unit', 'quantity')
    @api.depends('price_sale_unit', 'quantity')
    def _compute_total(self):
        price = self.price_sale_unit or 0.0
        quantity = self.quantity or 0.0
        self.price_total = price * quantity

    @api.one
    @api.onchange('price_sale_unit', 'price_cost')
    @api.depends('price_sale_unit', 'price_cost')
    def _compute_margin(self):
        price_sale_unit = self.price_sale_unit or 0.0
        price_cost = self.price_cost or 0.0
        self.margin = price_sale_unit - price_cost

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_sale_unit = self.product_id.list_price
            self.price_cost = self.product_id.standard_price
            self.description = self.product_id.html_description

    name = fields.Text(string='Description', required=True)
    recoverable = fields.Boolean('Recoverable')
    description = fields.Html('HTML Description')
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='set null',
                                 domain=['|',
                                         ('qty_available', '>', 0),
                                         ('type', '=', 'service')],)
    price_sale_unit = fields.Float(string='Unit Sale Price', required=True)
    price_cost = fields.Float(string='Unit Price Cost', required=True)
    margin = fields.Float(string='Margin', required=True, store=True,
                          readonly=True, compute='_compute_margin')
    quantity = fields.Float(string='Quantity', required=True, default=1)
    price_total = fields.Float(string='Total Price', required=True,
                               store=True, readonly=True,
                               compute='_compute_total')
    quotation_item_id = fields.Many2one('analytic.quotation.item',
                                        string='Quotation Items')

    @api.one
    @api.multi
    def _create_inventory(self):
        if self.product_id and self.product_id.type in ['product', 'consu']:
            name = _('INV: %s') % tools.ustr(self.product_id.name)
            location_id = \
                self.env['stock.location'].search([('usage', '=', 'internal')])
            inventory_values = {'name': name,
                                'product_id': self.product_id.id,
                                'location_id': location_id[0].id,
                                'filter': 'product'}
            inventory = self.env['stock.inventory'].create(inventory_values)
            new_qty = self.product_id.qty_available - self.quantity
            th_qty = self.product_id.qty_available
            line_values = {'inventory_id': inventory.id,
                           'product_qty': new_qty,
                           'location_id': location_id.id,
                           'product_id': self.product_id.id,
                           'product_uom_id': self.product_id.uom_id.id,
                           'theoretical_qty': th_qty}
            self.env['stock.inventory.line'].create(line_values)
            inventory.action_done()
        return True

    @api.model
    def create(self, vals):
        concept = super(AnalyticQuotationItemConcept, self).create(vals)
        concept._create_inventory()
        return concept

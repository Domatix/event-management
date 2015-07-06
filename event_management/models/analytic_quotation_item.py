from openerp import models, fields, api


class QuotationItem(models.Model):
    _inherit = "analytic.quotation.item"

    by_attendee = fields.Boolean(string='By attendee', defaul=False)

    @api.one
    @api.onchange('concept_ids', 'by_attendee')
    @api.depends('concept_ids', 'by_attendee')
    def _compute_composed_price(self):
        super(QuotationItem, self)._compute_composed_price()
        composed_price = self.composed_price
        if self.by_attendee and self.analytic_id:
            composed_price *= self.analytic_id.attendees_qty
        self.composed_price = composed_price

    @api.one
    @api.onchange('quotation_item_template_id')
    def onchange_item_template(self):
        super(QuotationItem, self).onchange_item_template()
        if self.quotation_item_template_id:
            item_template = self.quotation_item_template_id
            self.by_attendee = item_template.by_attendee

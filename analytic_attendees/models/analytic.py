from openerp import models, fields, api


class EventType(models.Model):
    """ Event Type """
    _name = 'event.type'

    name = fields.Char(
        string='Event Type',
        required=True)


class ServiceType(models.Model):
    """ Service Type """
    _name = 'service.type'

    name = fields.Char(
        string='Service Type',
        required=True)


class Analytic(models.Model):
    _inherit = "account.analytic.account"

    @api.one
    @api.onchange('attendees_qty', 'price_by_attendee')
    def onchange_compute_planned_revenue(self):
        if self.attendees_qty and self.price_by_attendee:
            self.planned_revenue = self.attendees_qty * self.price_by_attendee

    @api.one
    @api.onchange('planned_revenue')
    def onchange_compute_price_by_attendee(self):
        if self.planned_revenue and self.attendees_qty:
            self.price_by_attendee = self.planned_revenue / self.attendees_qty

    attendees_qty = fields.Integer(
        string="Attendees's Qty")
    price_by_attendee = fields.Float(
        string='Price by Attendee')
    planned_revenue = fields.Float(
        string="Planned revenue")
    event_type = fields.Many2one(
        'event.type',
        string='Type of Event')
    service_type = fields.Many2one(
        'service.type',
        string='Type of Service')

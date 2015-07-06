from openerp import models, api


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
                               'by_attendee': item.by_attendee,
                               'concept_ids': concept_list
                               }
                quotation_item_ids.append((0, 0, item_values))
        self.quotation_item_ids = quotation_item_ids

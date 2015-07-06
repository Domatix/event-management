# -*- coding: utf-8 -*-
from openerp.tools.misc import mute_logger
from openerp.tests import common
import time


class TestEventManagement(common.TransactionCase):

    def setUp(self):
        super(TestEventManagement, self).setUp()

        self.PartnerObj = self.env['res.partner']
        self.ModelDataObj = self.env['ir.model.data']
        self.ContractObj = self.env['account.analytic.account']
        self.QuotationItemObj = self.env['analytic.quotation.item']
        self.QuotationItemConceptObj = \
            self.env['analytic.quotation.item.concept']

        # Model Data
        self.main_partner = \
            self.ModelDataObj.xmlid_to_res_id('base.main_partner')
        self.product_advance = self.ModelDataObj.xmlid_to_res_id('analytic_quotation.product_advance')
        self.product_event = self.ModelDataObj.xmlid_to_res_id('analytic_quotation.product_event')

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models')
    def test_00_event_management(self):
        """In order to create a quotation item I create the concept."""
#        List of quotation items created
        quotation_item = []
#        dict of concept values to create the first concept
        concept_values1 = [{'name': 'Entrantes',
                            'price_sale_unit': 300,
                            'price_cost': 150,
                            'quantity': 1},
                           {'name': 'Plato principal',
                            'price_sale_unit': 1000,
                            'price_cost': 600,
                            'quantity': 1},
                           {'name': 'Postres',
                            'price_sale_unit': 200,
                            'price_cost': 80,
                            'quantity': 1,
                            }]
#        I create the concept and check the result
        concepts1 = []
        for values in concept_values1:
            concept = self.QuotationItemConceptObj.create(values)
            self.assertTrue(concept, "Concept not created")
#            I compute the margin
            concept._compute_margin()
            price_sale_unit = concept.price_sale_unit
            price_cost = concept.price_cost
#            I check the margin compute
            assert concept.margin == price_sale_unit - price_cost, \
                "The margin concept compute is wrong!"
#            I compute the total price
            concept._compute_total()
            quantity = concept.quantity
#            I check the total price compute
            assert concept.price_total == price_sale_unit * quantity, \
                "The total price compute of concept is wrong!"
            concepts1.append(concept.id)

#        dict of quotation item values to create the first quotation item
        quotation_item_values1 = {'name': 'Partida Menú',
                                  'by_attendee': True,
                                  'type': 'composed',
                                  'price_cost_total': 850,
                                  'concept_ids': [(6, 0, concepts1)]}
#        I create the quotation item and check the result
        quotation_item1 = self.QuotationItemObj.create(quotation_item_values1)
        self.assertTrue(quotation_item1, "Quotation Item not created")
        quotation_item.append(quotation_item1)

#        dict of concept values to create the second concept
        concept_values2 = [{'name': 'Refrescos',
                            'price_sale_unit': 500,
                            'price_cost': 220,
                            'quantity': 1},
                           {'name': 'Bebidas Alcohólicas',
                            'price_sale_unit': 500,
                            'price_cost': 200,
                            'quantity': 1,
                            }]
#        I create the concept and check the result
        concepts2 = []
        for values in concept_values2:
            concept = self.QuotationItemConceptObj.create(values)
            self.assertTrue(concept, "Concept not created")
#            I compute the margin
            concept._compute_margin()
            price_sale_unit = concept.price_sale_unit
            price_cost = concept.price_cost
#            I check the margin compute
            assert concept.margin == price_sale_unit - price_cost, \
                "The margin concept compute is wrong!"
#            I compute the total price
            concept._compute_total()
            quantity = concept.quantity
#            I check the total price compute
            assert concept.price_total == price_sale_unit * quantity, \
                "The total price compute of concept is wrong!"
            concepts2.append(concept.id)

#        dict of quotation item values to create the second quotation item
        quotation_item_values2 = {'name': 'Partida Bebidas',
                                  'type': 'composed',
                                  'price_cost_total': 450,
                                  'concept_ids': [(6, 0, concepts2)]}
#        I create the quotation item and check the result
        quotation_item2 = \
            self.QuotationItemObj.create(quotation_item_values2)
        self.assertTrue(quotation_item2, "Quotation Item not created")
        quotation_item.append(quotation_item2)

#        dict of concept values to create the third concept
        concept_values3 = [{'name': 'RRHH',
                            'price_sale_unit': 3000,
                            'price_cost': 1200,
                            'quantity': 1}]
#        I create the concept and check the result
        concepts3 = []
        for values in concept_values3:
            concept = self.QuotationItemConceptObj.create(values)
            self.assertTrue(concept, "Concept not created")
#            I compute the margin
            concept._compute_margin()
            price_sale_unit = concept.price_sale_unit
            price_cost = concept.price_cost
#            I check the margin compute
            assert concept.margin == price_sale_unit - price_cost, \
                "The margin concept compute is wrong!"
#            I compute the total price
            concept._compute_total()
            quantity = concept.quantity
#            I check the total price compute
            assert concept.price_total == price_sale_unit * quantity, \
                "The total price compute of concept is wrong!"
            concepts3.append(concept.id)

#        dict of quotation item values to create the third quotation item
        quotation_item_values3 = {'name': 'Partida Recursos Humanos',
                                  'type': 'composed',
                                  'price_cost_total': 1320,
                                  'concept_ids': [(6, 0, concepts3)]}
#        I create the quotation item and check the result
        quotation_item3 = self.QuotationItemObj.create(quotation_item_values3)
        self.assertTrue(quotation_item3, "Quotation Item not created")
        quotation_item.append(quotation_item3)

        """In order to create a analytic using the quotation item created"""
        quotation_item_ids = [item.id for item in quotation_item]
#        dict of contract values to create a new contract
        contract_values = {'name': 'Contract X',
                           'code': 'Contract X',
                           'partner_id': self.main_partner,
                           'attendees_qty': 20,
                           'price_by_attendee': 50,
                           'date_start': time.strftime('%Y-%m-%d'),
                           'date': time.strftime('%Y-%m-%d'),
                           'total_price': 34000,
                           'quotation_item_ids': [(6, 0, quotation_item_ids)]}
        contract = self.ContractObj.create(contract_values)
        self.assertTrue(contract, "Contract not created")
#        I check the planned revenue
        contract.onchange_compute_planned_revenue()
        assert contract.planned_revenue == 20 * 50, \
            "The planned revenue is different than 1000!!"

#        After create a lead I check the total price of quotation item
#        using the concept price and checking the option by attendees
        for item in contract.quotation_item_ids:
            item._compute_composed_price()
            composed_price = 0
            for concept in item.concept_ids:
                composed_price += concept.price_total
            if item.by_attendee:
                composed_price *= item.analytic_id.attendees_qty
            assert item.composed_price == composed_price, \
                "The composed price of quotation item computed is wrong!"
#            I check the margin computed
            item._compute_margin()
            margin = composed_price - item.price_cost_total
            assert item.margin == margin, \
                "The margin item computed is wrong!"

#        I check the total price
        contract._compute_total_item_price()
        assert contract.total_item_price == 1500 * 20 + 1000 + 3000, \
            "The total price is different than 34000!"
#        I check the total cost
        contract._compute_total_cost()
        cost = 0
        for item in contract.quotation_item_ids:
            cost += item.price_cost_total
        assert contract.total_cost == cost, \
            "The cost compute for the contract is wrong!"

        """In order to check the invoice create"""
#        Creating the first invoice
        values = contract._prepare_invoice(self.product_advance, 2000,
                                           time.strftime('%Y-%m-%d'))
        invoice1 = self.env['account.invoice'].create(values)
        self.assertTrue(invoice1, "Invoice one no created")

#        Creating the second invoice whit the 30 % of total price
        values = contract._prepare_invoice(self.product_advance, 10200,
                                           time.strftime('%Y-%m-%d'))
        invoice2 = self.env['account.invoice'].create(values)
        self.assertTrue(invoice2, "Invoice two no created")
#        Creating the 3 invoice whit the rest amount
        values = contract._prepare_invoice(self.product_event, 21800,
                                           time.strftime('%Y-%m-%d'))
        invoice3 = self.env['account.invoice'].create(values)
        self.assertTrue(invoice3, "Invoice tree no created")
        """In order to compare the total invoiced whit total price
        of the lead."""
        product_id = [self.product_advance, self.product_event]
        invoice_line = self.env['account.invoice.line']
        lines = invoice_line.search([('origin', '=', contract.name),
                                     ('product_id', 'in', product_id),
                                     ('account_analytic_id', '=', contract.id)
                                     ])
        invoiced = 0
        for line in lines:
            invoiced += line.price_subtotal
#        I compare the total invoiced whit total price of the lead.
        assert invoiced == contract.total_price, \
            "The total invoiced is different than total price of contract!"

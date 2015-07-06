from openerp import models, fields


class product(models.Model):
    _inherit = "product.template"

    html_description = fields.Html('HTML Description')

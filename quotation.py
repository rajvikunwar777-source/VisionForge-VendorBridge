# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VendorBridgeQuotation(models.Model):
    _name = 'vendor.bridge.quotation'
    _description = 'Vendor Quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'price_total asc, delivery_time asc'

    name = fields.Char(string='Quotation Ref', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('vendor.bridge.vendor', string='Vendor', required=True, tracking=True)
    rfq_id = fields.Many2one('vendor.bridge.rfq', string='RFQ Reference', required=True, ondelete='cascade', tracking=True)
    
    product_name = fields.Char(related='rfq_id.product_name', string='Product', readonly=True)
    quantity = fields.Float(related='rfq_id.quantity', string='Quantity', readonly=True)
    unit = fields.Selection(related='rfq_id.unit', string='Unit', readonly=True)
    
    price_unit = fields.Float(string='Quoted Price (Per Unit)', required=True, default=0.0, tracking=True)
    tax_percent = fields.Float(string='Tax (%)', default=0.0, tracking=True)
    discount = fields.Float(string='Discount (%)', default=0.0, tracking=True)
    price_total = fields.Float(string='Total Amount', compute='_compute_price_total', store=True, tracking=True)
    
    delivery_time = fields.Integer(string='Delivery Time (Days)', default=7, tracking=True, help="Expected delivery duration in days")
    warranty = fields.Char(string='Warranty / Guarantee', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True, copy=False)

    @api.depends('price_unit', 'tax_percent', 'discount', 'quantity')
    def _compute_price_total(self):
        for rec in self:
            subtotal = rec.price_unit * rec.quantity
            discount_amt = subtotal * (rec.discount / 100.0)
            taxable_amt = subtotal - discount_amt
            tax_amt = taxable_amt * (rec.tax_percent / 100.0)
            rec.price_total = taxable_amt + tax_amt

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vendor.bridge.quotation') or _('New')
        return super(VendorBridgeQuotation, self).create(vals_list)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_accept(self):
        self.ensure_one()
        if self.state not in ['draft', 'submitted']:
            raise UserError(_("Only draft or submitted quotations can be accepted."))
            
        # Reject other quotations for the same RFQ
        other_quotes = self.search([
            ('rfq_id', '=', self.rfq_id.id),
            ('id', '!=', self.id)
        ])
        if other_quotes:
            other_quotes.write({'state': 'rejected'})

        self.write({'state': 'accepted'})
        self.rfq_id.write({'state': 'done'})

        # Check if PO already exists for this RFQ/Quotation
        existing_po = self.env['vendor.bridge.po'].search([
            ('quotation_id', '=', self.id)
        ])
        
        if not existing_po:
            # Create Purchase Order
            expected_date = fields.Date.add(fields.Date.context_today(self), days=self.delivery_time)
            po = self.env['vendor.bridge.po'].create({
                'vendor_id': self.vendor_id.id,
                'rfq_id': self.rfq_id.id,
                'quotation_id': self.id,
                'amount_total': self.price_total,
                'expected_delivery': expected_date,
                'state': 'draft'
            })
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Purchase Order Created'),
                'view_mode': 'form',
                'res_model': 'vendor.bridge.po',
                'res_id': po.id,
                'target': 'current',
            }

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def name_get(self):
        result = []
        for quote in self:
            name = f"{quote.name} - {quote.vendor_id.name} ({quote.price_total})"
            result.append((quote.id, name))
        return result

    def _compute_display_name(self):
        for quote in self:
            quote.display_name = f"{quote.name} - {quote.vendor_id.name} ({quote.price_total:.2f})"

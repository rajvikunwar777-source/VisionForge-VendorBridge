# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VendorBridgePO(models.Model):
    _name = 'vendor.bridge.po'
    _description = 'Purchase Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='PO Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('vendor.bridge.vendor', string='Vendor', required=True, tracking=True)
    rfq_id = fields.Many2one('vendor.bridge.rfq', string='RFQ Reference', readonly=True, tracking=True)
    quotation_id = fields.Many2one('vendor.bridge.quotation', string='Quotation Reference', readonly=True, tracking=True)
    
    product_name = fields.Char(related='rfq_id.product_name', string='Product', readonly=True)
    quantity = fields.Float(related='rfq_id.quantity', string='Quantity', readonly=True)
    unit = fields.Selection(related='rfq_id.unit', string='Unit', readonly=True)
    
    amount_total = fields.Float(string='Total Amount', required=True, tracking=True)
    order_date = fields.Date(string='Order Date', default=fields.Date.context_today, required=True, tracking=True)
    expected_delivery = fields.Date(string='Expected Delivery Date', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True, copy=False)
    
    approver_id = fields.Many2one('res.users', string='Approver', readonly=True, tracking=True)
    approval_comments = fields.Text(string='Approver Comments', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vendor.bridge.po') or _('New')
        return super(VendorBridgePO, self).create(vals_list)

    def action_submit_approval(self):
        self.write({'state': 'to_approve'})

    def action_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approver_id': self.env.user.id
        })

    def action_reject(self):
        self.ensure_one()
        if not self.approval_comments:
            raise UserError(_("Please add comments explaining the reason for rejection."))
        self.write({
            'state': 'rejected',
            'approver_id': self.env.user.id
        })

    def action_confirm(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Only approved Purchase Orders can be confirmed."))
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_draft(self):
        self.write({'state': 'draft', 'approver_id': False, 'approval_comments': False})

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VendorBridgeRFQ(models.Model):
    _name = 'vendor.bridge.rfq'
    _description = 'Request for Quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='RFQ Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    rfq_date = fields.Date(string='RFQ Date', default=fields.Date.context_today, required=True, tracking=True)
    delivery_date = fields.Date(string='Expected Delivery Date', required=True, tracking=True)
    product_name = fields.Char(string='Product Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', required=True, default=1.0, tracking=True)
    unit = fields.Selection([
        ('unit', 'Units'),
        ('kg', 'Kilograms'),
        ('litre', 'Litres'),
        ('meter', 'Meters'),
        ('box', 'Boxes')
    ], string='Unit', required=True, default='unit', tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High')
    ], string='Priority', default='1', tracking=True)
    vendor_ids = fields.Many2many(
        'vendor.bridge.vendor', 
        'vendor_bridge_rfq_vendor_rel', 
        'rfq_id', 
        'vendor_id', 
        string='Selected Vendors', 
        required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sent', 'Sent to Vendors'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True, copy=False)
    
    approver_id = fields.Many2one('res.users', string='Approver', readonly=True, tracking=True)
    approval_comments = fields.Text(string='Approver Comments', tracking=True)
    
    quotation_ids = fields.One2many('vendor.bridge.quotation', 'rfq_id', string='Vendor Quotations', readonly=True)
    po_ids = fields.One2many('vendor.bridge.po', 'rfq_id', string='Purchase Orders', readonly=True)
    quotation_count = fields.Integer(string='Quotation Count', compute='_compute_quotation_count')
    po_count = fields.Integer(string='PO Count', compute='_compute_po_count')

    @api.depends('quotation_ids')
    def _compute_quotation_count(self):
        for rfq in self:
            rfq.quotation_count = len(rfq.quotation_ids)

    @api.depends('po_ids')
    def _compute_po_count(self):
        for rfq in self:
            rfq.po_count = len(rfq.po_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vendor.bridge.rfq') or _('New')
        return super(VendorBridgeRFQ, self).create(vals_list)

    def action_submit_approval(self):
        self.ensure_one()
        if not self.vendor_ids:
            raise UserError(_("Please add at least one vendor before submitting for approval."))
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

    def action_send_rfq(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Only approved RFQs can be sent to vendors."))
        
        # Auto-create quotation shells for each vendor if they don't exist
        Quotation = self.env['vendor.bridge.quotation']
        for vendor in self.vendor_ids:
            existing = Quotation.search([('rfq_id', '=', self.id), ('vendor_id', '=', vendor.id)])
            if not existing:
                Quotation.create({
                    'rfq_id': self.id,
                    'vendor_id': vendor.id,
                    'state': 'draft'
                })
        self.write({'state': 'sent'})

    def action_set_draft(self):
        self.write({'state': 'draft', 'approver_id': False, 'approval_comments': False})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quotations for %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'vendor.bridge.quotation',
            'domain': [('rfq_id', '=', self.id)],
            'context': {'default_rfq_id': self.id},
        }

    def action_view_pos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Orders for %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'vendor.bridge.po',
            'domain': [('rfq_id', '=', self.id)],
            'context': {'default_rfq_id': self.id},
        }

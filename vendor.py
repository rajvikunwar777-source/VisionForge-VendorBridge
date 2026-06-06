# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class VendorBridgeVendor(models.Model):
    _name = 'vendor.bridge.vendor'
    _description = 'Vendor Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Vendor Name', required=True, tracking=True)
    code = fields.Char(string='Vendor Code', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    contact_person = fields.Char(string='Contact Person', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    address = fields.Text(string='Address')
    gst_number = fields.Char(string='GST Number', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The Vendor Code must be unique!'),
        ('gst_unique', 'unique(gst_number)', 'The GST Number must be unique!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code('vendor.bridge.vendor') or _('New')
        return super(VendorBridgeVendor, self).create(vals_list)

    def name_get(self):
        result = []
        for vendor in self:
            name = f"[{vendor.code}] {vendor.name}" if vendor.code else vendor.name
            result.append((vendor.id, name))
        return result

    # For Odoo 17/18/19 support where name_get is deprecated in favor of _compute_display_name
    def _compute_display_name(self):
        for vendor in self:
            vendor.display_name = f"[{vendor.code}] {vendor.name}" if vendor.code else vendor.name

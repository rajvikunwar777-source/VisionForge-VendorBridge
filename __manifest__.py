# -*- coding: utf-8 -*-
{
    'name': 'VendorBridge',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Procurement & Vendor Management System',
    'description': """
VendorBridge: A complete Odoo 19 custom module for Procurement and Vendor Management.
====================================================================================

Key Features:
-------------
* **Vendor Management**: Profile tracking with GSTIN, address, and status.
* **RFQ Management**: Create RFQs, define required products, quantities, dates, and link multiple vendors.
* **Vendor Quotations**: Record unit prices, tax, discounts, delivery times, and warranties for vendors.
* **Approval Workflow**: Integrated approval controls for managing pending, approved, and rejected states.
* **Purchase Orders**: Automatically compile confirmed quotations into structured Purchase Orders.
    """,
    'author': 'Antigravity',
    'website': 'https://github.com/vishva/vendor_bridge',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/vendor_views.xml',
        'views/rfq_views.xml',
        'views/quotation_views.xml',
        'views/purchase_order_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

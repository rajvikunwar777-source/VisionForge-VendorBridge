# Installation Instructions - VendorBridge Custom Module

Follow these steps to deploy, install, and configure the VendorBridge module on your Odoo 19 server.

## Prerequisites

* **Odoo Version**: Odoo 19.0 (Community or Enterprise).
* **Database**: PostgreSQL 13 or higher.
* **Dependencies**: Standard Odoo dependencies including Python 3.10+ and standard pip packages.

---

## Step 1: Copy Module Folder to Addons

1. Locate your Odoo custom addons directory (e.g. `/path/to/odoo/addons` or a custom directory specified in your configuration file).
2. Extract the `vendor_bridge` zip archive or copy the folder into that custom addons directory.
3. Ensure proper file permissions are set so the Odoo system user can read the files:
   ```bash
   chmod -R 755 vendor_bridge
   chown -R odoo:odoo vendor_bridge
   ```

---

## Step 2: Configure `odoo.conf`

Ensure your custom addons path is included in the Odoo configuration file (`odoo.conf` or `openerp-server.conf`):

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/custom/addons
```

Restart your Odoo server instance to recognize the new folder structure:
```bash
sudo service odoo-server restart
# Or if running via systemd:
sudo systemctl restart odoo
```

---

## Step 3: Install VendorBridge

1. Log into your Odoo database using a web browser with **Administrator** credentials.
2. Activate **Developer Mode** (Settings -> Scroll down -> Click **Activate the developer mode**).
3. Navigate to the **Apps** menu dashboard.
4. Click on **Update Apps List** in the top navigation bar and select **Update** on the confirmation dialog.
5. In the search bar, clear the default "Apps" filter.
6. Search for `VendorBridge`.
7. Click the **Activate** or **Install** button on the VendorBridge app card.

---

## Step 4: Access and Roles

Once installed, navigate to the **VendorBridge** menu item in your sidebar or apps drawer.
To configure approvals:
1. Navigate to **Settings** -> **Users & Companies** -> **Users**.
2. Edit user profiles and assign the following permissions under the **VendorBridge Procurement** category:
   * **User**: Can create RFQs, record Quotations, and confirm POs.
   * **Manager**: Full administrative rights including RFQ/PO approval actions (Approve / Reject).

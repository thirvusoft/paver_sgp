import frappe

def create_scrap_warehouse():
    company = frappe.db.get_value("Company",frappe.db.get_single_value('Global Defaults', 'default_company'))
    abbr = frappe.get_value("Company",company, 'abbr')
    if(not frappe.db.exists('Warehouse', f'Scrap Warehouse - {abbr}')):
        warehouse = frappe.new_doc("Warehouse")
        parent = ''
        if frappe.db.exists("Warehouse", f'All Warehouses - {abbr}'):
            parent = f'All Warehouses - {abbr}'
        warehouse.update({
            'warehouse_name' : 'Scrap Warehouse',
            'parent_warehouse' : parent
        })
        warehouse.save(ignore_permissions=True)

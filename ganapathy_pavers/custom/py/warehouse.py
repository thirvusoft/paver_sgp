import frappe

def create_scrap_warehouse():
    for i in frappe.get_all("Company",pluck='name'):
        abbr = frappe.db.get_value("Company",i,'abbr')        
        if(not frappe.db.exists('Warehouse', f'Scrap Warehouse - {abbr}')):
            warehouse = frappe.new_doc("Warehouse")
            parent = ''
            if frappe.db.exists("Warehouse", f'All Warehouses - {abbr}'):
                parent = f'All Warehouses - {abbr}'
            warehouse.update({
                'warehouse_name' : 'Scrap Warehouse',
                'parent_warehouse' : parent,
                'company' : i
            })
            warehouse.save(ignore_permissions=True)
        if(not frappe.db.exists('Warehouse', f'Remaining Pavers - {abbr}')):
            warehouse = frappe.new_doc("Warehouse")
            parent = ''
            if frappe.db.exists("Warehouse", f'All Warehouses - {abbr}'):
                parent = f'All Warehouses - {abbr}'
            warehouse.update({
                'warehouse_name' : 'Remaining Pavers',
                'parent_warehouse' : parent,
                'company' : i
            })
            warehouse.save(ignore_permissions=True)

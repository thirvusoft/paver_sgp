import frappe

@frappe.whitelist()
def get_parent_work_order_status(bom):
    link = frappe.db.sql(f''' 
            SELECT name as work_order, status
            FROM `tabWork Order`
            WHERE status not in  ('Completed', 'Cancelled') and bom_no = "{bom}" and parent_work_order = "" or parent_work_order is NULL
    ''', as_dict=1)
    child_data = frappe.db.sql(f''' 
        SELECT work_order, status
        FROM `tabWork Order Status`
        WHERE parent = "{bom}"
    ''', as_dict=1)
    if(len(child_data) and link != child_data):
        return link, child_data
    elif(not len(child_data)):
        return link
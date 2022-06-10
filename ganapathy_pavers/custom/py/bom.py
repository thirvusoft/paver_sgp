import frappe

@frappe.whitelist()
def get_parent_work_order_status(bom):
    link = frappe.db.sql(f''' 
            SELECT name as work_order, status
            FROM `tabWork Order`
            WHERE bom_no = "{bom}" and (parent_work_order = "" or parent_work_order is NULL)
    ''', as_dict=1)
    final_wo = []
    status = ['Completed', 'Closed', 'Cancelled']
    for i in link:
        child_wo = frappe.db.sql(f''' 
            SELECT  name as work_order, status
            FROM `tabWork Order`
            WHERE parent_work_order = "{i['work_order']}"
        ''', as_list=1)
        child_wo1 = frappe.db.sql(f''' 
            SELECT  name as work_order, status
            FROM `tabWork Order`
            WHERE parent_work_order = "{child_wo[0][0]}"
        ''', as_list=1)
        if(child_wo[0][1] not in status and child_wo1[0][1] not in status):
                final_wo.append(i)

    return final_wo[::-1]
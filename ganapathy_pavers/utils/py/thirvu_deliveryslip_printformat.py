import frappe

def print_format(docname):
    same_item=  frappe.db.sql("""select dn_item.item_name , sum(dn_item.ts_qty) as bundle,count(dn_item.item_code) as count from `tabDelivery Note Item` as dn_item where parent=%s group by dn_item.item_code having count(dn_item.item_code)>1 """,docname,as_dict=1)
    return same_item
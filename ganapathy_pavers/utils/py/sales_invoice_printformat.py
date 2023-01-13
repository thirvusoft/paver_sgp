
import frappe

def sales_invoice_print_format(docname):
    sales_item=  frappe.db.sql("""select si_item.item_name as item_name,si_item.print_item_name as print_item_name , sum(si_item.qty) as qty, sum(si_item.rate) as rate, sum(si_item.amount) as amount,si_item.gst_hsn_code as hsn_code,si_item.uom as uom from `tabSales Invoice Item` as si_item where parent=%s group by si_item.print_item_name """,docname,as_dict=1)
    print(sales_item)
    return sales_item

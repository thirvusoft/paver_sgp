import frappe
from ganapathy_pavers.utils.py.purchase_invoice import  batch_property_setter
from ganapathy_pavers.custom.py.purchase_invoice import calculate_tax

def execute():
    batch_property_setter()

def item_wise_tax():
    d = frappe.get_all("Purchase Invoice", {"docstatus": 1})
    print('total', len(d))
    i = 0
    for row in d:
        i+=1
        doc = frappe.get_doc("Purchase Invoice", row.name)
        calculate_tax(doc)
        print(i)

#  ganapathy_pavers.patches.purchase_invoice_fixes.item_wise_tax
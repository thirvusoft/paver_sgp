import frappe
import json
from erpnext.controllers.taxes_and_totals import get_itemised_tax
from erpnext.controllers.taxes_and_totals import get_itemised_taxable_amount
def update_customer(self,event):
    cus=self.customer
    for row in self.items:
        so=row.sales_order
        if(so):
            doc=frappe.get_doc('Sales Order', so)
            if(cus!=doc.customer):
                frappe.db.set(doc, "customer", cus)


             
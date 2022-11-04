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



def einvoice_validation(self,event):
    accounting=frappe.get_value("Branch",self.branch,"is_accounting")
    if(accounting==1):
        if(not self.transporter and not self.vehicle_no and not self.mode_of_transport):
            frappe.throw("Enter the Transport Details")



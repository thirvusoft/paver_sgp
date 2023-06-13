# import frappe
from ganapathy_pavers.utils.event_sync.sales_invoice import si_validate

def validate(self, event=None):
    if self.ref_doctype == "Sales Invoice":
        si_validate(self, event)

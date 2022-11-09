import frappe

def dn_tax_validation(self, event=None):
    """
        For Delivery Note
    """
    for row in self.items:
        if row.unacc:
            row.item_tax_template=""

def tax_validation(self, event=None):
    """
        For Sales Order and Sales Invoice
    """
    if self.branch and not frappe.get_value("Branch", self.branch, "is_accounting"):
        for row in self.items:
            row.unacc=1
            row.item_tax_template=""
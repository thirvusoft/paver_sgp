import frappe

def update_lead_on_save(self, event = None):
    if self.quotation_to == "Lead" and self.party_name:
        frappe.get_doc("Lead", self.party_name).set_status(update=True, status="Quotation")
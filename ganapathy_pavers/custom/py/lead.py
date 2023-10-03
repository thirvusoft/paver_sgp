import frappe
from erpnext.crm.doctype.lead.lead import Lead

class lead_status(Lead):
    frappe.errprint("dsfsdgdf")
    def validate(self):
        self.set_lead_name()
        self.set_title()
        if self.status not in ["Converted","Completed"]:
            self.set_status()
        self.check_email_id_is_unique()
        self.validate_email_id()
        self.validate_contact_date()
        self.set_prev()

def new_status():
    doc=frappe.new_doc('Property Setter')
    doc.update({
        "doctype_or_field": "DocField",
        "doc_type":"Lead",
        "field_name":"status",
        "property":"options",
        "value":"\nLead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact\nCompleted\nWorking in process\nRaised PO"
    })
    doc.save()
    frappe.db.commit()
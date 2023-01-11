import frappe

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
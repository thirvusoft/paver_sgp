import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
def create_payment_entry(doc,action):
        payment_doc = get_payment_entry(doc.doctype,doc.name)
        company = frappe.get_doc('Company',doc.company)
        abbr=company.abbr
        payment_doc.type="Others"
        payment_doc.branch=doc.branch
        payment_doc.posting_date=doc.posting_date
        payment_doc.paid_from = 'Cash - '+abbr
        payment_doc.save()
        payment_doc.submit()
import frappe
<<<<<<< HEAD
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
def create_payment_entry(doc,action):
        payment_doc = get_payment_entry(doc.doctype,doc.name)
        company = frappe.get_doc('Company',doc.company)
        abbr=company.abbr
        payment_doc.posting_date=doc.posting_date
        payment_doc.paid_from = 'Cash - '+abbr
        payment_doc.save()
        payment_doc.submit()
=======
def create_payment_entry(doc,action):
        add_doc=frappe.new_doc('Payment Entry')
        add_doc.payment_type='Pay'
        add_doc.party_type = 'Employee'
        add_doc.party = doc.employee
        add_doc.posting_date = doc.posting_date
        add_doc.posting_date = doc.posting_date
        add_doc.paid_from_account_currency = doc.currency
        add_doc.mode_of_payment = doc.mode_of_payment
        add_doc.paid_amount=doc.advance_amount
        add_doc.received_amount=doc.advance_amount
        add_doc.source_exchange_rate=1.0
        add_doc.target_exchange_rate=1.0
        add_doc.paid_to=doc.advance_account
        add_doc.paid_from=doc.advance_account
        add_doc.append(
		"references",
		{
                        "reference_doctype": 'Employee Advance',
                        "reference_name": doc.name,
                        "total_amount": doc.advance_amount,
                        "outstanding_amount": doc.advance_amount,
                        "allocated_amount": doc.advance_amount,
                },
        )

        add_doc.insert()
        add_doc.submit()        
        frappe.db.commit()
>>>>>>> 62319c38eb8687c6054e0a77b0969d58f4224bbd

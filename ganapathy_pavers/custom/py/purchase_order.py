import frappe

def getdate(doc, event):
    doc.required_by_date = doc.schedule_date

def purchasenotification():
    notification = frappe.get_all(
			"Purchase Order",
			fields=["*"],
			filters={"per_received": 0, "required_by_date": frappe.utils.nowdate()},
            pluck="name"
		)
    for i in notification:
        doc=frappe.new_doc('Notification Log')
        doc.update({
        'subject': f'{ i } has no Purchase receipt',
        'type': 'Alert',
        'document_type': 'Purchase Order',
        'message': f'The Purchase Order { i } does not have a purchase receipt'
        })
        doc.flags.ignore_permissions=True
        doc.save()
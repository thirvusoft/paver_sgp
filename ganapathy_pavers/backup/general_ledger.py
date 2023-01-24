# General Entry Backup
# Line  160 to 180
def make_entry(args, adv_adj, update_outstanding, from_repost=False):
	gle = frappe.new_doc("GL Entry")
	gle.update(args)
	try:
		if gle.voucher_type in ['Payment Entry','Sales Invoice','Sales Order','Journal Entry'] and frappe.db.get_value(gle.voucher_type,gle.voucher_no,'type'):
			gle.update({'type':frappe.db.get_value(gle.voucher_type,gle.voucher_no,'type')})
		if gle.voucher_type == "Delivery Note":
			gle.update({
				'party': frappe.db.get_value(gle.voucher_type,gle.voucher_no,'customer'),
				'party_type': "Customer"		
				})
	except:
		pass
	gle.flags.ignore_permissions = 1
	gle.flags.from_repost = from_repost
	gle.flags.adv_adj = adv_adj
	gle.flags.update_outstanding = update_outstanding or 'Yes'
	gle.submit()

	if not from_repost:
		validate_expense_against_budget(args)
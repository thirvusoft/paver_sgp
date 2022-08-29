# General Entry Backup
# Line  229 to 230
def make_entry(args, adv_adj, update_outstanding, from_repost=False):
    # 229
    if gle.voucher_type in ['Payment Entry','Sales Invoice','Sales Order','Journal Entry'] and frappe.db.get_value(gle.voucher_type,gle.voucher_no,'type'):
			gle.update({'type':frappe.db.get_value(gle.voucher_type,gle.voucher_no,'type')})
    # 230
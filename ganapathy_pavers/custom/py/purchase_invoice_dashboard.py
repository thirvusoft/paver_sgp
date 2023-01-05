
from frappe import _
import frappe

def get_data(data=None):
	return {
		'fieldname': 'purchase_invoice',
		'non_standard_fieldnames': {
			'Journal Entry': 'reference_name',
			'Payment Entry': 'reference_name',
			'Payment Request': 'reference_name',
			'Landed Cost Voucher': 'receipt_document',
			'Purchase Invoice': 'return_against',
			'Auto Repeat': 'reference_document'
		},
		'internal_links': {
			'Purchase Order': ['items', 'purchase_order'],
			'Purchase Receipt': ['items', 'purchase_receipt'],
		},
		'transactions': [
			{
				'label': _('Payment'),
				'items': ['Payment Entry', 'Payment Request', 'Journal Entry']
			},
			{
				'label': _('Reference'),
				'items': ['Purchase Order', 'Purchase Receipt', 'Asset', 'Landed Cost Voucher']
			},
			{
				'label': _('Returns'),
				'items': ['Purchase Invoice']
			},
			{
				'label': _('Subscription'),
				'items': ['Auto Repeat']
			},
            {
				'label': _('Vehicle'),
				'items': ['Vehicle Log']
			},
		]
	}

def tags_msg(self,events):
	a=frappe.db.get_values("Purchase Invoice",{"name":self.name},"_user_tags",as_dict=True)
	if a[0]["_user_tags"]==None:
		frappe.msgprint("Select the tags")
from frappe import _

def get_data():
    return {
        'fieldname': 'cw_usb',
        'transactions': [
			{
				'label': _('Stock'),
				'items': ['Stock Entry',]
			},
        ]
    }
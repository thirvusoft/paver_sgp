from frappe import _

def get_data():
    return {
        'fieldname': 'usb',
        'transactions': [
			{
				'label': _('Stock'),
				'items': ['Stock Entry',]
			},
        ]
    }
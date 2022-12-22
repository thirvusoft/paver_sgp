
from frappe import _


def get_data(data=None):
	return {
		'fieldname': 'vehicle_log',
		'transactions': [
			{
				'label': _('Transactions'),
				'items': ['Journal Entry']
			}
		],
		'disable_create_buttons': ["Journal Entry"]
	}

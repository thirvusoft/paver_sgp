from frappe import _

def get_data():
    return {
        'fieldname': 'employee_advance_tool',
        'transactions': [
			{
				'label': _('Advances'),
				'items': ['Employee Advance',]
			},
        ]
    }
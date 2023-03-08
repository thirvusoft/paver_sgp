# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe 
from frappe import _


def execute(filters=None):
    columns, data = [], [{}]
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data
def get_columns(filters):
    columns = [
        {
            "label": _("Vehicle"),
            "fieldtype": "Link",
            "fieldname": "license_plate",
            "options":"Vehicle",
            "width": 150
        },
        {
            "label": _("Qty"),
            "fieldtype": "Float",
            "fieldname": "fuel_qty",
            "width": 100
        },
        {
            "label": _("Amount"),
            "fieldtype": "Float",
            "fieldname": "total_fuel",
            "width": 100
        },
        ]
    return columns

def get_data(filters):
    fuel=filters.get('fuel_type')
    filters_1={
        'select_purpose': 'Fuel',
        'date':['between',[filters.get('from_date'),filters.get('to_date')]],
        'docstatus':1, 
        'fuel_qty':['>',0],
        'from_barrel': filters.get("from_barrel", 0) or 0
        }
    if fuel:
        vehicle=frappe.get_all("Vehicle", filters={'fuel_type':fuel}, pluck='name')
        filters_1['license_plate']= ['in', vehicle]
    vehicle_log=frappe.db.get_all("Vehicle Log", filters=filters_1, fields=['license_plate','sum(fuel_qty) as fuel_qty','sum(total_fuel) as total_fuel'], group_by='license_plate')
    return vehicle_log

        
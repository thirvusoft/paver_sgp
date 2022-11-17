// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicle report"] = {
	"filters": [
		{
			'fieldname':'from_date',
			'label':'From Date',
			'fieldtype':'Date',
			// 'reqd':1,
		},
		{
			'fieldname':'to_date',
			'label':'To Date',
			'fieldtype':'Date',
			// 'reqd':1,
		},
		{
			'fieldname':'fuel_type',
			'label':'Fuel Type',
			'fieldtype':'Select',
			'options':'\nPetrol\nDiesel\nNatural Gas\nElectric',
			'default':'Diesel'
		},
	]
};

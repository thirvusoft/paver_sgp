// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily and Monthly Summary"] = {
	"filters": [
		{
			'fieldname':'from_date',
			'label':'From Date',
			'fieldtype':'Datetime',
		},
		{
			'fieldname':'to_date',
			'label':'To Date',
			'fieldtype':'Datetime',
		},
	]
};

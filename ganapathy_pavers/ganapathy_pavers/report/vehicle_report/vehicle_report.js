// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicle report"] = {
	"filters": [
		{
			'fieldname':'from_date',
			'label':'From Date',
			'fieldtype':'Date',
		},
		{
			'fieldname':'to_date',
			'label':'To Date',
			'fieldtype':'Date',
		},
		{
			'fieldname':'fuel_type',
			'label':'Fuel Type',
			'fieldtype':'Select',
			'options':"\n"+frappe.get_meta('Vehicle').fields.filter(df => df.fieldname==='fuel_type')[0].options ,
			'default':frappe.get_meta('Vehicle').fields.filter(df => df.fieldname==='fuel_type')[0].options.includes('Diesel')?'Diesel':''
		},
	]
};

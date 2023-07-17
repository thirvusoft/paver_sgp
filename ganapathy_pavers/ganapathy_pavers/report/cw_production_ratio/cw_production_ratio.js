// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CW Production Ratio"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
		},
		{
			fieldname: 'compound_wall_type',
			label: 'Compound Wall Type',
			fieldtype: 'MultiSelectList',
			get_data: async () => {
				await frappe.model.with_doctype('CW Manufacturing')
				let res = [{
					'value': 'Compound Wall',
					'description': ''
				}]
				frappe.get_meta("CW Manufacturing").fields.every(row => {
					if (row.fieldname == 'type') {
						(row.options || '').split('\n').forEach(opt => {
							if (!['Post', 'Slab'].includes(opt)) {
								res.push({
									'value': opt,
									'description': ''
								})
							}
						});
						return false
					}
					return true
				})
				return res
			}
		},
	]
};


// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicle Usage"] = {
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
			fieldname: "purpose",
			label: __("Purpose"),
			fieldtype: "MultiSelectList",
			get_data: async function () {
				let res = [], opts = "";
				frappe.model.with_doctype("Vehicle Log", () => {
					frappe.get_meta("Vehicle Log").fields.every(row => {
						if (row.fieldname == "select_purpose") {
							opts = row.options
							return false
						}
						return true
					})
				});

				opts.split('\n').forEach(opt => {
					if (opt) {
						res.push({
							value: opt,
							description: opt
						});
					}
				});

				return res
			}
		}
	]
};

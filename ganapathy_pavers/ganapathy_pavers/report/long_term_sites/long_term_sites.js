// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Long Term Sites"] = {
	filters: [
		{
			fieldname: "type",
			label: __("Type"),
			fieldtype: "Select",
			options: "\nPavers\nCompound Wall"
		},
		{
			fieldname: "from_date",
			label: __("From Date(Completion)"),
			fieldtype: "Date",
			depends_on: `eval: ((frappe?.query_report?.get_filter_value("status") || cur_dialog?.get_value('status'))?.length == 1 && (frappe?.query_report?.get_filter_value("status") || cur_dialog?.get_value('status'))[0] == "Completed")`
		},
		{
			fieldname: "to_date",
			label: __("To Date(Completion)"),
			fieldtype: "Date",
			depends_on: `eval: ((frappe?.query_report?.get_filter_value("status") || cur_dialog?.get_value('status'))?.length == 1 && (frappe?.query_report?.get_filter_value("status") || cur_dialog?.get_value('status'))[0] == "Completed")`
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "MultiSelectList",
			onchange: () => {
				cur_dialog?.refresh()
				frappe?.query_report?.refresh()
			},
			get_data: async function() {
				let res = [];
				await frappe.model.with_doctype('Project', () => {
					frappe.get_meta('Project').fields.every(row => {
						if (row.fieldname == 'status') {
							row.options.split('\n').forEach(opt => {
								if (opt) {
									res.push({
										value: opt,
										description: opt
									});
								}
							});
							return false
						}
						return true
					});
				});

				return res
			}
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer"
		},
		{
			fieldname: "limit",
			label: __("Limit"),
			fieldtype: "Int",
			default: 10
		},
	]
};

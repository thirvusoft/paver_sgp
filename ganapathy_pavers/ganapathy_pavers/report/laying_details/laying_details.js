// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Laying Details"] = {
	filters: [
		{
			fieldname: "type",
			label: __("Type"),
			fieldtype: "Select",
			options: "\nPavers\nCompound Wall"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "MultiSelectList",
			get_data: async function () {
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
		frappe.get_route()[0]=="dashboard-view"?{
			fieldtype: 'Column Break',
			fieldname: 'column_break_233'
		}:{fieldtype: 'Data', hidden: 1, fieldname: '----'},
		{
			fieldname: "job_worker",
			label: __("Job Worker"),
			fieldtype: "Link",
			options: "Employee",
			get_query: function () {
				return {
					filters: {
						designation: "Job Worker"
					}
				}
			}
		},
		{
			fieldname: "site",
			label: __("Site"),
			fieldtype: "Link",
			options: "Project"
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item"
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: "Job Worker\nItem\nSite",
			default: "Job Worker"
		},
		{
			"fieldname": "show_only_other_work",
			"label": __("Show Only Other Work"),
			"fieldtype": "Check",
			on_change: function () {
				if (frappe?.query_report?.get_filter('show_only_other_work')?.get_value() || cur_dialog?.get_value('show_only_other_work')) {
					frappe?.query_report?.get_filter('hide_other_work')?.set_value(!frappe?.query_report?.get_filter('show_only_other_work')?.get_value())
					cur_dialog?.set_value('hide_other_work', !cur_dialog?.get_value('show_only_other_work'))
				}
				frappe.query_report.refresh();
			},
			onchange: function () {
				if (frappe?.query_report?.get_filter('show_only_other_work')?.get_value() || cur_dialog?.get_value('show_only_other_work')) {
					frappe?.query_report?.get_filter('hide_other_work')?.set_value(!frappe?.query_report?.get_filter('show_only_other_work')?.get_value())
					cur_dialog?.set_value('hide_other_work', !cur_dialog?.get_value('show_only_other_work'))
				}
			}
		},
		{
			"fieldname": "hide_other_work",
			"label": __("Don't Show Other Work"),
			"fieldtype": "Check",
			on_change: function () {
				if (frappe?.query_report?.get_filter('hide_other_work')?.get_value() || cur_dialog?.get_value('hide_other_work')) {
					frappe.query_report.get_filter('show_only_other_work').set_value(!frappe.query_report.get_filter('hide_other_work').get_value())
					cur_dialog?.set_value('show_only_other_work', !cur_dialog?.get_value('hide_other_work'))
				}
				frappe.query_report.refresh();
			},
			onchange: function () {
				if (frappe?.query_report?.get_filter('hide_other_work')?.get_value() || cur_dialog?.get_value('hide_other_work')) {
					frappe.query_report.get_filter('show_only_other_work').set_value(!frappe.query_report.get_filter('hide_other_work').get_value())
					cur_dialog?.set_value('show_only_other_work', !cur_dialog?.get_value('hide_other_work'))
				}
			},
		},
	]
};

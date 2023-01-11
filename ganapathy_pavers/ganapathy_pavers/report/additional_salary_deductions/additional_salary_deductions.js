// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Additional Salary Deductions"] = {
	filters: [
		{
			fieldname: "employee",
			fieldtype: "Link",
			options: "Employee",
			label: "Employee"
		},
		{
			fieldname: "show_salary_slips",
			fieldtype: "Check",
			label: "Show Deducted Salary Slips"
		}
	]
};

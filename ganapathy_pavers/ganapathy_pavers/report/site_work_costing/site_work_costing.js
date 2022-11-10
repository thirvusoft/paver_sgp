// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Site Work Costing"] = {
	"filters": [
		{
			fieldname: "customer",
			label: "Customer",
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "name",
			label: "Site Work",
			fieldtype: "Link",
			options: "Project",
		},
	]
};

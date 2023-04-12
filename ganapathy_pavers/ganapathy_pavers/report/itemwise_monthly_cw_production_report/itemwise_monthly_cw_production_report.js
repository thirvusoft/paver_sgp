// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Itemwise Monthly CW Production Report"] = {
	"filters": [
	  {
		fieldname: "from_date",
		label: __("From Date"),
		fieldtype: "Date",
		width: "80",
		default: frappe.datetime.month_start(),
		reqd: 1,
	  },
	  {
		fieldname: "to_date",
		label: __("To Date"),
		fieldtype: "Date",
		default: frappe.datetime.month_end(),
		width: "80",
		reqd: 1,
	  },
	  {
		  fieldname: "report_type",
		  label: __("Report Type"),
		  fieldtype: "Select",
		  options: "Summary\nReport",
		  default: "Summary"
	  }
	],
  };
  
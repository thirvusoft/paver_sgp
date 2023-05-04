// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

var currentDate = moment();
var prevMonthEnd = moment(currentDate).subtract(1, 'month').startOf('month').format();

frappe.query_reports["Vehicle Alerts"] = {
	filters: [
		{
			label: "Date",
			fieldname: "date",
			fieldtype: "Date",
			reqd: 1,
			default: prevMonthEnd
		}
	],
};

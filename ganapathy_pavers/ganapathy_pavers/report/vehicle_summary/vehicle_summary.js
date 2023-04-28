// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

var currentDate = moment();
var prevMonthStart = moment(currentDate).subtract(1, 'month').startOf('month').format();
var prevMonthEnd = moment(currentDate).subtract(1, 'month').endOf('month').format();

frappe.query_reports["Vehicle Summary"] = {
	filters: [
		{
			label: "From Date",
			fieldname: "from_date",
			fieldtype: "Date",
			reqd: 1,
			default: prevMonthStart
		},
		{
			label: "To Date",
			fieldname: "to_date",
			fieldtype: "Date",
			reqd: 1,
			default: prevMonthEnd
		}
	],
	formatter: function(value, row, column, data, default_formatter) {
		value = __(default_formatter(value, row, column, data));
		if (data.bold) {
			value = $(`<div style="font-weight: bold; background: ${["TOTAL", "AVERAGE"].includes(data.vehicle)?"rgb(127 221 253 / 85%)":"rgb(242 140 140 / 81%)"}">${value}</div>`);
			let $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		}
		return value
	}
};

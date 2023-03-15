// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */
let show = true
frappe.query_reports["Item Price Difference"] = {
	filters: [
		{
			reqd: 1,
			default: "",
			options: "Item",
			label: __("Item"),
			fieldname: "item",
			fieldtype: "Link",
			get_query: () => {
				return {
					filters: { "has_variants": 1 }
				}
			},
		}
	]
};

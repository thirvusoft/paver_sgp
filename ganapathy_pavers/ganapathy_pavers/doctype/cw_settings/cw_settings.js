// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('CW Settings', {
	refresh: function (frm) {
		frm.set_query("item_code", "bin_items", function () {
			return {
				"filters": {
					item_group: "Raw Material"
				}
			}
		})
	}
});

// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
var acc_filters = []
frappe.ui.form.on('Service Item', {
	refresh: async function (frm) {
		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_child_under_vehicle_expense_service",
			callback(r) {
				acc_filters = r.message;
			}
		});
		frm.set_query("expense_account", function () {
			return {
				filters: {
					name: ['in', acc_filters],
					is_group: 0
				}
			}
		});
	}
});

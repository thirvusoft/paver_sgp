// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

var acc_filters = [], vehicle_expense_filters = [], vehicle_filters = [];
frappe.ui.form.on('Expense Accounts', {
	refresh: async function (frm) {
		["paver_group", "cw_group", "lg_group", "fp_group"].forEach(field => frm.set_query(field, function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 1,
					root_type: "Expense"
				}
			}
		}));
		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_filter",
			args: {
				company: cur_frm.doc.company || "",
			},
			callback(r) {
				acc_filters = r.message["exp_accounts"];
				vehicle_expense_filters = r.message["exp_groups"];
			}
		})
		frm.set_query("vehicle_expense", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 1,
					root_type: "Expense",
					name: ["not in", vehicle_expense_filters]
				}
			}
		});
		frm.set_query("paver_account", "expense_account_common_groups", function () {
			return {
				filters: {
					company: frm.doc.company,
					name: ['in', acc_filters['paver']],
					is_group: 0
				}
			}
		});
		frm.set_query("cw_account", "expense_account_common_groups", function () {
			return {
				filters: {
					company: frm.doc.company,
					name: ['in', acc_filters['cw']],
					is_group: 0
				}
			}
		});
		frm.set_query("lg_account", "expense_account_common_groups", function () {
			return {
				filters: {
					company: frm.doc.company,
					name: ['in', acc_filters['lg']],
					is_group: 0
				}
			}
		});
		frm.set_query("fp_account", "expense_account_common_groups", function () {
			return {
				filters: {
					company: frm.doc.company,
					name: ['in', acc_filters['fp']],
					is_group: 0
				}
			}
		});

		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_child_under_vehicle_expense",
			callback(r) {
				vehicle_filters = r.message;
			}
		});
		["default_fuel_account", "default_tyre_account"].forEach(field => frm.set_query(field, function () {
			return {
				filters: {
					name: ['in', vehicle_filters],
					is_group: 0
				}
			}
		}));
	},
	paver_group: function (frm) {
		frm.trigger("refresh");
	},
	cw_group: function (frm) {
		frm.trigger("refresh");
	},
	lg_group: function (frm) {
		frm.trigger("refresh");
	},
	fp_group: function (frm) {
		frm.trigger("refresh");
	},
});

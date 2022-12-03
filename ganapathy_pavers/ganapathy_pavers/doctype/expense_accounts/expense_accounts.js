// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Accounts', {
	refresh: async function (frm) {
		["paver_group", "cw_group", "lg_group", "fp_group"].forEach(field => frm.set_query(field, function () {
			return {
				filters: {
					is_group: 1,
					root_type: "Expense"
				}
			}
		}));
		var acc_filters;
		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_filter",
			args: {
				company: cur_frm.doc.company || "",
			},
			callback(r) {
				acc_filters = r.message;
			}
		})
		frm.set_query("paver_account", "expense_account_common_groups", function () {
			return {
				filters: {
					name: ['in', acc_filters['paver']],
					is_group: 0
				}
			}
		});
		frm.set_query("cw_account", "expense_account_common_groups", function () {
			return {
				filters: {
					name: ['in', acc_filters['cw']],
					is_group: 0
				}
			}
		});
		frm.set_query("lg_account", "expense_account_common_groups", function () {
			return {
				filters: {
					name: ['in', acc_filters['lg']],
					is_group: 0
				}
			}
		});
		frm.set_query("fp_account", "expense_account_common_groups", function () {
			return {
				filters: {
					name: ['in', acc_filters['fp']],
					is_group: 0
				}
			}
		});
	}
});

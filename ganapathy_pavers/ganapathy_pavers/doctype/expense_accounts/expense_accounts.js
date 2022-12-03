// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Accounts', {
	refresh: function (frm) {
		["paver_group", "cw_group", "lg_group", "fp_group"].forEach(field => frm.set_query(field, function () {
			return {
				filters: {
					is_group: 1,
					root_type: "Expense"
				}
			}
		}));

		// frm.set_query("paver_account", "expense_account_common_groups", function() {
		// 	return {
		// 		filters: {
		// 			parent_account: cur_frm.doc.paver_group,
		// 			is_group: 0
		// 		}
		// 	}
		// });
		// frm.set_query("cw_account", "expense_account_common_groups", function() {
		// 	return {
		// 		filters: {
		// 			parent_account: cur_frm.doc.cw_group,
		// 			is_group: 0
		// 		}
		// 	}
		// });
		// frm.set_query("lg_account", "expense_account_common_groups", function() {
		// 	return {
		// 		filters: {
		// 			parent_account: cur_frm.doc.lg_group,
		// 			is_group: 0
		// 		}
		// 	}
		// });
		// frm.set_query("fp_account", "expense_account_common_groups", function() {
		// 	return {
		// 		filters: {
		// 			parent_account: cur_frm.doc.fp_group,
		// 			is_group: 0
		// 		}
		// 	}
		// });
	}
});

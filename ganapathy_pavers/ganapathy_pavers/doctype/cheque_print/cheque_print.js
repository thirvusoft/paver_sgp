// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cheque Print', {
	get_amount_in_text: async function(frm) {
		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.cheque_print.cheque_print.aount_in_words",
			freeze: true,
			args: {
				amount: frm.doc.rupees || 0
			},
			callback: function(r) {
				frm.set_value('rupees_in_text', r.message || '');
			}
		});
	}
});

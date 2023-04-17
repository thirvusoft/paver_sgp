frappe.provide("ganapathy_pavers")

ganapathy_pavers.show_reference = function (title, reference, total_amount) {
	reference = JSON.parse(reference)
	if (cur_dialog) {
		cur_dialog.hide()
	}
	let opt = '<ul class="expense-account-details">'

	let previous_acc = "", current_acc = "", current_amount = 0, amount_disp_count = 0;
	let idx = 0;
	reference.forEach(e => {
		idx++;
		current_acc = e.account || "";
		if (current_acc != previous_acc && idx != 1) {
			amount_disp_count++;
			opt += `</ul>
			<div class="expense-reference-dialog-total-row">
				<b>AMOUNT</b><b> ${format_currency(current_amount)}</b>
			</div><ul class="expense-account-details">`;
			current_amount = 0;
		}
		if ((idx == 1 || current_acc != previous_acc) && e.account) {
			opt += `
			<div class="expense-details-title">${e.account}</div>
			`
		}
		opt += `
			<li>
				<div class="expense-reference-dialog-row">
					<div>
						${frappe.utils.get_form_link(e.doctype, e.docname, true, e.doctype + " " + e.docname)}
					</div>
					<div>
						${e.account || ""}
					</div>
					<div>
						<b>${format_currency(e.amount)}</b>
					</div>
				</div>
			</li>
		`
		current_amount += (parseFloat(e.amount) || 0)
		previous_acc = current_acc || "";
	});

	if (reference.length > 1) {
		amount_disp_count++;
		opt += `</ul>
			<div class="expense-reference-dialog-total-row">
				<b>AMOUNT</b><b> ${format_currency(current_amount)}</b>
			</div><ul class="expense-account-details">`;
	}
	if (amount_disp_count > 1) {
		opt += `</ul>
		<div class="expense-reference-dialog-total-row expense-final-total-row">
			<b>TOTAL AMOUNT</b><b> ${format_currency(total_amount)}</b>
		</div>`
	}

	let d = new frappe.ui.Dialog({
		title: title || "Expense Reference",
		fields: [
			{
				fieldname: 'ref',
				fieldtype: 'HTML',
				options: opt,
			}
		],
		size: "large"
	})
	d.show()
}
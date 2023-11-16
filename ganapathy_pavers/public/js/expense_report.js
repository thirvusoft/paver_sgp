frappe.provide("ganapathy_pavers")

ganapathy_pavers.show_reference = function (title, reference, total_amount) {
	let calculate_total_amount = total_amount ? false : true;
	if (calculate_total_amount) {
		total_amount = 0
	}
	reference = JSON.parse(reference)
	if (cur_dialog) {
		cur_dialog.hide()
	}
	let opt = '<ul class="expense-account-details">'
	let current_amount = 0, amount_disp_count = 0;

	const groupedData = reference.reduce((acc, obj) => {
		const key = obj.title || "";
		if (!acc[key]) {
			acc[key] = [];
		}
		acc[key].push(obj);
		return acc;
	}, {});

	for (const ref in groupedData) {
		let reference = groupedData[ref];
		let previous_acc = "", current_acc = "";
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
				<div class="expense-details-title">${ref} ${e.account}</div>
				`
			}
			opt += `
				<li>
					<div class="expense-reference-dialog-row">
						<div>
							${(e.doctype && e.docname) ? frappe.utils.get_form_link(e.doctype, e.docname, true, e.doctype + " " + e.docname) : ''}
						</div>
						<div>
							${e.other_info || e.account || ''}
						</div>
						<div>
							<b>${format_currency(e.amount|| 0)}</b>
						</div>
					</div>
				</li>
			`
			if (calculate_total_amount) {
				total_amount += (parseFloat(e.amount) || 0)
			}
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
	}

	if (amount_disp_count > 1 || Object.keys(groupedData).length > 1) {
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
frappe.provide("ganapathy_pavers")

ganapathy_pavers.show_reference = function (title, reference, total_amount) {
	reference = JSON.parse(reference)
    if (cur_dialog) {
        cur_dialog.hide()
    }
	let opt='<ul>'

	reference.forEach(e => {
		opt += `
			<li>
				<div class="expense-reference-dialog-row">
					<div>
						${frappe.utils.get_form_link(e.doctype, e.docname, true, e.doctype + '-' +e.docname)}
					</div>
					<div>
						<b>${format_currency(e.amount)}</b>
					</div>
				</div>
			</li>
		`
	});

	opt += `</ul>
	<div class="expense-reference-dialog-total-row">
		<b>Total Amount:</b><b> ${format_currency(total_amount)}</b>
	</div>`

	let d = new frappe.ui.Dialog({
        title: title || "Reference",
        fields: [
            {
                fieldname: 'ref',
                fieldtype: 'HTML',
                options: opt,
            }
        ],
    })
    d.show()
}
frappe.provide("ganapathy_pavers")

ganapathy_pavers.show_reference = function (title, reference) {
    if (cur_dialog) {
        cur_dialog.hide()
    }
    let d = new frappe.ui.Dialog({
        title: title || "Reference",
        fields: [
            {
                fieldname: 'ref',
                fieldtype: 'HTML',
                options: `
                    ${reference}
                `
            }
        ]
    })
    d.show()
}
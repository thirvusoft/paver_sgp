frappe.ui.form.on("Delivery Note" ,{
    validate:function(frm){
        frappe.call({
            method: "ganapathy_pavers.custom.py.attach_pdf.attach_pdf",
            args: {
                'doctype': cur_frm.doc.doctype,
                'doc': cur_frm.doc.name
            },
            callback: function () {
                frappe.call({
                    method: "ganapathy_pavers.custom.py.api.send_invoice",
                    args: {
                        'cus': frm.doc.customer,
                        'name': frm.doc.name,
                        'doctype': frm.doc.doctype
                    },
                    callback: function (r) {
                    console.log(r.message)
                    }
                })
            }
        })
}
})
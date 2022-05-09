frappe.ui.form.on("Work Order",{
    on_submit: function(frm,cdt,cdn){
        frappe.call({
            method: "ganapathy_pavers.custom.py.work_order.get_link",
            args:{doc:frm.doc.name},
            callback(r){
                window.location.assign(r.message)
            }
        })
    }
})
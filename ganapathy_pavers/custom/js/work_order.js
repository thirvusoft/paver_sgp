frappe.ui.form.on("Work Order",{
    on_submit: function(frm){
        frappe.call({
            method: "ganapathy_pavers.custom.py.work_order.get_link",
            args:{doc:frm.doc.name},
            callback(r){
                window.location.assign(r.message)
            }
        })
    },
    onload: function(frm){
        if(frm.doc.__unsaved || frm.doc.parent_work_order){
            frm.set_df_property("linked_work_order",'hidden',1)
        }
        else{
            frappe.call({
                method: "ganapathy_pavers.custom.py.work_order.get_child_work_order_status",
                args: {parent: frm.doc.name},
                callback(r){
                    var docstatus= cur_frm.doc.docstatus
                    cur_frm.set_value("linked_work_order", r.message)
                    cur_frm.refresh()
                    if(docstatus == 1){
                    cur_frm.save('Update')
                    }
                    else{
                        cur_frm.save()
                    }
                }
            })

        }
    }
})
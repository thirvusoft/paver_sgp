frappe.ui.form.on("BOM",{
    onload: function(frm){
        if(cur_frm.doc.doctype == "BOM"){
        if(frm.doc.__unsaved){
            frm.set_df_property("linked_work_orders",'hidden',1)
        }
        else{
            frappe.call({
                method: "ganapathy_pavers.custom.py.bom.get_parent_work_order_status",
                args:{bom:frm.doc.name},
                callback(r){
                    
                    if(r.message){
                    cur_frm.set_value("linked_work_orders", r.message)
                    cur_frm.refresh()
                    cur_frm.save('Update')
                    }
                    
                }
            }) 
        }
    }
    }
})

frappe.ui.form.on('BOM',{
    setup: function(frm){
        frm.set_query('source_warehouse','operations', function(){
            return {
                filters:{"is_group":0}
            }
        })

        frm.set_query('target_warehouse','operations', function(){
            return {
                filters:{"is_group":0}
            }
        })
    }
})
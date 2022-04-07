frappe.ui.form.on('Sales Order',{
    onload: function(frm){
        //cur_frm.set_df_property('items','hidden',1)
        cur_frm.set_df_property('items','mandatory',0)
    }
})


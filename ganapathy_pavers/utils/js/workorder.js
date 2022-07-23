frappe.ui.form.on('Work Order', {
    refresh: function(frm){
        frm.set_query('mould_name', function(frm){
            return {
                filters:{
                    'paver_name': 'production_item'
                }
            }
        })
    }
})


frappe.ui.form.on('Asset', {
    refresh: function(frm){
        frm.set_query('paver_name', function(frm){
            return {
                filters:{
                    'item_group': 'Pavers'
                }
            }
        })
    }
})
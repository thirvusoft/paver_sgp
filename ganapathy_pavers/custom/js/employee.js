frappe.ui.form.on('Employee', {
    onload: function(frm){
        frm.set_query('machine', function(frm){
            return {
                filters: {
                    'location': frm.doc.location
                }
            }
        })
    }
})
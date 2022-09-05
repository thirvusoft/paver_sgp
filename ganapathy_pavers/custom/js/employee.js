frappe.ui.form.on('Employee', {
    onload: function(frm){
        frm.set_query('machine', function(frm){
            return {
                filters: {
                    'location': cur_frm.doc.location
                }
            }
        })
        frm.set_query('reports_to', function(frm){
            return {
                filters:{
                    'designation': 'Operator'
                }
            }
        });   
    }
})
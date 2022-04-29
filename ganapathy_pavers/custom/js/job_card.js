frappe.ui.form.on("Job Card",{
    onload: function(frm){
        if(frm.doc.doc_onload == 0){
        frm.set_value('time_logs',[])
        frm.set_value('doc_onload',1)
        }
    }
})
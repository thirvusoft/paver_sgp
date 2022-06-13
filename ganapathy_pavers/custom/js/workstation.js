frappe.ui.form.on("Workstation",{
    get_employees: function(frm){
        if(frm.doc.designation){
            frappe.db.get_list("Employee",{fields:['name'],filters:{'designation':frm.doc.designation}}).then((data)=>{
                console.log(data)
                data.forEach(function(i){
                    let child = cur_frm.add_child('ts_labor')
                    child.ts_labour = i['name']
                })
                cur_frm.refresh();
            })
        }
    }
})
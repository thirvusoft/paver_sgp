frappe.ui.form.on("Vehicle Log" ,{
    onload:function(frm){
            frm.set_query('employee', function(frm){
                        return {
                            filters:{
                                'designation': 'Driver'
                            }
                        }
                    });
                    
    },
    odometer:function(frm){
        frm.set_value("today_odometer_value",cur_frm.doc.odometer-cur_frm.doc.last_odometer )
        frm.refresh()
    } 
});
          

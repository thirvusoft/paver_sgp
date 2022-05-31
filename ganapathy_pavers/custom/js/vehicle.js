frappe.ui.form.on("Vehicle" ,{
    onload:function(frm){
         
                    frm.set_query('operator', function(frm){
                              return {
                                  filters:{
                                      'employee_categories': 'Operator'
                                  }
                              }
                          }),
                    frm.set_query('employee', function(frm){
                              return {
                                  filters:{
                                      'employee_categories':'Driver'
                                  }
                              }
                    });
        
                    let Maintenance=["Insurance","FC Details","Road Tax","Permit","Pollution Certificate","Green Tax"]
                    for(let row=0;row<Maintenance.length;row++){
                       
                        var new_row = frm.add_child("maintanence_details_");
                        new_row.maintenance=Maintenance[row]
                         }
                                  refresh_field("maintanence_details_");

                              
                                
                    
    }

})

function vehicle(frm,cdt,cdn){
	let row=locals[cdt][cdn];
	if( row.frequency !=""){
            if(!row.from_date){}
            else
                    frappe.call({
                        method:"ganapathy_pavers.custom.py.vehicle.todate",
                        args:{
                            'diff':row.frequency, 
                            'fdate':row.from_date,
                        },
                        callback: function(r){
                            frappe.model.set_value(cdt,cdn,'to_date',r.message);
                        }
                    })
    }
    else
       {}

}

function notification(frm,cdt,cdn){
	let row=locals[cdt][cdn]; 
               frappe.call({
                        method:"ganapathy_pavers.custom.py.vehicle.notify",
                        args:{
                            'day':row.day_before ? row.day_before:'', 
                            'month':row.month_before ? row.month_before:'',
                            'week':row.week_before ? row.week_before:'',
                            'todate':to_date ? row.to_date:'',
                        },
                        callback: function(r){
                           console.log("hhhh")
                        }
                    })
    
}





frappe.ui.form.on('Maintenance Details', {
    frequency:function(frm,cdt,cdn){
        vehicle(frm,cdt,cdn);
 
},
   from_date:function(frm,cdt,cdn){
        vehicle(frm,cdt,cdn);
 
},
   month_before:function(frm,cdt,cdn){
      notification(frm,cdt,cdn);

},
   week_before:function(frm,cdt,cdn){
    notification(frm,cdt,cdn);
},
   day_before:function(frm,cdt,cdn){
    notification(frm,cdt,cdn);
},
   to_date:function(frm,cdt,cdn){
     notification(frm,cdt,cdn);
}

})


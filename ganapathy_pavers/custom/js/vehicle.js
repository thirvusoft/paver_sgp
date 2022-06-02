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
    let license=cur_frm.doc.license_plate
	let row=locals[cdt][cdn];
	if( row.frequency !=""){
            if(!row.from_date){}
            if(row.day_before==1){
                  let day=1
                    frappe.call({
                        method:"ganapathy_pavers.custom.py.vehicle.todate",
                        args:{
                            'diff':row.frequency, 
                            'fdate':row.from_date,
                            'duaration':day ? day:'', 
                            'lic':license,
                            'main':row.maintenance,
                        },
                        callback: function(r){
                            frappe.model.set_value(cdt,cdn,'to_date',r.message);
                        }
                    })
                }
            if(row.week_before===1){
                    console.log('test');
                    let day=7
                      frappe.call({
                          method:"ganapathy_pavers.custom.py.vehicle.todate",
                          args:{
                              'diff':row.frequency, 
                              'fdate':row.from_date,
                              'duaration':day ? day:'',
                              'lic':license,
                              'main':row.maintenance,
                          },
                          callback: function(r){
                              frappe.model.set_value(cdt,cdn,'to_date',r.message);
                          }
                      })
                  }
                  if(row.month_before===1){
                    console.log('test1');
                    let day=30
                      frappe.call({
                          method:"ganapathy_pavers.custom.py.vehicle.todate",
                          args:{
                              'diff':row.frequency, 
                              'fdate':row.from_date,
                              'duaration':day ? day:'', 
                              'lic':license,
                              'main':row.maintenance,
                          },
                          callback: function(r){
                              frappe.model.set_value(cdt,cdn,'to_date',r.message);
                          }
                      })
                  }
    }
    else
       {}

}


frappe.ui.form.on('Maintenance Details', {
    frequency:function(frm,cdt,cdn){
        vehicle(frm,cdt,cdn);
 
},
   from_date:function(frm,cdt,cdn){
        vehicle(frm,cdt,cdn);
 
},
   month_before:function(frm,cdt,cdn){
     vehicle(frm,cdt,cdn);
},
   week_before:function(frm,cdt,cdn){
     vehicle(frm,cdt,cdn);
}, 
   day_before:function(frm,cdt,cdn){
     vehicle(frm,cdt,cdn);
},
  maintenance:function(frm,cdt,cdn){
     vehicle(frm,cdt,cdn);

   },
})


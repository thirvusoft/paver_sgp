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
	if(row.from_date != ""){
        console.log(today().toLocaleDateString("en-US", options));}
       // console.log(toLocaleDateString(row.from_date));}
    else
       console.log("&&&&&&&&&&&&&&")
	  //frappe.model.set_value(cdt,cdn,'no_of_sheets',Math.round(row.qty/row.label_count_per_paper));

}
frappe.ui.form.on('Maintenance Details', {
 from_date:function(frm,cdt,cdn){
   vehicle(frm,cdt,cdn);
},

})


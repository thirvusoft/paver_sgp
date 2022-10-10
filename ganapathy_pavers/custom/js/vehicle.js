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
                    }),
                    frm.set_query("add_on", function(frm) {
                        return {
                            filters: {
                                'is_add_on' : ['!=', 1]
                            }
                        };
                    });
                // if (cur_frm.is_new()){
                //     let Maintenance=["Insurance","FC Details","Road Tax","Permit","Pollution Certificate","Green Tax"]
                //     for(let row=0;row<Maintenance.length;row++){
                       
                //         var new_row = frm.add_child("maintanence_details_");
                //         new_row.maintenance=Maintenance[row]
                //          }
                //                   refresh_field("maintanence_details_");
                //          }

    }

})
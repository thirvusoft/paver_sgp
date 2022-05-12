frappe.ui.form.on("Vehicle Log" ,{
          onload:function(frm){
                    frm.set_query('employee', function(frm){
                              return {
                                  filters:{
                                      'designation': 'Driver'
                                  }
                              }
                          });
                         let Maintenance=["Insurance","FC Details","Road Tax","Permit","Pollution Certificate","Green Tax"]
                          for(let row=0;row<Maintenance.length;row++){
                             
                              var new_row = frm.add_child("maintanence_details");
                              new_row.maintenance=Maintenance[row]
                               }
                                        refresh_field("maintanence_details");
          }
});
          

frappe.ui.form.on("Vehicle Log" ,{
          onload:function(frm){
                    frm.set_query('employee', function(frm){
                              return {
                                  filters:{
                                      'designation': 'Driver'
                                  }
                              }
                          });
                         
          }
});
          

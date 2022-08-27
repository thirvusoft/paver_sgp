frappe.ui.form.on("Purchase Receipt" ,{
          onload:function(frm){
                    frm.set_query('transporter', function(frm){
                              return {
                                  filters:{
                                      'supplier_name': 'Own Transporter'
                                  }
                              }
                          });
          }
})
frappe.ui.form.on('BOM', {

item:function(frm){
    frm.set_query('asset_name', function(frm){
                return {
                    filters:{
                        'paver_name': cur_frm.doc.item,
                        'status' : 'Submitted'
                    }
                }
            })
        },

onload:function(frm){
    frm.set_query('asset_name', function(frm){
              return {
                  filters:{
                      'paver_name': cur_frm.doc.item,
                      'status' : 'Submitted'
                  }
              }
          })
        }
    })

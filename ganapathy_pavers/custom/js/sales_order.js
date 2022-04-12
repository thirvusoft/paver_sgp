function setquery(frm){
    frm.set_query('item','pavers',function(frm){
        return {
            filters:{
                'is_sales_item':1,
                'item_group':'Pavers',
                'has_variants':0
            }
        }
    })
}


frappe.ui.form.on('Sales Order',{
    
    onload:function(frm){
        setquery(frm)
        if(cur_frm.is_new()==1){
            frm.clear_table('items')
        }
        cur_frm.set_df_property('items','reqd',0);
        cur_frm.set_df_property('items','hidden',1)
    },
    type:function(frm){
        setquery(frm)
    },
    before_save:async function(frm){
        frm.clear_table("items");
        if(cur_frm.doc.type=='Pavers'){
            for(let row=0;row<cur_frm.doc.pavers.length;row++){
                var message;
                var new_row = frm.add_child("items");
                new_row.item_code=cur_frm.doc.pavers[row].item
                new_row.qty=cur_frm.doc.pavers[row].allocated_paver_area
                new_row.rate=cur_frm.doc.pavers[row].rate
                new_row.amount=cur_frm.doc.pavers[row].amount
                await frappe.call({
                    method:'ganapathy_pavers.custom.py.sales_order.get_item_value',
                    args:{
                        'doctype':cur_frm.doc.pavers[row].item,
                    },
                    callback: function(r){
                        message=r.message;
                        new_row.item_name=message['item_name']
                        new_row.uom=message['uom']
                        new_row.description=message['description']
                    }
                })
                new_row.conversion_factor=1
                new_row.warehouse=cur_frm.doc.set_warehouse
                new_row.delivery_date=cur_frm.doc.delivery_date
            }
        }   
        refresh_field("items");
    },
    
    on_submit:function(frm){
        frappe.call({
            method:"ganapathy_pavers.custom.py.sales_order.create_site",
            args:{
                self: cur_frm.doc
            },
            callback: function(r){
                //frappe.set_route('project', 'new-project-1',r.message['doc'])
            }
        })
    }
})


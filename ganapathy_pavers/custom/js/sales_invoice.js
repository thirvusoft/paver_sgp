frappe.ui.form.on('Sales Invoice Item', {
    ts_qty: function(frm,cdt,cdn){
        bundle_calc(frm, cdt, cdn)
    },
    conversion_factor: function(frm,cdt,cdn){
        bundle_calc(frm, cdt, cdn)
    }
})


async function bundle_calc(frm, cdt, cdn){
    let row = locals[cdt][cdn]
    let uom=row.uom
    let conv
    await frappe.db.get_doc('Item', row.item_code).then((doc) => {
        let bundle_conv=1;
        let other_conv=1;
        for(let doc_row=0; doc_row<doc.uoms.length; doc_row++){
            if(doc.uoms[doc_row].uom==uom){
                other_conv=doc.uoms[doc_row].conversion_factor
            }
            if(doc.uoms[doc_row].uom=='bundle'){
                bundle_conv=doc.uoms[doc_row].conversion_factor
            }
        }
        conv=bundle_conv/other_conv
    })
    frappe.db.get_doc('Item',row.item_code).then((doc)=>{
        if(doc.item_group=='Pavers'){
            frappe.model.set_value(cdt, cdn, 'qty', row.ts_qty*conv)
            let rate=row.rate
            frappe.model.set_value(cdt, cdn, 'rate', 0)
            frappe.model.set_value(cdt, cdn, 'rate', rate)
       }
    })
}



frappe.ui.form.on('Sales Invoice', {
    onload:async function(frm){
        console.clear()
        if(cur_frm.is_new()){
            for(let ind=0;cur_frm.doc.items.length;ind++){
                let cdt=cur_frm.doc.items[ind].doctype
                let cdn=cur_frm.doc.items[ind].name
                let row=locals[cdt][cdn]
                let uom=row.uom
                let conv
                if(row.item_code)
                {
                await frappe.db.get_doc('Item', row.item_code).then((doc) => {
                    let bundle_conv=1;
                    let other_conv=1;
                    for(let doc_row=0; doc_row<doc.uoms.length; doc_row++){
                        if(doc.uoms[doc_row].uom==uom){
                            other_conv=doc.uoms[doc_row].conversion_factor
                        }
                        if(doc.uoms[doc_row].uom=='bundle'){
                            bundle_conv=doc.uoms[doc_row].conversion_factor
                        }
                    }
                    conv=bundle_conv/other_conv
                })
            
            
            frappe.db.get_doc('Item',row.item_code).then((doc)=>{
                if(doc.item_group=='Pavers'){
                    frappe.model.set_value(cdt, cdn, 'ts_qty', row.qty/conv)
                    let rate=row.rate
                    frappe.model.set_value(cdt, cdn, 'rate', 0)
                    frappe.model.set_value(cdt, cdn, 'rate', rate)
                }    
                })
            }
        }
            }
        }
})
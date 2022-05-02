frappe.ui.form.on('Delivery Note Item', {
    qty: function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        stock_uom(frm,cdt,cdn)
        frappe.model.set_value(cdt,cdn,'stock_qty',row.ts_qty?row.ts_qty:0)
        
    },
    conversion_factor: function(frm,cdt,cdn){
        stock_uom(frm,cdt,cdn)
    },
    ts_qty: async function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        await frappe.model.set_value(cdt, cdn, 'qty', (row.ts_qty?row.ts_qty:0)*(row.conversion_factor?row.conversion_factor:0))
        frappe.model.set_value(cdt,cdn,'stock_qty',row.ts_qty?row.ts_qty:0)
    }
})

function stock_uom(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    frappe.model.set_value(cdt, cdn, 'ts_qty', (row.qty?row.qty:0)/(row.conversion_factor?row.conversion_factor:0))
}

frappe.ui.form.on('Delivery Note',{
    onload:async function(frm){
        for(let row=0;row<frm.doc.items.length;row++){
            let ts_doc=locals[frm.doc.items[row].doctype][frm.doc.items[row].name]
            let uom = ts_doc.uom
            await frappe.model.set_value(frm.doc.items[row].doctype, frm.doc.items[row].name, 'uom', '')
            await frappe.model.set_value(frm.doc.items[row].doctype, frm.doc.items[row].name, 'uom', uom)
            let qty = ts_doc.qty
            await frappe.model.set_value(frm.doc.items[row].doctype, frm.doc.items[row].name, 'qty', qty)
            await frappe.model.set_value(frm.doc.items[row].doctype, frm.doc.items[row].name, 'ts_qty', (ts_doc.qty?ts_doc.qty:0)/(ts_doc.conversion_factor?ts_doc.conversion_factor:0))
            await frappe.model.set_value(frm.doc.items[row].doctype, frm.doc.items[row].name,'stock_qty',ts_doc.ts_qty?ts_doc.ts_qty:0)
        }
    }
})
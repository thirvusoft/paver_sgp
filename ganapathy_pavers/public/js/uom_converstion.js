frappe.provide("ganapathy_pavers");

ganapathy_pavers.uom_conversion = async function uom_conversion(item, from_uom = '', from_qty = 0, to_uom = '', throw_error = 1) {
    if (!item) {
        return
    }
    if (!to_uom) {
        return from_qty;
    }
    if (!from_uom) {
        const stockUOM = await frappe.call('frappe.client.get_value', {
            doctype: 'Item',
            fieldname: 'stock_uom',
            filters: { name: item },
        });
        from_uom = stockUOM.message.stock_uom;
    }
    const itemDoc = await frappe.call('frappe.client.get', {
        doctype: 'Item',
        name: item,
    });
    let fromConv = 0;
    let toConv = 0;
    itemDoc.message.uoms.forEach((row) => {
        if (row.uom === from_uom) {
            fromConv = row.conversion_factor;
        }
        if (row.uom === to_uom) {
            toConv = row.conversion_factor;
        }
    });
    if ((!fromConv || !toConv) && !throw_error) {
        return 0
    } 
    if (!fromConv) {
        frappe.throw(`Please Enter <b>${from_uom}</b> Conversion for item <b>${item}</b>`);
    }
    if (!toConv) {
        frappe.throw(`Please Enter <b>${to_uom}</b> Conversion for item <b>${item}</b>`);
    }
    
    return (parseFloat(from_qty) * (fromConv || 0)) / (toConv || 1);
}

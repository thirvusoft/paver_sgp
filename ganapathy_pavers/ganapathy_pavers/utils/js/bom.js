frappe.ui.form.on('BOM', {
    refresh: function(frm) {
        frm.remove_custom_button("Create","Work Order")
    	frm.add_custom_button("Work Order", ()=> {
            make_work_order(frm)
        },("Create"))
  }
});
function make_work_order(frm) {
    frm.events.setup_variant_prompt(frm, "Work Order", (frm, item, data, variant_items) => {
        frappe.call({
            method: "erpnext.manufacturing.doctype.work_order.work_order.make_work_order",
            args: {
                bom_no: frm.doc.name,
                item: item,
                qty: data.qty || 0.0,
                project: frm.doc.project,
                variant_items: variant_items
            },
            freeze: true,
            callback: function(r) {
                if(r.message) {
                    let doc = frappe.model.sync(r.message)[0];
                    frappe.set_route("Form", doc.doctype, doc.name);
                }
            }
        });
    });
}
function setup_variant_prompt(frm, title, callback, skip_qty_field) {
    const fields = [];

    if (frm.doc.has_variants) {
        fields.push({
            fieldtype: 'Link',
            label: __('Variant Item'),
            fieldname: 'item',
            options: "Item",
            reqd: 1,
            get_query: function() {
                return {
                    query: "erpnext.controllers.queries.item_query",
                    filters: {
                        "variant_of": frm.doc.item
                    }
                };
            }
        });
    }

    if (!skip_qty_field) {
        // fields.push({
        // 	fieldtype: 'Float',
        // 	label: __('Qty To Manufacture'),
        // 	fieldname: 'qty',
        // 	reqd: 1,
        // 	default: 1,
        // 	onchange: () => {
        // 		const { quantity, items: rm } = frm.doc;
        // 		const variant_items_map = rm.reduce((acc, item) => {
        // 			acc[item.item_code] = item.qty;
        // 			return acc;
        // 		}, {});
        // 		const mf_qty = cur_dialog.fields_list.filter(
        // 			(f) => f.df.fieldname === "qty"
        // 		)[0]?.value;
        // 		const items = cur_dialog.fields.filter(
        // 			(f) => f.fieldname === "items"
        // 		)[0]?.data;

        // 		if (!items) {
        // 			return;
        // 		}

        // 		items.forEach((item) => {
        // 			item.qty =
        // 				(variant_items_map[item.item_code] * mf_qty) /
        // 				quantity;
        // 		});

        // 		cur_dialog.refresh();
        // 	}
        // });
    }

    var has_template_rm = frm.doc.items.filter(d => d.has_variants === 1) || [];
    if (has_template_rm && has_template_rm.length > 0) {
        fields.push({
            fieldname: "items",
            fieldtype: "Table",
            label: __("Raw Materials"),
            fields: [
                {
                    fieldname: "item_code",
                    options: "Item",
                    label: __("Template Item"),
                    fieldtype: "Link",
                    in_list_view: 1,
                    reqd: 1,
                },
                {
                    fieldname: "variant_item_code",
                    options: "Item",
                    label: __("Variant Item"),
                    fieldtype: "Link",
                    in_list_view: 1,
                    reqd: 1,
                    get_query: function(data) {
                        if (!data.item_code) {
                            frappe.throw(__("Select template item"));
                        }

                        return {
                            query: "erpnext.controllers.queries.item_query",
                            filters: {
                                "variant_of": data.item_code
                            }
                        };
                    }
                },
                {
                    fieldname: "qty",
                    label: __("Quantity"),
                    fieldtype: "Float",
                    in_list_view: 1,
                    reqd: 1,
                },
                {
                    fieldname: "source_warehouse",
                    label: __("Source Warehouse"),
                    fieldtype: "Link",
                    options: "Warehouse"
                },
                {
                    fieldname: "operation",
                    label: __("Operation"),
                    fieldtype: "Data",
                    hidden: 1,
                }
            ],
            in_place_edit: true,
            data: [],
            get_data: function () {
                return [];
            },
        });
    }
    if(fields.length){let dialog = frappe.prompt(fields, data => {
        let item = data.item || frm.doc.item;
        let variant_items = data.items || [];

        variant_items.forEach(d => {
            if (!d.variant_item_code) {
                frappe.throw(__("Select variant item code for the template item {0}", [d.item_code]));
            }
        })

        callback(frm, item, data, variant_items);

    }, __(title), __("Create"));
}
else{
    callback(frm, frm.doc.item, {}, []);
}

    has_template_rm.forEach(d => {
        dialog.fields_dict.items.df.data.push({
            "item_code": d.item_code,
            "variant_item_code": "",
            "qty": d.qty,
            "source_warehouse": d.source_warehouse,
            "operation": d.operation
        });
    });

    // if (has_template_rm) {
    // 	dialog.fields_dict.items.grid.refresh();
    // }
}
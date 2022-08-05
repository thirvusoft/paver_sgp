// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shot Blast Costing', {
	refresh: function(frm) {
		frm.set_query("material_manufacturing","items",function(){
			return {
				"filters": {
					is_shot_blasting:1,
				}
			}
		})
	},
	setup: function(frm){
		frappe.db.get_single_value("USB Setting","default_curing_target_warehouse_for_setting").then(value =>{
			cur_frm.set_value("warehouse", value) 
		})
		cur_frm.refresh_field("warehouse");
	},
	validate: function(frm){	   
		total(frm) 
	},
	total_cost: function(frm){
		cur_frm.set_value("total_cost_per_sqft", frm.doc.total_cost/frm.doc.total_sqft) 
	},
	from_time: function(frm) {
		var field="total_hrs"
		total_hrs(frm,field,frm.doc.from_time,frm.doc.to_time)
	},
	to_time: function(frm){
		var field="total_hrs"
		total_hrs(frm,field,frm.doc.from_time,frm.doc.to_time)
	},
	total_hrs: function(frm){
		total_cost(frm)
	},
	refresh: function(frm){
		total_cost(frm)
	},
	additional_cost: function(frm){
		cur_frm.set_value('total_cost', frm.doc.additional_cost + frm.doc.labour_cost) 
	},
});
frappe.ui.form.on('Shot Blast Items', {
	material_manufacturing: function(frm,cdt,cdn){
		var row= locals[cdt][cdn]
		frappe.db.get_doc("Material Manufacturing", row.material_manufacturing).then((r) => {
			frappe.model.set_value(cdt,cdn,"item_name",r.item_to_manufacture)
			frappe.model.set_value(cdt,cdn,"batch",r.batch_no_curing)
			frappe.model.set_value(cdt,cdn,"bundle",r.no_of_bundle-r.shot_blasted_bundle)                
		});
	},
	damages_in_nos: function(frm,cdt,cdn){
		var row= locals[cdt][cdn]   
		frappe.db.get_doc("Material Manufacturing", row.material_manufacturing).then((r) => {
			frappe.db.get_value("Item", {"name": r.item_to_manufacture},"pavers_per_sqft", (sqft) => {
				frappe.model.set_value(cdt,cdn,"damages_in_sqft",row.damages_in_nos/sqft.pavers_per_sqft)                
			});                
		});           
	},
	bundle_taken: function(frm,cdt,cdn){
		var row= locals[cdt][cdn]   
		if(row.bundle_taken>row.bundle){
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
		frappe.db.get_value("Item", {"name": row.item_name},"bundle_per_sqr_ft", (sqft) => {
			frappe.model.set_value(cdt,cdn,"sqft",row.bundle_taken*sqft.bundle_per_sqr_ft)
		});   
	},
	sqft: function(frm,cdt,cdn){
		var row= locals[cdt][cdn]   
		total(frm) 
	},

});
function total(frm){
	var total_bundle = 0
	var total_sqft = 0
	for(var i=0;i<frm.doc.items.length;i++){
		total_bundle += frm.doc.items[i].bundle_taken
		total_sqft += frm.doc.items[i].sqft
		if(frm.doc.items[i].bundle_taken>frm.doc.items[i].bundle){
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
	}
	cur_frm.set_value("total_bundle",total_bundle)
	cur_frm.set_value("total_sqft",total_sqft)
}
function total_hrs(frm,field,from,to){
	frappe.call({
		method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_hrs",
        args:{
			from_time:from,
			to:to
		},
		callback(r){
			cur_frm.set_value(field, r.message);
		}
	})
}
function total_cost(frm){
	if(frm.doc.total_hrs > 0 && frm.doc.docstatus == 0){
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_expense",
			args:{
				workstation:frm.doc.workstation,
			},
			callback(r){
				cur_frm.set_value('labour_cost', r.message*frm.doc.total_hrs);
				cur_frm.set_value('total_cost', frm.doc.additional_cost + frm.doc.labour_cost);
			}
		})
	}
}
frappe.ui.form.on('Shot Blast Costing', {
	refresh : function(frm){
		set_css(frm);
	},
	// create_stock_entry: function(frm){
	// 	make_stock_entry(frm,"create_stock_entry")
	// },
});
function set_css(frm){
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.color = 'white'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.fontWeight = 'bold'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.backgroundColor = '#3399ff'
}
// function make_stock_entry(frm,type){
// 	frappe.call({
// 		method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.make_stock_entry",
// 		args:{
// 			doc:frm.doc,
// 			type:type
// 		},
// 	})
// }
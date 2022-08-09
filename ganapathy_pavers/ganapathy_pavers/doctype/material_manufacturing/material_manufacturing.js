// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
var uom_nos = 0
var uom_bundle = 0
frappe.ui.form.on('Material Manufacturing', {
	setup: function(frm){
		if(cur_frm.is_new() == 1){
			default_value("default_manufacture_operation","operation")
			default_value("default_rack_shift_workstation","workstation")
			default_value("default_manufacture_workstation","work_station")
			default_value("default_manufacture_source_warehouse","source_warehouse")
			default_value("default_manufacture_target_warehouse","target_warehouse")
			default_value("default_rack_shift_source_warehouse","rack_shift_source_warehouse")
			default_value("default_rack_shift_target_warehouse","rack_shift_target_warehouse")
			default_value("default_curing_source_warehouse","curing_source_warehouse")
			default_value("default_curing_target_warehouse","curing_target_warehouse")
			default_value("cement","cement_item")
			default_value("ggbs","ggbs_item")
			default_value("chips","chips_item_name")
			default_value("dust","dust_item_name")
			default_value("setting_oil","setting_oil_item_name")
		}
	},
	item_to_manufacture: function(frm){
		const find = frm.doc.item_to_manufacture.split("-");
		if(find[1] == "SHOT BLAST"){
			cur_frm.set_value("is_shot_blasting",1)
		}
		else{
			cur_frm.set_value("is_shot_blasting",0)
		}
	},
	is_shot_blasting: function(frm){
		if(frm.doc.is_shot_blasting == 1){
			default_value("default_curing_target_warehouse_for_setting","curing_target_warehouse")
		}
		else{
			default_value("default_curing_target_warehouse","curing_target_warehouse")
		}
	},
	from_time: function(frm) {
		var field="ts_total_hours"
		total_hrs(frm,field,frm.doc.from_time,frm.doc.to)
	},
	to: function(frm){
		var field="ts_total_hours"
		total_hrs(frm,field,frm.doc.from_time,frm.doc.to)
	},
	from_time_rack: function(frm) {
		var field="total_hours_rack"
		total_hrs(frm,field,frm.doc.from_time_rack,frm.doc.to_time_rack)
	},
	to_time_rack: function(frm){
		var field="total_hours_rack"
		total_hrs(frm,field,frm.doc.from_time_rack,frm.doc.to_time_rack)
	},
	from_time_curing: function(frm) {
		var field="total_hrs"
		total_hrs(frm,field,frm.doc.from_time_curing,frm.doc.to_time_curing)
	},
	to_time_curing: function(frm){
		var field="total_hrs"
		total_hrs(frm,field,frm.doc.from_time_curing,frm.doc.to_time_curing)
	},
	no_of_bundle: function(frm){
		cur_frm.set_value("shot_blasted_bundle",frm.doc.no_of_bundle)
	},
	shot_blasted_bundle: function(frm){
		if(frm.doc.shot_blasted_bundle == 0){
			cur_frm.set_value("status1","Completed")
			frm.save()
		}
	},
	additional_cost: function(frm){
		cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense) 
	},
	rack_shifting_additional_cost: function(frm){
		cur_frm.set_value('rack_shifting_total_expense', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense + frm.doc.strapping_cost) 
	},
	strapping_cost: function(frm){
		cur_frm.set_value('rack_shifting_total_expense', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense + frm.doc.strapping_cost) 
	},
	production_qty: function(frm){
		cur_frm.set_value('total_completed_qty', frm.doc.production_qty - frm.doc.damage_qty) 
		frappe.db.get_value("Item", {"name": frm.doc.item_to_manufacture},"pavers_per_sqft", (sqft) => {
			cur_frm.set_value('production_sqft', frm.doc.total_completed_qty / sqft.pavers_per_sqft)		
		}); 
	},
	damage_qty: function(frm){
		cur_frm.set_value('total_completed_qty', frm.doc.production_qty - frm.doc.damage_qty) 
		frappe.db.get_value("Item", {"name": frm.doc.item_to_manufacture},"pavers_per_sqft", (sqft) => {
			cur_frm.set_value('production_sqft', frm.doc.total_completed_qty / sqft.pavers_per_sqft)		
		});
	},
	curing_damaged_qty: function(frm){
		cur_frm.set_value('no_of_bundle', frm.doc.no_of_bundle - frm.doc.curing_damaged_qty) 
	},
	rack_shift_damage_qty: function(frm){
		cur_frm.set_value('total_no_of_produced_qty', frm.doc.total_no_of_produced_qty - frm.doc.rack_shift_damage_qty) 
	},
	rate_per_hrs: function(frm){
		cur_frm.set_value('labour_cost', (frm.doc.rate_per_hrs * frm.doc.total_hrs)/frm.doc.no_of_division)
	},
	total_hrs: function(frm){
		cur_frm.set_value('labour_cost', (frm.doc.rate_per_hrs * frm.doc.total_hrs)/frm.doc.no_of_division)
	},
	no_of_division: function(frm){
		cur_frm.set_value('labour_cost', (frm.doc.rate_per_hrs * frm.doc.total_hrs)/frm.doc.no_of_division)
	},
	refresh: function(frm){
		if(frm.doc.docstatus == 0){
		if(frm.doc.ts_total_hours > 0 && frm.doc.docstatus == 0){
			frappe.call({
				method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_expense",
				args:{
					workstation:frm.doc.work_station,
					operators_cost : frm.doc.operators_cost_in_manufacture,
					labour_cost : frm.doc.labour_cost_in_manufacture,
					tot_work_hrs: frm.doc.ts_total_hours,
					tot_hrs : frm.doc.total_working_hrs,
				},
				callback(r){
					cur_frm.set_value('total_manufacturing_expense', (r.message[0]*frm.doc.ts_total_hours)+r.message[1]);
					cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense);
				}
			})
		}
		if(frm.doc.total_hours_rack > 0 && frm.doc.docstatus == 0){
			frappe.call({
				method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_expense",
				args:{
					workstation:frm.doc.workstation,
					operators_cost : frm.doc.operators_cost_in_manufacture,
					labour_cost : frm.doc.labour_cost_in_manufacture,
					tot_work_hrs: frm.doc.total_hours_rack,
					tot_hrs : frm.doc.total_working_hrs,
				},
				callback(r){
					cur_frm.set_value('total_rack_shift_expense', (r.message[0]*frm.doc.total_hours_rack)+r.message[1]);
					cur_frm.set_value('rack_shifting_total_expense', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense + frm.doc.strapping_cost);
				}
			})
		}
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.find_batch",
			args:{
				name:frm.doc.name,
			},
			callback(r){
				if (r.message){
					cur_frm.set_value('batch_no_manufacture', r.message[0]);
					cur_frm.set_value('batch_no_rack_shifting', r.message[1]);
					cur_frm.set_value('batch_no_curing', r.message[2]);
				}
			}
		})
		std_item(frm)
		item_adding(frm)
		var total_bundle = 0
		for(var i=0;i<frm.doc.items.length;i++){
			total_bundle += frm.doc.items[i].amount
			if(frm.doc.items[i].amount == 0){
				frappe.throw("Kindly Enter Rate in Item Table")
			}
		}
		cur_frm.set_value('total_raw_material', total_bundle);
		if(frm.doc.setting_oil_item_name){
			cur_frm.set_value('total_setting_oil_qty',(frm.doc.raw_material_consumption.length*frm.doc.setting_oil_qty)/1000)
		  }
		cur_frm.set_value('strapping_cost', frm.doc.strapping_cost_per_sqft*frm.doc.production_sqft);
		cur_frm.set_value('total_expense_per_sqft', (total_bundle+frm.doc.total_expense)/frm.doc.production_sqft);
		cur_frm.set_value('rack_shifting_total_expense_per_sqft', (frm.doc.rack_shifting_total_expense)/frm.doc.production_sqft);
		cur_frm.set_value('labour_cost_per_sqft', frm.doc.labour_cost/frm.doc.production_sqft);
		cur_frm.set_value('item_price', frm.doc.total_expense_per_sqft+frm.doc.rack_shifting_total_expense_per_sqft+frm.doc.labour_cost_per_sqft+frm.doc.shot_blast_per_sqft);
		}
	},
	bom_no: function(frm){
		item_adding(frm)
	},
	strapping_cost_per_sqft: function(frm){
		cur_frm.set_value('strapping_cost', frm.doc.strapping_cost_per_sqft*frm.doc.production_sqft);
	},
	total_completed_qty: function(frm){
		cur_frm.set_value('total_no_of_produced_qty', frm.doc.total_completed_qty);
	},
	total_no_of_produced_qty: function(frm){
		var bundle_cf = 0
		var nos_cf = 0
		var default_cf = 0
		frappe.db.get_single_value("USB Setting","default_manufacture_uom").then(value =>{
			uom_nos = value 
		})
		frappe.db.get_single_value("USB Setting","default_rack_shift_uom").then(value =>{
			uom_bundle = value 
		})
		frappe.db.get_doc('Item', frm.doc.item_to_manufacture).then((doc) => {
			var default_uom = doc.stock_uom
			for(var i of doc.uoms){
				if(uom_bundle == i.uom){
					bundle_cf=i.conversion_factor	
				}
				if(uom_nos == i.uom){
					nos_cf=i.conversion_factor	
				}
				if(default_uom == i.uom){
					default_cf=i.conversion_factor	
				}
			}
			var total_amount = (frm.doc.total_no_of_produced_qty*nos_cf)/bundle_cf
			cur_frm.set_value('remaining_qty', ((frm.doc.total_no_of_produced_qty*nos_cf)%bundle_cf)/nos_cf);
			if(total_amount >= 1){
				cur_frm.set_value('total_no_of_bundle', Math.floor(total_amount));
			}
			else{
				cur_frm.set_value('total_no_of_bundle', 0);
			}
		});
	},
	total_no_of_bundle: function(frm){
		cur_frm.set_value('no_of_bundle', frm.doc.total_no_of_bundle);
	},
	onload: function(frm){
		frm.set_query("source_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		// var company = frappe.get_single('Global Defaults').default_company
		// cur_frm.set_value("company",company)
		
		frm.set_query("target_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("rack_shift_source_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("rack_shift_target_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("curing_source_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("curing_target_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("cement_item",function(){
			return {
				"filters": {
					item_group:"Raw Material"
				}
			}
		})
		frm.set_query("ggbs_item",function(){
			return {
				"filters": {
					item_group:"Raw Material"
				}
			}
		})
		frm.set_query("item_to_manufacture",function(){
			return {
					filters: [
						['Item', 'item_group', '!=', 'Raw Material']
					]
			}
		})
		frm.set_query("bom_no",function(){
			return {
				"filters": {
					item:frm.doc.item_to_manufacture,
					is_default:1
				}
			}
		})
	},
	create_stock_entry: function(frm){
		make_stock_entry(frm,"create_stock_entry")
	},
	create_rack_shiftingstock_entry: function(frm){
		make_stock_entry(frm,"create_rack_shiftingstock_entry")
	},
	curing_stock_entry: function(frm){
		make_stock_entry(frm,"curing_stock_entry")
	}
});
function make_stock_entry(frm,type){
	frappe.call({
		method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.make_stock_entry",
		args:{
			doc:frm.doc,
			type:type
		},
		callback: function(r){
			if(r.message){
				cur_frm.set_value("status1", r.message);
				cur_frm.refresh()
				frm.save()
			}
			
		 }
	})
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
function item_adding(frm){
	if(frm.doc.bom_no){
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.add_item",
			args:{
				bom_no:frm.doc.bom_no,
				doc:cur_frm.doc
			},
			callback(r){
				// cur_frm.set_value('items',r.message)
				var item1=[]
				for (const d of r.message){
					item1.push(d.item_code)
				}
				for (const d of r.message){
					for(const i of frm.doc.items){
						if(i.item_code == d.item_code && d.source_warehouse == i.source_warehouse){
							item1.indexOf(d.item_code) !== -1 && item1.splice(item1.indexOf(d.item_code), 1)
						}
					}
				}
				if(item1){
					for(var i=0;i<item1.length;i++){		
						for (const d of r.message){
							if(d.item_code == item1[i]){
								var row = frm.add_child('items');
								row.item_code = d.item_code;
								row.qty = d.qty;
								row.stock_uom = d.stock_uom;
								row.uom = d.uom;
								row.rate = d.rate;
								row.amount= d.amount
								row.source_warehouse= d.source_warehouse
							}
						}
					}
				}
				refresh_field("items");
			}
		})
	}
}
function std_item(frm){
	if(frm.doc.bom_no){
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.std_item",
			args:{
				doc:cur_frm.doc
			},
			callback(r){
				// cur_frm.set_value('items',r.message)
				var item1=[]
				for (const d of r.message){
					item1.push(d.item_code)
				}
				for (const d of r.message){
					for(const i of frm.doc.items){
						if(i.item_code == d.item_code && d.source_warehouse == i.source_warehouse){
							item1.indexOf(d.item_code) !== -1 && item1.splice(item1.indexOf(d.item_code), 1)
						}
					}
				}
				if(item1){
					for(var i=0;i<item1.length;i++){		
						for (const d of r.message){
							if(d.item_code == item1[i]){
								var row = frm.add_child('items');
								row.item_code = d.item_code;
								row.qty = d.qty;
								row.stock_uom = d.stock_uom;
								row.uom = d.uom;
								row.rate = d.rate;
								row.amount= d.amount
							}
						}
					}
				}
				refresh_field("items");
			}
		})
	}
}
function default_value(usb_field,set_field){
	frappe.db.get_single_value("USB Setting",usb_field).then(value =>{
		cur_frm.set_value(set_field, value) 
	})
	cur_frm.refresh_field(set_field);
}
frappe.ui.form.on('BOM Item', {
	rate: function(frm, cdt, cdn) {
		total_amount(frm, cdt, cdn)
		frappe.model.set_value(cdt,cdn,"item_tax_template",r.message)
	},
	qty: function(frm, cdt, cdn){
		total_amount(frm, cdt, cdn)
	},
	item_code: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.item_data",
			args:{
				item_code:d.item_code,
			},
			callback(r){
				frappe.model.set_value(cdt,cdn,"rate",r.message[2])
				frappe.model.set_value(cdt,cdn,"uom",r.message[1])
				frappe.model.set_value(cdt,cdn,"stock_uom",r.message[1])
			}
		})
		total_amount(frm, cdt, cdn)
	},
});
function total_amount(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt,cdn,"amount",d.qty*d.rate)
}
frappe.ui.form.on('Material Manufacturing', {
	refresh : function(frm){
		set_css(frm);
	}
});

function set_css(frm){
document.querySelectorAll("[data-fieldname='curing_stock_entry']")[1].style.color = 'white'
document.querySelectorAll("[data-fieldname='curing_stock_entry']")[1].style.fontWeight = 'bold'
document.querySelectorAll("[data-fieldname='curing_stock_entry']")[1].style.backgroundColor = '#3399ff'
document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.color = 'white'
document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.fontWeight = 'bold'
document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.backgroundColor = '#3399ff'
document.querySelectorAll("[data-fieldname='create_rack_shiftingstock_entry']")[1].style.color = 'white'
document.querySelectorAll("[data-fieldname='create_rack_shiftingstock_entry']")[1].style.fontWeight = 'bold'
document.querySelectorAll("[data-fieldname='create_rack_shiftingstock_entry']")[1].style.backgroundColor = '#3399ff'
}

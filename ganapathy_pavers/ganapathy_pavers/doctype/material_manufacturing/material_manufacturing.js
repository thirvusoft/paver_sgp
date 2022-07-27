// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
var uom_nos = 0
var uom_bundle = 0
frappe.ui.form.on('Material Manufacturing', {
	setup: function(frm){
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
	additional_cost: function(frm){
		cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense) 
	},
	rack_shifting_additional_cost: function(frm){
		cur_frm.set_value('rack_shifting_total_expense', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense) 
	},
	// damage_qty: function(frm){
	// 	cur_frm.set_value('total_completed_qty', frm.doc.total_completed_qty - frm.doc.damage_qty) 
	// },
	// rack_shift_damage_qty: function(frm){
	// 	cur_frm.set_value('total_no_of_produced_qty', frm.doc.total_no_of_produced_qty - frm.doc.rack_shift_damage_qty) 
	// },
	refresh: function(frm){
		if(frm.doc.ts_total_hours > 0 ){
			frappe.call({
				method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_expense",
				args:{
					workstation:frm.doc.work_station,
				},
				callback(r){
					cur_frm.set_value('total_manufacturing_expense', r.message*frm.doc.ts_total_hours);
					cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense);
				}
			})
		}
		if(frm.doc.total_hours_rack > 0 ){
			frappe.call({
				method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_expense",
				args:{
					workstation:frm.doc.workstation,
				},
				callback(r){
					cur_frm.set_value('total_rack_shift_expense', r.message*frm.doc.total_hours_rack);
					cur_frm.set_value('rack_shifting_total_expense', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense);
				}
			})
		}
		std_item(frm)
		item_adding(frm)
	},
	bom_no: function(frm){
		item_adding(frm)
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
			var total_amount = (frm.doc.total_no_of_produced_qty/default_cf)/bundle_cf
			cur_frm.set_value('remaining_qty', Math.round((frm.doc.total_no_of_produced_qty/default_cf)%bundle_cf));
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
					item:frm.doc.item_to_manufacture
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
		}
	})
	frm.refresh()
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
				var t = 0
				for (const d of r.message){
					for(const i of frm.doc.items){
						if(i.item_code == d.item_code){
							t=1
						}
					}
				}
				if(t == 0){
					for (const d of r.message){
						var row = frm.add_child('items');
						row.item_code = d.item_code;
						row.qty = d.qty;
						row.stock_uom = d.stock_uom;
						row.uom = d.uom;
						row.rate = d.rate;
						row.amount= d.amount
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
				var t = 0
				for (const d of r.message){
					for(const i of frm.doc.items){
						if(i.item_code == d.item_code){
							t=1
						}
					}
				}
				if(t == 0){
					for (const d of r.message){
						var row = frm.add_child('items');
						row.item_code = d.item_code;
						row.qty = d.qty;
						row.stock_uom = d.stock_uom;
						row.uom = d.uom;
						row.rate = d.rate;
						row.amount= d.amount
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
	refresh_field(usb_field);
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
// import FileUploaderComponent from './FileUploader.vue';

// export default class FileUploader {
// 	constructor({
// 		wrapper,
// 		method,
// 		on_success,
// 		doctype,
// 		docname,
// 		fieldname,
// 		files,
// 		folder,
// 		restrictions,
// 		upload_notes,
// 		allow_multiple,
// 		as_dataurl,
// 		disable_file_browser,
// 		frm
// 	} = {}) {

// 		frm && frm.attachments.max_reached(true);

// 		if (!wrapper) {
// 			this.make_dialog();
// 		} else {
// 			this.wrapper = wrapper.get ? wrapper.get(0) : wrapper;
// 		}

// 		this.$fileuploader = new Vue({
// 			el: this.wrapper,
// 			render: h => h(FileUploaderComponent, {
// 				props: {
// 					show_upload_button: !Boolean(this.dialog),
// 					doctype,
// 					docname,
// 					fieldname,
// 					method,
// 					folder,
// 					on_success,
// 					restrictions,
// 					upload_notes,
// 					allow_multiple,
// 					as_dataurl,
// 					disable_file_browser,
// 				}
// 			})
// 		});

// 		this.uploader = this.$fileuploader.$children[0];

// 		this.uploader.$watch('files', (files) => {
// 			let all_private = files.every(file => file.private);
// 			if (this.dialog) {
// 				this.dialog.set_secondary_action_label(all_private ? __('Set all public') : __('Set all private'));
// 			}
// 		}, { deep: true });

// 		if (files && files.length) {
// 			this.uploader.add_files(files);
// 		}

// 		this.uploader.$watch('close_dialog', (close_dialog) => {
// 			if (close_dialog) {
// 				this.dialog && this.dialog.hide();
// 			}
// 		});
// 	}

// 	upload_files() {
// 		this.dialog && this.dialog.get_primary_btn().prop('disabled', true);
// 		return this.uploader.upload_files()
// 			.then(() => {
// 				this.dialog && this.dialog.hide();
// 			});
// 	}

// 	make_dialog() {
// 		this.dialog = new frappe.ui.Dialog({
// 			title: __('Upload'),
// 			primary_action_label: __('Upload'),
// 			primary_action: () => this.upload_files(),
// 			secondary_action_label: __('Set all private'),
// 			secondary_action: () => {
// 				this.uploader.toggle_all_private();
// 			}
// 		});

// 		this.wrapper = this.dialog.body;
// 		this.dialog.show();
// 		this.dialog.$wrapper.on('hidden.bs.modal', function() {
// 			$(this).data('bs.modal', null);
// 			$(this).remove();
// 		});
// 	}
// }
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

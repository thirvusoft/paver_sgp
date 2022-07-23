// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Manufacturing', {
	from_time: function(frm) {
		total_hrs(frm)
	},
	to: function(frm){
		total_hrs(frm)
	},
	additional_cost: function(frm){
		cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense) 
	},
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
	},
	bom_no: function(frm){
		if(frm.doc.bom_no){
			frappe.call({
				method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.add_item",
				args:{
					bom_no:frm.doc.bom_no,
					doc:cur_frm.doc
				},
				callback(r){
					cur_frm.set_value('items',r.message)
				}
			})
		}
	},
	onload: function(frm){
		frm.set_query("source_warehouse",function(){
			return {
				"filters": {
					is_group:0
				}
			}
		})
		// var company = frappe.get_single('Global Defaults').default_company
		// cur_frm.set_value("company",company)
		
		frm.set_query("target_warehouse",function(){
			return {
				"filters": {
					is_group:0
				}
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
	}
});
function total_hrs(frm){
	frappe.call({
		method:"ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_hrs",
        args:{
			from_time:frm.doc.from_time,
			to:frm.doc.to
		},
		callback(r){
			cur_frm.set_value('ts_total_hours', r.message);
		}
	})
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

// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Card', {
	setup: function(frm) {
		frm.set_query('operation', function() {
			return {
				query: 'erpnext.manufacturing.doctype.job_card.job_card.get_operations',
				filters: {
					'work_order': frm.doc.work_order
				}
			};
		});

		frm.set_indicator_formatter('sub_operation',
			function(doc) {
				if (doc.status == "Pending") {
					return "red";
				} else {
					return doc.status === "Complete" ? "green" : "orange";
				}
			}
		);
	},

	on_submit: function(frm){
		let work_order_frm={};
		frappe.db.get_doc("Work Order", frm.doc.work_order).then(function(data){
			work_order_frm = data
			let purpose = frm.doc.stock_entry_type
			return frappe.xcall('erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry', {
				'work_order_id': work_order_frm.name,
				'purpose': frm.doc.stock_entry_type,
				'qty': frm.doc.total_completed_qty,
				'sw' : frm.doc.source_warehouse,
				'tw' : frm.doc.target_warehouse,
				'manufacturing_uom': frm.doc.manufacturing_uom,
				'repack_uom': frm.doc.repack_uom,
				'batch': frm.doc.remaining_item_batch_qty
			}).then(stock_entry => {
				frappe.model.sync(stock_entry);
				frappe.set_route('Form', stock_entry.doctype, stock_entry.name);
			});
		})
		
	},
	
	refresh: function(frm) {
		if(cur_frm.doc.status != 'Completed' || cur_frm.doc.status != 'Open'){
		cur_frm.add_custom_button(__("Show Bundle Info"), function() {
			if(cur_frm.doc.stock_entry_type == "Manufacture"){
				frappe.msgprint("Couldn't able to show information for 'Manufacture'")
			}
			else if(cur_frm.doc.stock_entry_type == "Repack"){
				frappe.db.get_list("Work Order",{filters: {name:cur_frm.doc.work_order}, fields:['parent_work_order']}).then( (parent_wo)=>{
					frappe.db.get_list("Job Card",{filters:{'work_order':parent_wo[0].parent_work_order}, fields:['total_completed_qty','repack_uom']}).then( (qty)=>{
						frappe.msgprint({title:"Previous Job Card Stock Information", message:"<p><b>JobCard:</b> "+parent_wo[0].parent_work_order+"</p><p><b>Qty:</b> "+qty[0].total_completed_qty+"</p><p><b>UOM:</b> Pcs</p>"})
					})
				})
			}
			else if(cur_frm.doc.stock_entry_type == "Material Transfer"){
				frappe.db.get_list("Work Order",{filters: {name:cur_frm.doc.work_order}, fields:['parent_work_order']}).then( (parent_wo)=>{
					frappe.db.get_list("Job Card",{filters:{'work_order':parent_wo[0].parent_work_order}, fields:['total_completed_qty','manufacturing_uom']}).then( (qty)=>{
						frappe.msgprint({title:"Previous Job Card Stock Information", message:"<p><b>JobCard</b>: "+parent_wo[0].parent_work_order+"</p><p><b>Qty:</b> "+qty[0].total_completed_qty+"</p><p><b>UOM:</b> Bundle</p>	"})
					})
				})
			}
		}); 


		cur_frm.add_custom_button(__("Add Remaining Pavers"), function(){
			var item = cur_frm.doc.production_item
			var bom = cur_frm.doc.bom_no
			var operation = cur_frm.doc.operation 
			var work_order = cur_frm.doc.work_order
			let jc_scrap_qty=0
				if(cur_frm.doc.scrap_items.length){
					cur_frm.doc.scrap_items.forEach( (i)=>{
						jc_scrap_qty+=i.stock_qty
					})
				}
			if(item && bom && operation && work_order && cur_frm.doc.stock_entry_type != "Manufacture"){
			let added_qty=0
			let added_jc=''
			let remaining_qty=0
			frappe.call({
				method: "erpnext.manufacturing.doctype.job_card.job_card.get_remaining_pavers",
				args: {
					work_order: work_order,
					item: item,
					operation: operation,
					se_type: cur_frm.doc.stock_entry_type,
					scrap_qty: jc_scrap_qty,
					cur_jc_qty: cur_frm.doc.total_completed_qty  
				},
				callback(r){
						var d=new frappe.ui.Dialog({
							title: "Add Remaining Pavers",
							fields: r.message[0],
							primary_action: function(data){
								for(var i=1;i<=r.message[1];i++){
									if(data['jc_add_qty'+i.toString()] > 0) {
									if(data['jc_add_qty'+i.toString()]<=data['jc_qty'+i.toString()]){
										added_qty.push(
											data['jc_add_qty'+i.toString()]
										)
										added_jc.push(
											data['jc_name'+i.toString()]
										)
										remaining_qty.push(
											data['jc_qty'+i.toString()]
										)
									}
									else{
										frappe.throw("'Added qty' must be less than 'remaining qty'")
									}
								}
								}
								if(added_jc.length){
									var d1 = new frappe.ui.Dialog({
										title:"Choose Start and End Time",
										fields:[
											{'fieldname':'start_time','label':"Start Time",'fieldtype':'Datetime','reqd':1},
											{"fieldtype":'Column Break'},
											{'fieldname':'end_time','label':"End Time",'fieldtype':'Datetime','reqd':1}
										],
										primary_action: function(times){
											frappe.call({
												method:"erpnext.manufacturing.doctype.job_card.job_card.update_jc_remaining_pavers",
												args:{qtys:added_qty,jcs:added_jc,max_qty:remaining_qty,times:times, wo:cur_frm.doc.work_order},
												callback: function(r){
													let hrs = r.message[1]
													let mins = r.message[1] * 60
													function add_time_log(employee){
														var shift_id=0;
														if(cur_frm.doc.time_logs.length){
														shift_id=cur_frm.doc.time_logs.at(-1).shift_id + 1
														}
														r.message[2].forEach( (i)=>{
															let batch_child = cur_frm.add_child("remaining_item_batch_qty")
															batch_child.batch_no = i[0]
															batch_child.qty = i[1]
															cur_frm.refresh()
														})
														
														employee.forEach( (i)=>{
															let child = cur_frm.add_child("time_logs")
															child.employee = i['employee']
															child.from_time = times['start_time']
															child.to_time = times['end_time']
															child.completed_qty = r.message[0]
															child.shift_id = shift_id
															child.time_in_mins = mins
															child.time_in_hrs = hrs
															cur_frm.refresh()
														})
														cur_frm.save()
													}
													if(cur_frm.doc.employee.length){
														add_time_log(cur_frm.doc.employee)
													}
													else{
														var employee_list=[]
														frappe.db.get_doc("Workstation",frm.doc.workstation).then(ts_workstation_details=>{
															for(var i=0;i<ts_workstation_details.ts_labor.length;i++){
																employee_list.push({employee:ts_workstation_details.ts_labor[i].ts_labour})
															}
															frm.events.start_job(frm, "Work In Progress", employee_list);
														})

													}
												}
											})
											d1.hide()
											d.hide()
										}
									})
									d1.show()
								
							}
							else{
								d.hide()
							}
								
							}
						})
						d.show()
				}
			})
		}
		})
	}
		if(frm.doc.doc_onload == 0){
			frm.set_value('time_logs',[])
			frm.set_value('doc_onload',1)
		}
		frappe.flags.pause_job = 0;
		frappe.flags.resume_job = 0;
		let has_items = frm.doc.items && frm.doc.items.length;

		if (frm.doc.__onload.work_order_stopped) {
			frm.disable_save();
			return;
		}

		if (!frm.doc.__islocal && has_items && frm.doc.docstatus < 2) {
			let to_request = frm.doc.for_quantity > frm.doc.transferred_qty;
			let excess_transfer_allowed = frm.doc.__onload.job_card_excess_transfer;

			if (to_request || excess_transfer_allowed) {
				frm.add_custom_button(__("Material Request"), () => {
					frm.trigger("make_material_request");
				});
			}

			// check if any row has untransferred materials
			// in case of multiple items in JC
			let to_transfer = frm.doc.items.some((row) => row.transferred_qty < row.required_qty);

			if (to_transfer || excess_transfer_allowed) {
				frm.add_custom_button(__("Material Transfer"), () => {
					frm.trigger("make_stock_entry");
				}).addClass("btn-primary");
			}
		}

		if (frm.doc.docstatus == 1 && !frm.doc.is_corrective_job_card) {
			frm.trigger('setup_corrective_job_card');
		}

		frm.set_query("quality_inspection", function() {
			return {
				query: "erpnext.stock.doctype.quality_inspection.quality_inspection.quality_inspection_query",
				filters: {
					"item_code": frm.doc.production_item,
					"reference_name": frm.doc.name
				}
			};
		});

		frm.trigger("toggle_operation_number");

		if (frm.doc.docstatus == 0 && !frm.is_new() 
		// && (frm.doc.for_quantity > frm.doc.total_completed_qty || !frm.doc.for_quantity)
			&& (frm.doc.items || !frm.doc.items.length || frm.doc.for_quantity == frm.doc.transferred_qty)) {
			frm.trigger("prepare_timer_buttons");
		}
		frm.trigger("setup_quality_inspection");

		if (frm.doc.work_order) {
			frappe.db.get_value('Work Order', frm.doc.work_order,
				'transfer_material_against').then((r) => {
				if (r.message.transfer_material_against == 'Work Order') {
					frm.set_df_property('items', 'hidden', 1);
				}
			});
		}
	},

	setup_quality_inspection: function(frm) {
		let quality_inspection_field = frm.get_docfield("quality_inspection");
		quality_inspection_field.get_route_options_for_new_doc = function(frm) {
			return  {
				"inspection_type": "In Process",
				"reference_type": "Job Card",
				"reference_name": frm.doc.name,
				"item_code": frm.doc.production_item,
				"item_name": frm.doc.item_name,
				"item_serial_no": frm.doc.serial_no,
				"batch_no": frm.doc.batch_no,
				"quality_inspection_template": frm.doc.quality_inspection_template,
			};
		};
	},

	setup_corrective_job_card: function(frm) {
		frm.add_custom_button(__('Corrective Job Card'), () => {
			let operations = frm.doc.sub_operations.map(d => d.sub_operation).concat(frm.doc.operation);

			let fields = [
				{
					fieldtype: 'Link', label: __('Corrective Operation'), options: 'Operation',
					fieldname: 'operation', get_query() {
						return {
							filters: {
								"is_corrective_operation": 1
							}
						};
					}
				}, {
					fieldtype: 'Link', label: __('For Operation'), options: 'Operation',
					fieldname: 'for_operation', get_query() {
						return {
							filters: {
								"name": ["in", operations]
							}
						};
					}
				}
			];

			frappe.prompt(fields, d => {
				frm.events.make_corrective_job_card(frm, d.operation, d.for_operation);
			}, __("Select Corrective Operation"));
		}, __('Make'));
	},

	make_corrective_job_card: function(frm, operation, for_operation) {
		frappe.call({
			method: 'erpnext.manufacturing.doctype.job_card.job_card.make_corrective_job_card',
			args: {
				source_name: frm.doc.name,
				operation: operation,
				for_operation: for_operation
			},
			callback: function(r) {
				if (r.message) {
					frappe.model.sync(r.message);
					frappe.set_route("Form", r.message.doctype, r.message.name);
				}
			}
		});
	},

	operation: function(frm) {
		frm.trigger("toggle_operation_number");

		if (frm.doc.operation && frm.doc.work_order) {
			frappe.call({
				method: "erpnext.manufacturing.doctype.job_card.job_card.get_operation_details",
				args: {
					"work_order":frm.doc.work_order,
					"operation":frm.doc.operation
				},
				callback: function (r) {
					if (r.message) {
						if (r.message.length == 1) {
							frm.set_value("operation_id", r.message[0].name);
						} else {
							let args = [];

							r.message.forEach((row) => {
								args.push({ "label": row.idx, "value": row.name });
							});

							let description = __("Operation {0} added multiple times in the work order {1}",
								[frm.doc.operation, frm.doc.work_order]);

							frm.set_df_property("operation_row_number", "options", args);
							frm.set_df_property("operation_row_number", "description", description);
						}

						frm.trigger("toggle_operation_number");
					}
				}
			})
		}
	},

	operation_row_number(frm) {
		if (frm.doc.operation_row_number) {
			frm.set_value("operation_id", frm.doc.operation_row_number);
		}
	},

	toggle_operation_number(frm) {
		frm.toggle_display("operation_row_number", !frm.doc.operation_id && frm.doc.operation);
		frm.toggle_reqd("operation_row_number", !frm.doc.operation_id && frm.doc.operation);
	},

	prepare_timer_buttons: function(frm) {
		frm.trigger("make_dashboard");

		if (!frm.doc.started_time && !frm.doc.current_time) {
			frm.add_custom_button(__("Start Job"), () => {
                if ((frm.doc.employee && !frm.doc.employee.length) || !frm.doc.employee) {
                    // frappe.prompt({fieldtype: 'Table MultiSelect', label: __('Select Employees'),
                    //  options: "Job Card Time Log", fieldname: 'employees'}, d => {
                            var employee_list=[]
                            frappe.db.get_doc("Workstation",frm.doc.workstation).then(ts_workstation_details=>{
                                for(var i=0;i<ts_workstation_details.ts_labor.length;i++){
                                    employee_list.push({employee:ts_workstation_details.ts_labor[i].ts_labour})
                                }
                                frm.events.start_job(frm, "Work In Progress", employee_list);
                            })
                    // }, __("Assign Job to Employee"));
                } else {
                    frm.events.start_job(frm, "Work In Progress", frm.doc.employee);
                }
            }).addClass("btn-primary");
		} else if (frm.doc.status == "On Hold") {
			frm.add_custom_button(__("Resume Job"), () => {
				frm.events.start_job(frm, "Resume Job", frm.doc.employee);
			}).addClass("btn-primary");
		} else {
			frm.add_custom_button(__("Pause Job"), () => {
				frm.events.complete_job(frm, "On Hold");
			});

			frm.add_custom_button(__("Complete Job"), () => {
				var sub_operations = frm.doc.sub_operations;

				let set_qty = true;
				if (sub_operations && sub_operations.length > 1) {
					set_qty = false;
					let last_op_row = sub_operations[sub_operations.length - 2];

					if (last_op_row.status == 'Complete') {
						set_qty = true;
					}
				}

				if (set_qty) {
					frappe.prompt({fieldtype: 'Float', label: __('Completed Quantity'),
						fieldname: 'qty', default: frm.doc.for_quantity}, data => {
						frm.events.complete_job(frm, "Complete", data.qty);
					}, __("Enter Value"));
				} else {
					frm.events.complete_job(frm, "Complete", 0.0);
				}
			}).addClass("btn-primary");
		}
	},

	start_job: function(frm, status, employee) {
		if(!employee.length){frappe.throw({title:"Not Found",message:"Employee not found in workstation <b>"+frm.doc.workstation+"</b>"})}
		const args = {
			job_card_id: frm.doc.name,
			start_time: frappe.datetime.now_datetime(),
			employees: employee,
			status: status
		};
		frm.events.make_time_log(frm, args);
	},

	complete_job: function(frm, status, completed_qty) {
		const args = {
			job_card_id: frm.doc.name,
			complete_time: frappe.datetime.now_datetime(),
			status: status,
			completed_qty: completed_qty
		};
		frm.events.make_time_log(frm, args);
	},

	make_time_log: function(frm, args) {
		frm.events.update_sub_operation(frm, args);

		frappe.call({
			method: "erpnext.manufacturing.doctype.job_card.job_card.make_time_log",
			args: {
				args: args
			},
			freeze: true,
			callback: function () {
				frm.reload_doc();
				frm.trigger("make_dashboard");
			}
		});
	},

	update_sub_operation: function(frm, args) {
		if (frm.doc.sub_operations && frm.doc.sub_operations.length) {
			let sub_operations = frm.doc.sub_operations.filter(d => d.status != 'Complete');
			if (sub_operations && sub_operations.length) {
				args["sub_operation"] = sub_operations[0].sub_operation;
			}
		}
	},

	validate: function(frm) {
		if ((!frm.doc.time_logs || !frm.doc.time_logs.length) && frm.doc.started_time) {
			frm.trigger("reset_timer");
		}
	},

	reset_timer: function(frm) {
		frm.set_value('started_time' , '');
	},

	make_dashboard: function(frm) {
		if(frm.doc.__islocal)
			return;

		frm.dashboard.refresh();
		const timer = `
			<div class="stopwatch" style="font-weight:bold;margin:0px 13px 0px 2px;
				color:#545454;font-size:18px;display:inline-block;vertical-align:text-bottom;>
				<span class="hours">00</span>
				<span class="colon">:</span>
				<span class="minutes">00</span>
				<span class="colon">:</span>
				<span class="seconds">00</span>
			</div>`;

		var section = frm.toolbar.page.add_inner_message(timer);

		let currentIncrement = frm.doc.current_time || 0;
		if (frm.doc.started_time || frm.doc.current_time) {
			if (frm.doc.status == "On Hold") {
				updateStopwatch(currentIncrement);
			} else {
				currentIncrement += moment(frappe.datetime.now_datetime()).diff(moment(frm.doc.started_time),"seconds");
				initialiseTimer();
			}

			function initialiseTimer() {
				const interval = setInterval(function() {
					var current = setCurrentIncrement();
					updateStopwatch(current);
				}, 1000);
			}

			function updateStopwatch(increment) {
				var hours = Math.floor(increment / 3600);
				var minutes = Math.floor((increment - (hours * 3600)) / 60);
				var seconds = increment - (hours * 3600) - (minutes * 60);

				$(section).find(".hours").text(hours < 10 ? ("0" + hours.toString()) : hours.toString());
				$(section).find(".minutes").text(minutes < 10 ? ("0" + minutes.toString()) : minutes.toString());
				$(section).find(".seconds").text(seconds < 10 ? ("0" + seconds.toString()) : seconds.toString());
			}

			function setCurrentIncrement() {
				currentIncrement += 1;
				return currentIncrement;
			}
		}
	},

	hide_timer: function(frm) {
		frm.toolbar.page.inner_toolbar.find(".stopwatch").remove();
	},

	for_quantity: function(frm) {
		frm.doc.items = [];
		frm.call({
			method: "get_required_items",
			doc: frm.doc,
			callback: function() {
				refresh_field("items");
			}
		})
	},

	make_material_request: function(frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.manufacturing.doctype.job_card.job_card.make_material_request",
			frm: frm,
			run_link_triggers: true
		});
	},

	make_stock_entry: function(frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.manufacturing.doctype.job_card.job_card.make_stock_entry",
			frm: frm,
			run_link_triggers: true
		});
	},

	timer: function(frm) {
		return `<button> Start </button>`
	},

	set_total_completed_qty: function(frm) {
		frm.doc.total_completed_qty = 0;
		frm.doc.time_logs.forEach(d => {
			if (d.completed_qty) {
				frm.doc.total_completed_qty += d.completed_qty;
			}
		});

		refresh_field("total_completed_qty");
	}
});

frappe.ui.form.on('Job Card Time Log', {
	completed_qty: function(frm) {
		frm.events.set_total_completed_qty(frm);
	},

	to_time: function(frm) {
		frm.set_value('started_time', '');
	}
})

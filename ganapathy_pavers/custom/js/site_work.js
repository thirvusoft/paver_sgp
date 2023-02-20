function setquery(frm,cdt,cdn){
	frm.set_query("item", "item_details", function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
	return {
		filters: {
			'item_group': cur_frm.doc.project_type,
			'has_variants': 0
		}
	}
});
	frm.set_query("item", "item_details_compound_wall", function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
	return {
		filters: {
			'item_group': cur_frm.doc.project_type,
			'has_variants': 0
		}
	}
});
}
var validate=true
frappe.ui.form.on("Project",{
	after_save: function(frm){
		validate=true;
	},
	validate: function(frm){
		if (validate && frm.doc.status=="Completed" && frm.doc.previous_state!="Completed")
		{frappe.validated=false;
		frappe.confirm('Are you sure you want to complete this site?',
    	function(){
			validate=false;
			frappe.validated=true;
			cur_frm.save();
			window.close();
			cur_frm.refresh()
		}
    )}
	},
    project_type:function(frm,cdt,cdn){
        setquery(frm,cdt,cdn)
    }, 
    refresh: async function(frm,cdt,cdn){
		if (frm.doc.status == "Completed") {
			frm.add_custom_button("Update Site Completion Date",  function() {
				let d = new frappe.ui.Dialog({
					title: "Update Site Completion Date",
					fields: [
						{
							fieldname: "date",
							label: "Site Completion Date",
							fieldtype: "Date",
							reqd: 1
						}
					],
					primary_action: async function(data) {
						await frappe.call({
							method: "ganapathy_pavers.custom.py.site_work.update_completion_date",
							args: {
								date: data.date,
								name: frm.doc.name
							},
							callback: function (r) {
								frm.reload_doc()
								d.hide()
							},
						})
					}
				});
				d.show();
			});
		}
		await frm.add_custom_button("Update Delivery Details", function() {
			if (!frm.is_dirty()) {
				frappe.call({
					method: "ganapathy_pavers.custom.py.site_work.update_delivered_qty",
					args: {
						site_work: [frm.doc.name]
					},
					freeze: true,
					freeze_message: "Updating",
					callback(r) {
						frm.reload_doc()
					}
				});
			} else {
				frappe.show_alert({message: "Please Save this Form", indicator: "red"})
			}
		})
        if(!cur_frm.is_new()){
            cur_frm.set_df_property('is_multi_customer', 'read_only', 1)
            cur_frm.set_df_property('customer_name', 'read_only', 1)
            cur_frm.set_df_property('customer', 'read_only', 1)
        }
		cur_frm.remove_custom_button('Duplicate Project with Tasks')
		cur_frm.remove_custom_button('Kanban Board')
		cur_frm.remove_custom_button('Gantt Chart')
        setquery(frm,cdt,cdn)

		let sw_items=[];
		for(let item=0;item<(frm.doc.item_details?frm.doc.item_details.length:0);item++){
			if(!(sw_items.includes(frm.doc.item_details[item].item))){
				sw_items.push(frm.doc.item_details[item].item)
			}
		}
		for(let item=0;item<(frm.doc.item_details_compound_wall?frm.doc.item_details_compound_wall.length:0);item++){
			if(!(sw_items.includes(frm.doc.item_details_compound_wall[item].item))){
				sw_items.push(frm.doc.item_details_compound_wall[item].item)
			}
		}
		frm.set_query('item','job_worker', function(frm){
			return {
				filters:[
					['item_code' ,'in', sw_items]
				]
			}
		})

        frm.set_query('name1','job_worker',function(frm){
            return{
                filters:
					{
						'designation': 'Job Worker'
					}
			}
        })
        frm.set_query('supervisor', function(frm){
            return {
                filters:{
                    'designation': 'Supervisor'
                }
            }
        });
        frm.set_query("advance_account", 'additional_cost', function(frm, cdt, cdn) {
            let data=locals[cdt][cdn]
			if (!data.job_worker) {
				frappe.msgprint(__("Please select employee first"));
			}
			let company_currency = erpnext.get_currency(cur_frm.doc.company);
			let currencies = [company_currency];
			if (data.currency && (data.currency != company_currency)) {
				currencies.push(data.currency);
			}
			return {
				filters: {
					"root_type": "Asset",
					"is_group": 0,
					"company": cur_frm.doc.company,
					"account_currency": ["in", currencies],
				}
			};
		});
		customer_query()
    },
    is_multi_customer:function(frm){
        customer_query()
        if(cur_frm.doc.is_multi_customer){
            cur_frm.set_df_property('customer','reqd',0)
            cur_frm.set_df_property('customer','hidden',1)
            cur_frm.set_df_property('customer_name','hidden',0)
        }
        else{
            cur_frm.set_df_property('customer','reqd',1)
            cur_frm.set_df_property('customer','hidden',0)
            cur_frm.set_df_property('customer_name','hidden',1)
        }	
    },
    customer: function(frm){
        customer_query()
    },
    onload:function(frm){
		let  additional_cost=cur_frm.doc.additional_cost?cur_frm.doc.additional_cost:[]
		if(additional_cost.length==0 && cur_frm.is_new()){
		
			let add_on_cost=["Any Food Exp in Site","Other Labour Work","Site Advance"]
				for(let row=0;row<add_on_cost.length;row++){
				
				var new_row = frm.add_child("additional_cost");
				new_row.description=add_on_cost[row]
				}
					refresh_field("additional_cost");
			}
		cur_frm.set_query('job_worker', 'additional_cost', function(){
			return {
				filters: {
					designation: 'Job Worker'
				}
			}
		})
		customer_query()
	}
})

function percent_complete(frm,cdt,cdn){ 
	let total_area=0;
	let total_bundle = 0;
	let paver= cur_frm.doc.item_details?cur_frm.doc.item_details:[]
	let cw= cur_frm.doc.item_details_compound_wall?cur_frm.doc.item_details_compound_wall:[]
	for(let row=0;row<paver.length;row++){
		total_area+= cur_frm.doc.item_details[row].required_area?cur_frm.doc.item_details[row].required_area:0
		total_bundle += cur_frm.doc.item_details[row].number_of_bundle?cur_frm.doc.item_details[row].number_of_bundle:0
	        }
	for(let row=0;row<cw.length;row++){
		total_area+= cur_frm.doc.item_details_compound_wall[row].allocated_ft?cur_frm.doc.item_details_compound_wall[row].allocated_ft:0
			}
	let completed_area=0;
	let total_comp_bundle = 0;
	let work= cur_frm.doc.job_worker?cur_frm.doc.job_worker:[]
	for(let row=0;row<work.length;row++){
		if(!row.other_work){
			completed_area+= cur_frm.doc.job_worker[row].sqft_allocated?cur_frm.doc.job_worker[row].sqft_allocated:0
			total_comp_bundle += cur_frm.doc.job_worker[row].completed_bundle?cur_frm.doc.job_worker[row].completed_bundle:0
		}
	
	}
	let percent=(completed_area/total_area)*100
	frm.set_value('total_required_area',total_area)
	frm.set_value('total_completed_area',completed_area)
	frm.set_value('total_required_bundle',total_bundle)
	frm.set_value('total_completed_bundle',total_comp_bundle)
	frm.set_value('completed',percent)
}



function completed_bundle_calc(frm,cdt,cdn){
	let data = locals[cdt][cdn]
	let Bdl = data.completed_bundle
	var item_bundle_per_sqft
	let allocated_sqft
	var item = data.item
	if(Bdl && item && data.item_group == "Pavers"){
		frappe.db.get_doc('Item',item).then(value => {
			item_bundle_per_sqft = 0
			for(let i=0; i<value.uoms.length; i++){
				if(value.uoms[i].uom=='Bdl'){
					item_bundle_per_sqft=value.uoms[i].conversion_factor
				}
			}
			if(!item_bundle_per_sqft){
				frappe.throw({'message': 'Please enter Bdl conversion for an item: '+item})
			}
			allocated_sqft = Bdl * item_bundle_per_sqft
			frappe.model.set_value(cdt,cdn,"sqft_allocated",allocated_sqft?allocated_sqft:0)
		})
	} else if (frm.doc.type == "Compound Wall") {
		frappe.model.set_value(cdt,cdn,"sqft_allocated",(data.compound_wall_height || 0) * (data.running_sqft || 0))
	}
}



frappe.ui.form.on('TS Job Worker Details',{
	rate: function(frm, cdt, cdn){
		let data=locals[cdt][cdn]
		if(data.amount_calc_by_person) {
			return
		}
		amount(frm, cdt, cdn)
	},
	completed_bundle: function(frm,cdt,cdn){
		completed_bundle_calc(frm,cdt,cdn)
	},
	item:function(frm,cdt,cdn){
		completed_bundle_calc(frm,cdt,cdn)
	},
	running_sqft: function(frm,cdt,cdn){
		completed_bundle_calc(frm,cdt,cdn)
	},
	compound_wall_height:function(frm,cdt,cdn){
		completed_bundle_calc(frm,cdt,cdn)
	},
	sqft_allocated: function(frm, cdt, cdn){
		let data=locals[cdt][cdn]
		percent_complete(frm, cdt, cdn)
		if(data.amount_calc_by_person) {
			return
		}
		amount(frm, cdt, cdn)
	},
	job_worker_add: function(frm, cdt, cdn){
		let work= cur_frm.doc.job_worker?cur_frm.doc.job_worker:[]
		var name
		var start_date
		var date
		for(let row=0;row<work.length;row++){
			if(row){
				name = cur_frm.doc.job_worker[row-1].name1
				start_date = cur_frm.doc.job_worker[row-1].end_date?cur_frm.doc.job_worker[row-1].end_date:cur_frm.doc.job_worker[row-1].start_date
				date = frappe.datetime.add_days(start_date,1)
			}
			else{
				date = start_date
			}
		}
		frappe.model.set_value(cdt,cdn,"name1",name)
		frappe.model.set_value(cdt,cdn,"start_date",date)
		frappe.model.set_value(cdt,cdn,"end_date",date)
	},
	no_of_person: function(frm, cdt, cdn) {
		let data=locals[cdt][cdn]
		if(data.amount_calc_by_person) {
			frappe.model.set_value(cdt, cdn, "amount", (data.no_of_person || 0)*(data.rate_person || 0))
		}
	},
	rate_person:  function(frm, cdt, cdn) {
		let data=locals[cdt][cdn]
		if(data.amount_calc_by_person) {
			frappe.model.set_value(cdt, cdn, "amount", (data.no_of_person || 0)*(data.rate_person || 0))
		}
	},
	amount_calc_by_person: function(frm, cdt, cdn) {
		let data=locals[cdt][cdn]
		if(data.amount_calc_by_person) {
			frappe.model.set_value(cdt, cdn, "amount", (data.no_of_person || 0)*(data.rate_person || 0))
			return
		}
		amount(frm, cdt, cdn)
	}
})


function amount(frm,cdt,cdn){
	let row=locals[cdt][cdn]
	if(row.rate && row.sqft_allocated){
		frappe.model.set_value(cdt, cdn, 'amount', row.rate*row.sqft_allocated)
	}
	else{
		frappe.model.set_value(cdt, cdn, 'amount', 0)
	}
}



frappe.ui.form.on('Raw Materials',{
    item: function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if(row.item){
            frappe.db.get_doc('Item',row.item).then((item)=>{
                frappe.call({
                    method: "ganapathy_pavers.custom.py.sales_order.get_item_rate",
                    args:{
                        item: row.item
                    },
                    callback: async function(r){
                       await frappe.model.set_value(cdt,cdn,'rate', r.message?r.message:0);
                    }
                })
                frappe.model.set_value(cdt,cdn,'uom', item.stock_uom);
            })
        }
    },
    rate: function(frm,cdt,cdn){
        amount_rawmet(frm,cdt,cdn)
    },
    qty: function(frm,cdt,cdn){
        amount_rawmet(frm,cdt,cdn)
    }
})


function amount_rawmet(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    frappe.model.set_value(cdt,cdn,'amount', (row.rate?row.rate:0)*(row.qty?row.qty:0))
}



function customer_query(){
	let frm=cur_frm;
	let customer_list = []
	if(cur_frm.doc.is_multi_customer){
		for(let row=0; row<(frm.doc.customer_name?frm.doc.customer_name.length:0); row++){
			let cus=frm.doc.customer_name[row].customer
			frappe.db.get_value('Customer', cus, 'customer_name').then(cus_name => {
				if(!(customer_list.includes(cus_name.message.customer_name))){
					customer_list.push(cus_name.message.customer_name)
				}
			})
		}
	}else{
		customer_list.push(cur_frm.doc.customer?cur_frm.doc.customer:'')
	}
	cur_frm.set_query('customer', 'additional_cost', function(){
		return {
			filters: {
				customer_name: ['in', customer_list]
			}
		}
	})
	if(cur_frm.fields_dict.additional_cost.grid.open_grid_row){
		cur_frm.fields_dict.additional_cost.grid.refresh()
	}
}


frappe.ui.form.on('Additional Costs', {
	customer: function(frm, cdt, cdn){
		frm=cur_frm;
		let customer_list = []
		if(cur_frm.doc.is_multi_customer){
			for(let row=0; row<(frm.doc.customer_name?frm.doc.customer_name.length:0); row++){
				let cus=frm.doc.customer_name[row].customer
				frappe.db.get_value('Customer', cus, 'customer_name').then(cus_name => {
					if(!(customer_list.includes(cus_name.message.customer_name))){
						customer_list.push(cus_name.message.customer_name)
					}
				})
			}
		}else{
			customer_list.push(cur_frm.doc.customer?cur_frm.doc.customer:'')
		}
		cur_frm.set_query('customer', 'additional_cost', function(){
			return {
				filters: {
					customer_name: ['in', customer_list]
				}
			}
		})
		if(cur_frm.fields_dict.additional_cost.grid.open_grid_row){
			cur_frm.fields_dict.additional_cost.grid.refresh()
		}	
	},
	job_worker: function(frm, cdt, cdn){
		let data=locals[cdt][cdn]
		if(data.job_worker){
			frappe.call({
				method: "erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment.get_employee_currency",
				args: {
					employee: data.job_worker,
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'currency', r.message);
						frm.refresh_fields();
					}
				}
			});
		}
	},
	currency: function(frm, cdt, cdn) {
		let data=locals[cdt][cdn]
		if (data.currency) {
			var from_currency = data.currency;
			var company_currency;
			if (!cur_frm.doc.company) {
				company_currency = erpnext.get_currency(frappe.defaults.get_default("Company"));
			} else {
				company_currency = erpnext.get_currency(cur_frm.doc.company);
			}
			if (from_currency != company_currency) {
				set_exchange_rate(cdt, cdn, from_currency, company_currency);
			} else {
				frappe.model.set_value(cdt, cdn, "exchange_rate", 1.0);
			}
			cur_frm.refresh_fields();
		}
	}	
})
function set_exchange_rate(cdt, cdn, from_currency, company_currency) {
	frappe.call({
		method: "erpnext.setup.utils.get_exchange_rate",
		args: {
			from_currency: from_currency,
			to_currency: company_currency,
		},
		callback: function(r) {
			frappe.model.set_value(cdt, cdn, "exchange_rate", flt(r.message));
		}
	});
}

frappe.ui.form.on('TS Customer', {
	customer: function(frm, cdt, cdn){
		customer_query()
	}
})

from . import __version__ as app_version
import frappe

app_name = "ganapathy_pavers"
app_title = "Ganapathy Pavers"
app_publisher = "Thirvusoft"
app_description = "Ganapathy Pavers"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "careers@thirvusoft.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/css/ganapathy_pavers.min.css"
app_include_js = "/assets/js/ganapathy_pavers.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/ganapathy_pavers/css/ganapathy_pavers.css"
# web_include_js = "/assets/ganapathy_pavers/js/ganapathy_pavers.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ganapathy_pavers/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_list_js = {
	"Project" : "/custom/js/sw_quick_entry.js",
	"Item Price": "/custom/js/item_price_list.js",
	}

# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------


# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

before_install = "ganapathy_pavers.custom.py.warehouse.create_scrap_warehouse"
after_install = ["ganapathy_pavers.custom.py.item_group.item_group",
				 "ganapathy_pavers.custom.py.defaults.create_designation",
				 "ganapathy_pavers.custom.py.defaults.create_asset_category",
				 "ganapathy_pavers.custom.py.defaults.create_role",
				 "ganapathy_pavers.utils.py.vehicle.batch_customization",
				 "ganapathy_pavers.utils.py.vehicle_log.batch_customization",
				 "ganapathy_pavers.utils.py.assets.item_customization",
				 "ganapathy_pavers.utils.py.gl_entry.gl_entry_customization",
				 "ganapathy_pavers.utils.py.workstation.workstation_item_customization",
				 "ganapathy_pavers.utils.py.purchase_order.batch_customization",
				#  "ganapathy_pavers.utils.py.customer.create_multi_customer",
				 "ganapathy_pavers.utils.py.item.batch_customization",
				 "ganapathy_pavers.patches.location.execute",
				 "ganapathy_pavers.utils.py.quotation.batch_property_setter",
				 "ganapathy_pavers.utils.py.purchase_invoice.batch_property_setter",
				 "ganapathy_pavers.utils.py.payment_entry.payment_entry_property_setter",
                 "ganapathy_pavers.utils.py.stock_entry.stock_entry_custom_field",
		 		 "ganapathy_pavers.custom.py.defaults.selling_settings"
				 ]
				

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ganapathy_pavers.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	# "ToDo": "custom_app.overrides.CustomToDo"
	"Salary Slip":"ganapathy_pavers.utils.py.salary_slip.CustomSalary",
	"Payroll Entry":"ganapathy_pavers.utils.py.payroll_entry.MessExpense",
	"Opening Invoice Creation Tool":"ganapathy_pavers.custom.py.opening_invoice.OpeningInvoice",
	"Stock Entry" : "ganapathy_pavers.custom.py.stock_entry.Tsstockentry",
	"Vehicle Log" : "ganapathy_pavers.custom.py.vehicle_overwrite.odometer",
	"Journal Entry": "ganapathy_pavers.custom.py.journal_entry_override._JournalEntry",
	"Purchase Invoice": "ganapathy_pavers.custom.py.purchase_invoice_expense._PurchaseInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

jenv = {
	"methods": [
		"get_delivery_transport_detail:ganapathy_pavers.utils.py.sitework_printformat.get_delivery_transport_detail",
		"get_bank_details:ganapathy_pavers.get_bank_details",
		"uom_conversion:ganapathy_pavers.uom_conversion",
		"print_item_name:ganapathy_pavers.utils.py.sales_invoice_printformat.sales_invoice_print_format",
		"item_list:ganapathy_pavers.utils.py.sitework_printformat.site_work",
		"site_completion_delivery_uom:ganapathy_pavers.utils.py.sitework_printformat.site_completion_delivery_uom",
		"color_table1:ganapathy_pavers.utils.py.daily_maintenance.colour_details",
		"color_table2:ganapathy_pavers.utils.py.daily_maintenance.colour_details_sb",
		"bundle_sum:ganapathy_pavers.utils.py.thirvu_deliveryslip_printformat.print_format",
		"get_daily_maintenance_html:ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.daily_maintenance_print_format",
		"get_raw_materials_for_print:ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.get_raw_materials_for_print",
		"check_only_rm:ganapathy_pavers.utils.py.thirvu_deliveryslip_printformat.check_only_rm",
		"get_dsm_color:ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.get_dsm_color",
		"get_retail_cost:ganapathy_pavers.utils.py.sitework_printformat.get_retail_cost",
		"get_sbc_group_items:ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.sbc_print.get_sbc_group_items",
	]
}

doc_events = {
	"Event Sync Log": {
		"validate": [
			"ganapathy_pavers.utils.event_sync.event_sync.validate"
		]
	},
	"Item": {
		"validate": [
			"ganapathy_pavers.custom.py.item.validate_dsm_uom"
		],
		"before_validate": [
			"ganapathy_pavers.utils.event.validate_prime_item",
		]
	},
	"Stock Entry": {
		"on_submit": "ganapathy_pavers.custom.py.stock_entry.update_asset",
		"on_cancel": "ganapathy_pavers.custom.py.stock_entry.update_asset",
        "validate" : [
    			"ganapathy_pavers.custom.py.stock_entry.basic_rate_validation",
				"ganapathy_pavers.custom.py.stock_entry.expense_account",
			]
		
	},
	"Payment Entry":{
                      "on_submit":"ganapathy_pavers.utils.py.payment_entry.create_additional_salary"
          },
	"Salary Slip":{
        		"on_submit":[
					"ganapathy_pavers.utils.py.salary_slip.employee_advance",
					"ganapathy_pavers.utils.py.salary_slip.employee_update",
					"ganapathy_pavers.utils.py.salary_slip.additional_salary_update",
					],
				"on_cancel":[
					"ganapathy_pavers.utils.py.salary_slip.employee_update",
					"ganapathy_pavers.utils.py.salary_slip.additional_salary_update",
					],
				'validate':"ganapathy_pavers.utils.py.salary_slip.validate_salaryslip"
	},
	"Driver":{
		"validate":"ganapathy_pavers.custom.py.driver.validate_phone"
	},
	"Item Attribute":{
		"validate":"ganapathy_pavers.custom.py.item_varient.colour_creation"
	},

	"Employee Advance":{
		"on_submit":"ganapathy_pavers.utils.py.employee_advance.create_payment_entry",
		"on_cancel": [
			"ganapathy_pavers.custom.py.site_work.reduce_advance_amount",
			"ganapathy_pavers.ganapathy_pavers.doctype.employee_advance_tool.employee_advance_tool.cancel_employee_advance"
		]
	},
	"Project":{
		"autoname":"ganapathy_pavers.custom.py.site_work.autoname",
		"before_save":"ganapathy_pavers.custom.py.site_work.before_save",
		"validate":[
			"ganapathy_pavers.custom.py.site_work.refill_delivery_detail",
			"ganapathy_pavers.custom.py.site_work.validate",
			"ganapathy_pavers.custom.py.site_work.validate_status",
			"ganapathy_pavers.custom.py.site_work.rework_count",
			"ganapathy_pavers.custom.py.site_work.update_delivery_detail",
			"ganapathy_pavers.custom.py.site_work.job_worker",
			"ganapathy_pavers.custom.py.site_work.completed_and_required_area",
			"ganapathy_pavers.custom.py.site_work.job_worker_laying_details",
		],
		"after_insert":"ganapathy_pavers.custom.py.site_work.validate",
		"on_update":[
            	"ganapathy_pavers.custom.py.site_work.update_status",
				"ganapathy_pavers.custom.py.site_work.update_delivered_qty"
				]
	},
	"Sales Order":{
		"on_cancel":"ganapathy_pavers.custom.py.sales_order.remove_project_fields",
		"validate":[
			"ganapathy_pavers.custom.py.sales_order.item_table_pa_cw",
			"ganapathy_pavers.custom.py.tax_validation.tax_validation"
			],
		"on_update_after_submit": ["ganapathy_pavers.custom.py.sales_order.item_table_pa_cw",
									"ganapathy_pavers.custom.py.sales_order.update_site"]
	},
	"Job Card":{
		"on_submit":"afterganapathy_pavers.ganapathy_pavers.utils.py.jobcard.workstation"
	},
	"Delivery Note":{
		"before_validate":"ganapathy_pavers.custom.py.delivery_note.update_customer",
		"on_submit":[
					"ganapathy_pavers.custom.py.delivery_note.update_qty_sitework",
					"ganapathy_pavers.custom.py.delivery_note.update_return_qty_sitework",
					],
		# "on_cancel":[
		# 			"ganapathy_pavers.custom.py.delivery_note.reduce_qty_sitework",
		# 			"ganapathy_pavers.custom.py.delivery_note.reduce_return_qty_sitework"
		# 			 ],
		"validate":[
			"ganapathy_pavers.custom.py.delivery_note.validate",
			"ganapathy_pavers.custom.py.tax_validation.dn_tax_validation",
			"ganapathy_pavers.custom.py.delivery_note.sales_order_required"
			],
		# "before_submit":"ganapathy_pavers.custom.py.vehicle_log.vehicle_log_creation",
		# "on_update_after_submit": [
		# 	"ganapathy_pavers.custom.py.vehicle_log.update_vehicle_log"
		# ]
	},
	"Purchase Order":{
		"before_submit":"ganapathy_pavers.custom.py.purchase_order.getdate",
		"before_cancel": "ganapathy_pavers.custom.py.purchase_order.update_drop_ship_items_in_sw",
	},
	"Vehicle Log":{
		"on_update_after_submit": "ganapathy_pavers.custom.py.vehicle_log.onsubmit",
		"on_submit": [
						"ganapathy_pavers.custom.py.site_transport_cost.update_transport_cost_of_all_sites",
						"ganapathy_pavers.custom.py.vehicle_log.onsubmit",
						"ganapathy_pavers.custom.py.vehicle_log.onsubmit_hours",
						"ganapathy_pavers.custom.py.vehicle_log.update_transport_cost",
						"ganapathy_pavers.custom.py.vehicle_log.vehicle_log_draft",
						"ganapathy_pavers.custom.py.vehicle_log.supplier_journal_entry",
						"ganapathy_pavers.custom.py.vehicle_log.vehicle_log_mileage",
						"ganapathy_pavers.custom.py.vehicle_log.service_expenses",
						"ganapathy_pavers.custom.py.vehicle_log.fuel_stock_entry",
						"ganapathy_pavers.custom.py.vehicle_log.adblue_stock_entry",
						"ganapathy_pavers.custom.py.vehicle_log.fastag_expense",
						"ganapathy_pavers.custom.py.vehicle_log.update_fasttag_exp_to_sw",
						"ganapathy_pavers.custom.py.vehicle_log.update_delivery_note_created",
					  ],
		"on_cancel":[
						"ganapathy_pavers.custom.py.site_transport_cost.update_transport_cost_of_all_sites",
						"ganapathy_pavers.custom.py.vehicle_log.onsubmit",
						"ganapathy_pavers.custom.py.vehicle_log.update_fasttag_exp_to_sw",
						"ganapathy_pavers.custom.py.vehicle_log.update_transport_cost",
						"ganapathy_pavers.custom.py.vehicle_log.update_delivery_note_created",
					],
		"validate": ["ganapathy_pavers.custom.py.vehicle_log.validate",
					"ganapathy_pavers.custom.py.vehicle_log.validate_distance",
					"ganapathy_pavers.custom.py.vehicle_log.total_cost"
					],
		"on_update": [
			"ganapathy_pavers.custom.py.vehicle_log.update_delivery_note"
		]
	},
	"Sales Invoice":{
    	"before_validate":"ganapathy_pavers.custom.py.sales_invoice.update_customer",
		"validate":[
			"ganapathy_pavers.custom.py.sales_invoice.einvoice_validation",
			"ganapathy_pavers.custom.py.tax_validation.tax_validation"
			],
    	"on_submit":[
					"ganapathy_pavers.custom.py.delivery_note.update_qty_sitework",
					"ganapathy_pavers.custom.py.delivery_note.update_return_qty_sitework",
					],
		"on_cancel":[
					"ganapathy_pavers.custom.py.delivery_note.reduce_qty_sitework",
					"ganapathy_pavers.custom.py.delivery_note.reduce_return_qty_sitework"
					],
		
  	},
	"Vehicle":{
        "validate":[
					],
		"on_update": [
					"ganapathy_pavers.ganapathy_pavers.doctype.maintenance_type.maintenance_type.update_select_purpose",
					],
    },
 	"Employee Checkin":{
        "on_trash":"ganapathy_pavers.custom.py.employee_atten_tool.fill_emp_cancel_detail",
	},
	"Workstation":{
		"validate": "ganapathy_pavers.custom.py.workstation.total_no_salary",
		"on_update": "ganapathy_pavers.custom.py.workstation.make_custom_field",
		"after_rename": "ganapathy_pavers.custom.py.workstation.rename_custom_field",
		"on_trash": "ganapathy_pavers.custom.py.workstation.remove_custom_field",
	},
	"Purchase Receipt":{
		"validate":"ganapathy_pavers.custom.py.purchase_receipt.purchase_receipt_rawmaterial"
	},
	"Purchase Invoice":{
		"validate": [
			"ganapathy_pavers.custom.py.purchase_invoice.update_pi_items",
		],
		"on_submit":[
    		"ganapathy_pavers.custom.py.purchase_invoice_dashboard.tags_msg",
		    "ganapathy_pavers.custom.py.purchase_invoice.site_work_details_from_pi",
			"ganapathy_pavers.custom.py.purchase_invoice.create_service_vehicle_log",
		],
		"on_cancel": [
			"ganapathy_pavers.custom.py.purchase_invoice.site_work_details_from_pi",
		]
	},
	"Journal Entry": {
		"validate":"ganapathy_pavers.custom.py.journal_entry.journal_entry",
		"on_submit": [
			"ganapathy_pavers.custom.py.journal_entry.site_work_additional_cost"
		],
		"on_cancel": [
			"ganapathy_pavers.custom.py.journal_entry.site_work_additional_cost"
		],
	},
	"Attendance": {
		"on_trash":"ganapathy_pavers.custom.py.employee_checkin.unlink_logs",

		"on_submit": [
					"ganapathy_pavers.custom.py.attendance.attendance_submit",
				],
		"before_cancel":"ganapathy_pavers.custom.py.employee_atten_tool.fill_attn_cancel_detail"
	},
	"TS Employee Attendance Tool": {
		"validate": [
					# "ganapathy_pavers.custom.py.employee_atten_tool.day_wise_department",
					# "ganapathy_pavers.custom.py.employee_atten_tool.validate_same_dates"
					],
		"on_update": "ganapathy_pavers.custom.py.employee_atten_tool.create_and_delete_checkins",
		"on_cancel":"ganapathy_pavers.custom.py.employee_atten_tool.doc_cancel",
	},
	"Batch": {
		"autoname": "ganapathy_pavers.custom.py.batch.autoname",
		"on_trash": "ganapathy_pavers.custom.py.batch.update_series"
	},
	"Quotation": {
		"on_update": "ganapathy_pavers.custom.py.quotation.update_lead_on_save"
	}
}
after_migrate=["ganapathy_pavers.custom.py.site_work.create_status",
              "ganapathy_pavers.custom.py.lead.new_status",
              "ganapathy_pavers.custom.py.property_setter.property_setter",
			  "ganapathy_pavers.utils.py.vehicle.batch_customization",
			  "ganapathy_pavers.utils.py.vehicle_log.batch_customization",
			  "ganapathy_pavers.utils.py.quotation.batch_property_setter",
			  "ganapathy_pavers.utils.py.purchase_invoice.batch_property_setter",
			  "ganapathy_pavers.utils.py.payment_entry.payment_entry_property_setter",
			  "ganapathy_pavers.utils.py.salary_slip.remove_branch_read_only"
			  ]


doctype_js = {
                "TS Employee Attendance Tool":"custom/py/ts_employee_atten_tool.js",
				"Asset": "/custom/js/asset.js",
				"Item" : "/custom/js/item.js",
				"Payment Entry" : "/custom/js/payment_entry.js",
				"Project": "/custom/js/site_work.js",
				"Sales Order":"/custom/js/sales_order.js",
				"Purchase Invoice":"/custom/js/purchase_invoice.js",
				"Vehicle":"/custom/js/vehicle.js",
				"Timesheet" : "utils/js/timesheet.js",
				"Salary Slip":"utils/js/salary_slip.js",
				"Purchase Receipt":"/custom/js/purchase_receipt.js",
				"Workstation":["/custom/js/workstation.js","/custom/js/ts_operator.js"],
				"Employee Attendance Tool":"/custom/js/employee_atten_tool.js",
				"Employee":"/custom/js/employee.js",
				"Delivery Note":"/custom/js/delivery_note.js",
				"Sales Invoice": "/custom/js/sales_invoice.js",
				# "Journal Entry": "/custom/js/journal_entry.js",
				"Vehicle Log":[
								"/custom/js/vehicle_log.js", 
								"/custom/js/vehicle_log_service.js"
								],
				"Work Order" : "/utils/js/workorder.js",

	     		"BOM" : [ "/utils/js/bom.js", "/custom/js/bom.js"],
				"Quotation": "/custom/js/quotation.js",
				"Payroll Entry": "/utils/js/payroll_entry.js",
				"Employee Advance": "/utils/js/employee_advance.js",
			 }
# Scheduled Tasks
# ---------------

scheduler_events = {
    "all": [
		"ganapathy_pavers.custom.py.note.note_alert"
	],

	"cron": {
		"0 2 * * *": [
			"ganapathy_pavers.custom.py.vehicle_log.days",
			"ganapathy_pavers.custom.py.vehicle.vehicle_maintenance_notification",
		],
		"0 1 * * *": [
			# "ganapathy_pavers.custom.py.employee_checkin.mark_attendance",
			"ganapathy_pavers.custom.py.employee_checkin.scheduler_for_employee_shift"
		]
	},

	"daily":
		[
		"ganapathy_pavers.custom.py.purchase_order.purchasenotification",
		"ganapathy_pavers.custom.py.site_work.update_delivered_qty"
		],
	"daily_long": [
		"ganapathy_pavers.custom.py.bom.update_latest_price_in_all_boms"
		]

	
# 	"all": [
# 		"ganapathy_pavers.tasks.all"
# 	"daily": [
# 		"ganapathy_pavers.tasks.daily"
# 	],
# 	"hourly": [
# 		"ganapathy_pavers.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ganapathy_pavers.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ganapathy_pavers.tasks.monthly"
# 	]
}
cron_time=""
try:
	time = str(frappe.db.get_single_value('Thirvu HR Settings', 'checkin_type_resetting_time'))
	time = time.split(':')
	cron_time = f'{int(time[1])} {int(time[0])} * * *'
	scheduler_events['cron'][cron_time] = ['thirvu_hr.thirvu_hr.doctype.employee_checkin_without_log_type.employee_checkin_without_log_type.create_employee_checkin']
except:pass

# Testing
# -------

# before_tests = "ganapathy_pavers.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry": "ganapathy_pavers.custom.py.payment_entry.get_payment_entry",
	"erpnext.buying.doctype.purchase_order.purchase_order.update_status": "ganapathy_pavers.custom.py.purchase_order.update_status",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Vehicle Log": "ganapathy_pavers.custom.py.dashboards.vehicle_log.get_data",
	"Purchase Invoice": "ganapathy_pavers.custom.py.purchase_invoice_dashboard.get_data"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ganapathy_pavers.auth.validate"
# ]

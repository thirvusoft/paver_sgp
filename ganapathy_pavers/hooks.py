from . import __version__ as app_version

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
# app_include_css = "/assets/ganapathy_pavers/css/ganapathy_pavers.css"
# app_include_js = "/assets/ganapathy_pavers/js/ganapathy_pavers.js"

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

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
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

# before_install = "ganapathy_pavers.install.before_install"
# after_install = "ganapathy_pavers.install.after_install"

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
	"Opening Invoice Creation Tool":"ganapathy_pavers.custom.py.opening_invoice.OpeningInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

after_install="ganapathy_pavers.custom.py.defaults.create_designation"

doc_events = {
	"Payment Entry":{
                      "on_submit":"ganapathy_pavers.utils.py.payment_entry.create_additional_salary"
          },
	"Salary Slip":{
        		"on_submit":"ganapathy_pavers.utils.py.salary_slip.employee_update",
				"validate":"ganapathy_pavers.utils.py.salary_slip.round_off"
          },
	"Driver":{
		"validate":"ganapathy_pavers.custom.py.driver.validate_phone"
	},
	"Employee Advance":{
		"on_submit":"ganapathy_pavers.utils.py.employee_advance.create_payment_entry"
	},
	"Project":{
		"autoname":"ganapathy_pavers.custom.py.site_work.autoname",
		"before_save":"ganapathy_pavers.custom.py.site_work.before_save"
		
	},
	"Sales Order":{
		"on_cancel":"ganapathy_pavers.custom.py.sales_order.remove_project_fields"
	},
	"Delivery Note":{
		"validate":"ganapathy_pavers.custom.py.delivery_note.set_qty"
	},
	"Job Card":{
		"on_submit": "ganapathy_pavers.custom.py.job_card.create_timesheet"
	}
}
after_migrate=["ganapathy_pavers.custom.py.site_work.create_status"]
doctype_js = {
				"Item" : "/custom/js/item.js",
				"Payment Entry" : "/custom/js/payment_entry.js",
				"Project": "/custom/js/site_work.js",
				"Sales Order": [
								"/custom/js/site_work.js",
								"/custom/js/sales_order.js",
								],
				"Vehicle":"/custom/js/vehicle.js",
				"Timesheet" : "utils/js/timesheet.js",
				"Salary Slip":"utils/js/salary_slip.js",
				"Purchase Receipt":"/custom/js/purchase_receipt.js",
				"Workstation":"/custom/js/workstation.js",
				"Work Order": "/custom/js/work_order.js",
				"Delivery Note": "/custom/js/delivery_note.js",
				"Vehicle Log":"/custom/js/vehicle_log.js"
			 }
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ganapathy_pavers.tasks.all"
# 	],
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
# }

# Testing
# -------

# before_tests = "ganapathy_pavers.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ganapathy_pavers.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ganapathy_pavers.task.get_dashboard_data"
# }

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

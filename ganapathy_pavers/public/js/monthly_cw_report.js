frappe.provide("ganapathy_pavers")

ganapathy_pavers.monthly_compound_wall_report = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "width": "80",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "width": "80",
            "reqd": 1
        },
        {
            "fieldname": "expense_summary",
            "label": __("Expense Summary"),
            "fieldtype": "Check",
        },
        {
            "fieldname": "new_method",
            "label": __("New Expense Method"),
            "fieldtype": "Check",
            "default": 0,
        },
        {
            "fieldname": "vehicle_summary",
            "label": __("Vehicle Summary"),
            "fieldtype": "Check",
            "default": 0,
        }
    ],
	formatter: function (value, row, column, data, default_formatter) {
		if (column.fieldname == "qty" && data.reference_data) {
			value = __(default_formatter(value, row, column, data));
			value = $(`<span ondblclick=\'ganapathy_pavers.show_reference(\"${data.qty}\", ${JSON.stringify(data.reference_data)}, \"${data.uom}\")\'>${value}</span>`);
			var $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		} else {
			value = __(default_formatter(value, row, column, data));
		}
		return value
	}
};


ganapathy_pavers.itemwise_cw_filter = {
	"filters": [
	  {
		fieldname: "from_date",
		label: __("From Date"),
		fieldtype: "Date",
		width: "80",
		default: frappe.datetime.month_start(),
		reqd: 1,
	  },
	  {
		fieldname: "to_date",
		label: __("To Date"),
		fieldtype: "Date",
		default: frappe.datetime.month_end(),
		width: "80",
		reqd: 1,
	  },
	  {
		  fieldname: "report_type",
		  label: __("Report Type"),
		  fieldtype: "Select",
		  options: "Summary\nReport",
		  default: "Summary"
	  },
	  {
		  fieldname: "new_method",
		  label: __("New Expense Method"),
		  fieldtype: "Check",
		  default: 0,
	  },
	  {
		  fieldname: "vehicle_summary",
		  label: __("Vehicle Summary"),
		  fieldtype: "Check",
		  default: 0,
	  }
	],
  };
  
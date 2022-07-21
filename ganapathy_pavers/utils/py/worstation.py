import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def item_customization():
        custom_fields={
        "workstation":[
            dict(
            fieldname='assets_table_worksation',
            label='Assets',
            fieldtype='Table',
            options="Asset_table",
            insert_after='column_break_4'
            ),
            dict(
            fieldname='section_break1',
            fieldtype='Section Break',
            insert_after='assets_table_worksation'
            ),
            dict(
            fieldname='cost_per_hours',
            label='Cost Per Hour(s)',
            fieldtype='Int',
            insert_after='section_break1',
            ),
            dict(
            fieldname='section_break2',
            fieldtype='Section Break',
            insert_after='cost_per_hours'
            ),
            dict(
            fieldname='no_of_labours',
            label='No of Labour(s)',
            fieldtype='Int',
            insert_after='section_break2',
            ),
            dict(
            fieldname='no_of_operators',
            label='No of Operator(s)',
            fieldtype='Int',
            insert_after='no_of_labours',
            ),
            dict(
            fieldname='no_of_common_operators',
            label='No of Common Operator(s)',
            fieldtype='Int',
            insert_after='no_of_operators',
            ),
            dict(
            fieldname='division_factors',
            fieldtype='Column Break',
            insert_after='no_of_common_operators',
            ),
            dict(
            fieldname='division_factors1',
            label='Division Labour',
            fieldtype='Float',
            insert_after='division_factors',
            ),
            dict(
            fieldname='division_factors2',
            label='Division Operator', 
            fieldtype='Float',
            insert_after='division_factors1',
            ),
            dict(
            fieldname='division_factors3',
            label='Division Common Operator', 
            fieldtype='Float',
            insert_after='division_factors2',
            ),
            dict(
            fieldname='cal_wages',
            fieldtype='Column Break',
            insert_after='division_factors3',
            ),
            dict(
            fieldname='cal_wages1',
            label='Calculate Labour wages', 
            fieldtype='Float',
            insert_after='cal_wages',
            ),
            dict(
            fieldname='cal_wages2', 
            label='Calculate operator wages', 
            fieldtype='Float',
            insert_after='cal_wages1',
            ),
            dict(
            fieldname='cal_wages3',
            label='Calculate common operator wages', 
            fieldtype='Float',
            insert_after='cal_wages2',
            ),
            dict(
            fieldname='section_break3',
            fieldtype='Section Break',
            insert_after='cal_wages3',
            ),
            dict(
            fieldname='no_of_total_employees',
            label='No of Total Employee(s)',
            fieldtype='Int',
            insert_after='section_break3',
            ),
            dict(
            fieldname='sum_of_wages_per_hour_column_break',
            fieldtype='Column Break',
            insert_after='no_of_total_employees',
            ),
            dict(
            fieldname='sum_of_wages_per_hours',
            label='Sum of wages per hours',
            fieldtype='Float',
            insert_after='sum_of_wages_per_hour_column_break',
            ),
        ]
        }

        create_custom_fields(custom_fields)

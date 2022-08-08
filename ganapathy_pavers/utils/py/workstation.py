from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def workstation_item_customization():
        workstation_item_customization={
        "Workstation":[
            dict(
            fieldname='assets_table_worksation',
            label='Assets',
            fieldtype='Table',
            options='Asset_table',
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
            insert_after='section_break1'
            ),
            dict(
            fieldname='ts_columnbreak1',
            fieldtype='Column Break',
            insert_after='cost_per_hours'
            ),
            dict(
            fieldname='ts_machine_operator',
            label='Machine Operator',
            fieldtype='Link',
            options='Employee',
            insert_after='ts_columnbreak1'
            ),
            dict(
            fieldname='ts_columnbreak2',
            fieldtype='Column Break',
            insert_after='ts_machine_operator'
            ),
            dict(
            fieldname='ts_panmix_operator',
            label='Panmix Operator',
            fieldtype='Link',
            options='Employee',
            insert_after='ts_columnbreak2'
            ),
            dict(
            fieldname='section_break2',
            fieldtype='Section Break',
            insert_after='ts_panmix_operator'
            ),
            dict(
            fieldname='no_of_labours',
            label='No of Labour(s)',
            fieldtype='Int',
            insert_after='section_break2',
            default=0
            ),
            dict(
            fieldname='no_of_operators',
            label='No of Operator(s)',
            fieldtype='Int',
            insert_after='no_of_labours',
            default=0,
            hidden=1
            ),
            dict(
            fieldname='no_of_common_operators',
            label='No of Common Operator(s)',
            fieldtype='Int',
            insert_after='no_of_operators',
            default=0,
            hidden=1
            ),
            dict(
            fieldname='routine_operators',
            label='Routine Operator(s)',
            fieldtype='Int',
            insert_after='no_of_common_operators',
            default=0,
            hidden=1
            ),
            dict(
            fieldname='division_factors',
            fieldtype='Column Break',
            insert_after='routine_operators',
            hidden=1
            ),
            dict(
            fieldname='division_factors1',
            label='Division Labour',
            fieldtype="Float",
            insert_after='division_factors',
            default=1,
            precision=4
            ),
            dict(
            fieldname='division_factors2',
            label='Division Operator', 
            fieldtype='Float',
            insert_after='division_factors1',
            default=0,
            precision = 4,
            hidden=1
            ),
            dict(
            fieldname='division_factors3',
            label='Division Common Operator', 
            fieldtype='Float',
            insert_after='division_factors2',
            default=0,
            precision = 4,
            hidden=1
            ),
            dict(
            fieldname='division_factors4',
            label='Division Routine Operator', 
            fieldtype='Float',
            insert_after='division_factors3',
            default=4,
            precision = 4,
            hidden=1
            ),
            dict(
            fieldname='cal_wages',
            fieldtype='Column Break',
            insert_after='division_factors4',
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
            hidden=1
            ),
            dict(
            fieldname='cal_wages3',
            label='Calculate common operator wages', 
            fieldtype='Float',
            insert_after='cal_wages2',
            hidden=1
            ),
            dict(
            fieldname='cal_wages4',
            label='Calculate Routine operator wages', 
            fieldtype='Float',
            insert_after='cal_wages3',
            hidden=1
            ),
            dict(
            fieldname='ts_operators',
            label='Operators',
            fieldtype='Section Break',
            insert_after='cal_wages4',
            collapsible=1
            ),
            dict(
            fieldname='ts_operators_table',
            label='Operators',
            fieldtype='Table',
            insert_after='ts_operators',
            options='Ts Operators'
            ),
            dict(
            fieldname='ts_sectionbreak',
            fieldtype='Section Break',
            insert_after='ts_operators_table'
            ),
            dict(
            fieldname='ts_no_of_operator',
            label='No of Operators',
            fieldtype='Float',
            insert_after='ts_sectionbreak',
            ),
            dict(
            fieldname='ts_column_break',
            fieldtype='Column Break',
            insert_after='ts_no_of_operator'
            ),
            dict(
            fieldname='ts_sum_of_operator_wages',
            label='Sum of Operator Wages',
            fieldtype='Float',
            insert_after='ts_column_break',
            ),
            dict(
            fieldname='ts_sectionbreak3',
            fieldtype='Section Break',
            insert_after='ts_sum_of_operator_wages'
            ),
            dict(
            fieldname='no_of_total_employees',
            label='No of Total Employee(s)',
            fieldtype='Int',
            insert_after='ts_sectionbreak3',
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
        create_custom_fields(workstation_item_customization)

from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_cw_production_report.itemwise_monthly_cw_production_report import execute as compound_wall_report

def execute(filters=None):
	return compound_wall_report(filters, ["Lego Block"], prod_exp_sqft="lego", exp_group="lg_group")
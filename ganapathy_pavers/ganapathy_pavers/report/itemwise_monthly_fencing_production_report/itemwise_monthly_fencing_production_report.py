# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_cw_production_report.itemwise_monthly_cw_production_report import execute as compound_wall_report

def execute(filters=None):
	return compound_wall_report(filters, "Fencing Post")
	
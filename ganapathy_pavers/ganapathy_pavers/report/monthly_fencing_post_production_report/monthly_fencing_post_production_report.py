# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

from frappe import _
from ganapathy_pavers.ganapathy_pavers.report.monthly_compound_wall_production_report.monthly_compound_wall_production_report import execute as compound_wall_report

def execute(filters=None):
	return compound_wall_report(filters, ["Fencing Post"], "fencing_post")
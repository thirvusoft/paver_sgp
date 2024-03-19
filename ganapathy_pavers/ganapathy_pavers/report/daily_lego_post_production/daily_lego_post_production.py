# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
from ganapathy_pavers.ganapathy_pavers.report.daily_compound_wall_production_register.daily_compound_wall_production_register import execute as daily_cw_prod


def execute(filters=None):
	return daily_cw_prod(filters, 'Lego Block')
// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Maintenance', {
	get_attendance_details: function (frm) {
		if (cur_frm.doc.date) {
			frappe.call({
				method: "ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.get_attendance_details",
				args: {
					date: cur_frm.doc.date,
				},
				callback: function (res) {
					cur_frm.set_value('labour_present', res['message']['labour_present']);
					cur_frm.set_value('operator_present', res['message']['operator_present']);
					cur_frm.set_value('labour_absent',res['message']['labour_absent']);
					cur_frm.set_value('operator_absent', res['message']['operator_absent']);
				}
			});
		}
	},
	load_item_details: function (frm) {
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.paver_item",
			args: {
				warehouse: cur_frm.doc.warehouse || frappe.throw({ message: "Please enter <b>Warehouse for Pavers and Compound Walls</b>", title: "Missing Fields", indicator: "red" }),
				date: cur_frm.doc.date,
				warehouse_colour: cur_frm.doc.warehouse_colour || frappe.throw({ message: "Please enter <b>Warehouse for Colour Powder Items</b>", title: "Missing Fields", indicator: "red" })
			},
			freeze: true,
			freeze_message: loading_svg() || "Fetching data...",
			callback: function (r) {
				cur_frm.set_value('colour_details', r.message[0])
				cur_frm.set_value('red_total_n', r.message[1]['red'])
				cur_frm.set_value('black_total_n', r.message[1]['black'])
				cur_frm.set_value('grey_total_n', r.message[1]['grey'])
				cur_frm.set_value('brown_total_n', r.message[1]['brown'])
				cur_frm.set_value('yellow_total_n', r.message[1]['yellow'])
				cur_frm.set_value('colour_details_of_sb', r.message[2])
				cur_frm.set_value('red_total_s', r.message[3]['red'])
				cur_frm.set_value('black_total_s', r.message[3]['black'])
				cur_frm.set_value('grey_total_s', r.message[3]['grey'])
				cur_frm.set_value('brown_total_s', r.message[3]['brown'])
				cur_frm.set_value('yellow_total_s', r.message[3]['yellow'])
				cur_frm.set_value("vehicle_details", r.message[4])
				cur_frm.set_value("machine_details", r.message[5])
				cur_frm.set_value("compound_wall_stock", r.message[6])
				cur_frm.set_value("colour_powder", r.message[7])
				cur_frm.set_value("compound_wall_item_stock", r.message[8])
				cur_frm.set_value("size_details", r.message[9])
				cur_frm.set_value("raw_material_details", r.message[10])
			}
		})
	},
	load_current_stock: function (frm) {
		cur_frm.trigger("load_item_details")
	},
});

function loading_svg() {
	return `
<div class="svg-container">
<svg class="loading-svg" width="100" height="100" viewBox="0 0 300 300">
  <defs>
	<linearGradient id="gradient-fill" gradientUnits="userSpaceOnUse" x1="0" y1="300" x2="300" y2="0">
	  <stop offset="0%">
		<animate attributeName="stop-color" values="#00E06B;#CB0255;#00E06B" dur="5s" repeatCount="indefinite" />
	  </stop>
	  <stop offset="100%">
		<animate attributeName="stop-color" values="#04AFC8;#8904C5;#04AFC8" dur="8s" repeatCount="indefinite" />
	  </stop>
	</linearGradient>
	<clipPath id="clip">
	  <rect class="square s1" x="0" y="0" rx="12" ry="12" height="90" width="90"></rect>
	  <rect class="square s2" x="100" y="0" rx="12" ry="12" height="90" width="90"></rect>
	  <rect class="square s3" x="200" y="0" rx="12" ry="12" height="90" width="90"></rect>
	  <rect class="square s4" x="0" y="100" rx="12" ry="12" height="90" width="90"></rect>
	  <rect class="square s5" x="200" y="100" rx="12" ry="12" height="90" width="90"></rect>
	  <rect class="square s6" x="0" y="200" rx="12" ry="12" height="90" width="90"></rect>
	  <rect class="square s7" x="100" y="200" rx="12" ry="12" height="90" width="90"></rect>
	</clipPath>
  </defs>
  <rect class="gradient" clip-path="url('#clip')" height="300" width="300"></rect>
</svg>
<footer class="footer-data">
    Fetching data...
  </footer>
</div>
<style>
.loading-svg {
	transform: rotate(45deg);
  }
  
  .gradient {
	animation-iteration-count: infinite;
	animation-duration: 1s;
	fill: url('#gradient-fill');
  }
  .square {
	animation-iteration-count: infinite;
	animation-duration: 2s;
	transition-timing-function: ease-in-out;
  }
  
  .s1 {
	animation-name: slide-1;
  }
  
  .s2 {
	animation-name: slide-2;
  }
  
  .s3 {
	animation-name: slide-3;
  }
  
  .s4 {
	animation-name: slide-4;
  }
  
  .s5 {
	animation-name: slide-5;
  }
  
  .s6 {
	animation-name: slide-6;
  }
  
  .s7 {
	animation-name: slide-7;
  }
  
  @keyframes slide-1 {
	37.5% {
	  transform: translateX(0px);
	}
	50% {
	  transform: translateX(100px);
	}
	100% {
	  transform: translateX(100px);
	}
  }
  
  @keyframes slide-2 {
	25% {
	  transform: translateX(0px);
	}
	37.5% {
	  transform: translateX(100px);
	}
	100% {
	  transform: translateX(100px);
	}
  }
  
  @keyframes slide-3 {
	12.5% {
	  transform: translateY(0px);
	}
	25% {
	  transform: translateY(100px);
	}
	100% {
	  transform: translateY(100px);
	}
  }
  
  @keyframes slide-4 {
	50% {
	  transform: translateY(0px);
	}
	62.5% {
	  transform: translateY(-100px);
	}
	100% {
	  transform: translateY(-100px);
	}
  }
  
  @keyframes slide-5 {
	12.5% {
	  transform: translate(-100px, 0px);
	}
	87.5% {
	  transform: translate(-100px, 0px);
	}
	100% {
	  transform: translate(-100px, 100px);
	}
  }
  
  @keyframes slide-6 {
	62.5% {
	  transform: translateY(0px);
	}
	75% {
	  transform: translateY(-100px);
	}
	100% {
	  transform: translateY(-100px);
	}
  }
  
  @keyframes slide-7 {
	75%  {
	  transform: translateX(0px);
	}
	87.5% {
	  transform: translateX(-100px);
	}
	100% {
	  transform: translateX(-100px);
	}
  }
  
  .svg-container {
	text-align: center;
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
  }
  .footer-data {
	margin-top: 1em;
  }
  </style>
`

}
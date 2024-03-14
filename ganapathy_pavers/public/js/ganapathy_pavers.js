frappe.provide('ganapathy_pavers');

ganapathy_pavers.isVisible = (elem) => {
    if (!(elem instanceof Element)) throw Error('DomUtil: elem is not an element.');
    const style = getComputedStyle(elem);
    if (style.display === 'none') return false;
    if (style.visibility !== 'visible') return false;
    if (style.opacity < 0.1) return false;
    if (elem.offsetWidth + elem.offsetHeight + elem.getBoundingClientRect().height +
        elem.getBoundingClientRect().width === 0) {
        return false;
    }
    const elemCenter   = {
        x: elem.getBoundingClientRect().left + elem.offsetWidth / 2,
        y: elem.getBoundingClientRect().top + elem.offsetHeight / 2
    };
    if (elemCenter.x < 0) return false;
    if (elemCenter.x > (document.documentElement.clientWidth || window.innerWidth)) return false;
    if (elemCenter.y < 0) return false;
    if (elemCenter.y > (document.documentElement.clientHeight || window.innerHeight)) return false;
    let pointContainer = document.elementFromPoint(elemCenter.x, elemCenter.y);
    do {
        if (pointContainer === elem) return true;
    } while (pointContainer = pointContainer.parentNode);
    return false;
}

ganapathy_pavers.loading_svg = `
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

ganapathy_pavers.scroll_to_element = function(element) {
	let $el = $(element);

	// uncollapse section
	if (field.section.is_collapsed()) {
		field.section.collapse(false);
	}

	// scroll to input
	frappe.utils.scroll_to($el, true, 15);

	// highlight input
	$el.addClass('has-error');
	setTimeout(() => {
		$el.removeClass('has-error');
		$el.find('input, select, textarea').focus();
	}, 1000);
}

ganapathy_pavers.delivery_slip_scroll = function() {
	ganapathy_pavers.scroll_to_element(document.querySelector(`.dynamic-settings div[data-fieldtype="Check"][data-fieldname="print_as_bundle"]`))
}
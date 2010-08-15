function setActionForm() {
	action_id = $('#id_action').val();
	for(i in actions) {
		action = actions[i];
		if(action['pk'] == action_id) {
			kind = action['fields']['kind'];
			measurement = measurements[action['fields']['measurement']];
			if(measurement) {
				c = $('label[for=id_value]').children();
				$('label[for=id_value]').html(measurement[2]).append(c);
			}
			
			switch(kind) {
				case 'sc':
					$('#id_value').parent().parent().slideDown();
					break;
				default:
					$('#id_value').parent().parent().slideUp();
					break;
			}
			
			return;
		}
	}
	
	$('#id_value').parent().parent().hide();
}

function setComboDate(combo, date) {
	month = date.getMonth() + 1;
	day = date.getDate();
	year = date.getFullYear();
	
	combo.each(
		function(i) {
			switch(i) {
				case 0:
					$(this).val(month);
					break;
				case 1:
					$(this).val(day);
					break;
				case 2:
					$(this).val(year);
					break;
			}
		}
	);
}

$(document).ready(
	function(e) {
		$('.date-field.future-date').parent().each(
			function() {
				var container = $(this);
				var combo = container.find('.date-field.future-date');
				
				var tomorrow_link = $('<a href="javascript:;" style="margin-left: 0.5em;">Tomorrow</a>');
				tomorrow_link.bind('click',
					function(e) {
						e.preventDefault();
						date = new Date();
						date.setDate(date.getDate() + 1);
						
						setComboDate(combo, date);
					}
				);
				
				combo.last().after(tomorrow_link);
				
				var nextweek_link = $('<a href="javascript:;" style="margin-left: 0.5em;">Next week</a>');
				nextweek_link.bind('click',
					function(e) {
						e.preventDefault();
						date = new Date();
						date.setDate(date.getDate() + 7);
						
						setComboDate(combo, date);
					}
				);
				
				tomorrow_link.after(nextweek_link);
				
				var twoweeks_link = $('<a href="javascript:;" style="margin-left: 0.5em;">In 2 weeks</a>');
				twoweeks_link.bind('click',
					function(e) {
						e.preventDefault();
						date = new Date();
						date.setDate(date.getDate() + 14);
						
						setComboDate(combo, date);
					}
				);
				
				nextweek_link.after(twoweeks_link);
				
				var nextmonth_link = $('<a href="javascript:;" style="margin-left: 0.5em;">Next month</a>');
				nextmonth_link.bind('click',
					function(e) {
						e.preventDefault();
						date = new Date();
						date.setMonth(date.getMonth() + 1);
						
						setComboDate(combo, date);
					}
				);
				
				twoweeks_link.after(nextmonth_link);
			}
		);
		
		$('a[rel=external]').attr('target', '_blank');
	}
);
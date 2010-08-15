$(document).ready(
	function() {
		$('.edit-action').not('.last').each(
			function() {
				var panel = $(this);
				panel.find('.panel').hide();
				panel.find('h3 a').bind('click',
					function(e) {
						e.preventDefault();
						panel.find('.panel').slideToggle();
					}
				);
				
				val = panel.find('input[type=radio][checked=true]').val();
				multiplier = panel.find('select[name$=-measurement]');
				
				switch(val) {
					case 'sa':
						multiplier.parent().parent().hide();
						break;
					case 'sc':
						multiplier.parent().parent().show();
						break;
				}
			}
		);
		
		$('.edit-action').each(
			function() {
				var panel = $(this);
				panel.find('input[type=radio]').bind('click',
					function() {
						if($(this).attr('checked') == true) {
							val = $(this).val();
							multiplier = panel.find('select[name$=-measurement]');
							switch(val) {
								case 'sa':
									multiplier.parent().parent().slideUp();
									break;
								case 'sc':
									multiplier.parent().parent().slideDown();
									break;
							}
						}
					}
				);
			}
		);
		
		$('.edit-action').last().find('.panel select[name$=-measurement]').parent().parent().hide();
	}
);
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
				multiplier = panel.find('input[type=text][name$=-points_multiplier]');
				
				switch(val) {
					case 'pa': case 'pi':
						multiplier.parent().parent().hide();
						break;
					case 'ps': case 'ns':
						multiplier.parent().parent().hide();
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
							multiplier = panel.find('input[type=text][name$=-points_multiplier]');
							switch(val) {
								case 'pa': case 'pi':
									multiplier.parent().parent().slideUp();
									break;
								case 'ps': case 'ns':
									multiplier.parent().parent().slideDown();
									break;
							}
						}
					}
				);
			}
		);
	}
);
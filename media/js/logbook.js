$(document).ready(
	function() {
		$('#log-form .log-options li a').bind('click',
			function(e) {
				$('#log-form .log-options li a.selected').removeClass('selected');
				$(this).addClass('selected');

				href = $(this).attr('href').substr(1);
				$('.log-form').hide();
				$('.log-form#' + href).show();

				e.preventDefault();
			}
		);

		$('#id_action').bind('change',
			function(e) {
				setActionForm();
			}
		);

		setActionForm();
	}
);
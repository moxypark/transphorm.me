$(document).ready(
	function() {
		$('#log-form .field').not('.first').not('.error').hide();
		$('#log-form .field.first label').not('.error').bind('click',
			function(e) {
				$('#log-form div').not('.first').slideDown();
			}
		);
	}
)
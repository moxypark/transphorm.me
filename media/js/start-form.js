$(document).ready(
	function() {
		if($('label.error').length > 0) {
			$('label').not('.error').hide();
		} else {
			$('label[for=id_plan_name]').hide();
		}
		
		$('select#id_plan_copy').bind('change',
			function(e) {
				if($(this).val() == '') {
					$(this).parent().hide();
					$('label[for="id_plan_name"]').show();
					$('label[for="id_plan_name"]').focus();
				}
			}
		);
		
		$('input[type=radio][name=signup-create_account]').bind('change',
			function(e) {
				new_user = $(this).val() == 'True';
				$('label[for=id_signup-password_confirm]').slideToggle();
				$('label[for=id_signup-email]').slideToggle();
				$('label[for=id_signup-email_confirm]').slideToggle();
				$('label[for=id_signup-dob]').slideToggle();
				$('label[for=id_signup-gender]').slideToggle();
				$('label[for=id_signup-public]').slideToggle();
			}
		);
	}
);
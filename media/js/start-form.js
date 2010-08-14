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
				$('label[for=id_signup-password_confirm]').parent().slideToggle();
				$('label[for=id_signup-email]').parent().slideToggle();
				$('label[for=id_signup-email_confirm]').parent().slideToggle();
				$('label[for=id_signup-dob]').parent().slideToggle();
				$('label[for=id_signup-gender]').parent().slideToggle();
				$('label[for=id_signup-public]').parent().slideToggle();
			}
		);
		
		if($('input[type=radio][name=signup-create_account][value=False]').attr('checked') == true) {
			$('label[for=id_signup-password_confirm]').parent().hide();
			$('label[for=id_signup-email]').parent().hide();
			$('label[for=id_signup-email_confirm]').parent().hide();
			$('label[for=id_signup-dob]').parent().hide();
			$('label[for=id_signup-gender]').parent().hide();
			$('label[for=id_signup-public]').parent().hide();
		}
	}
);
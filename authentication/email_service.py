"""
Email service utility for sending OTP emails via Brevo (Sendinblue) API
"""
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

logger = logging.getLogger(__name__)


def send_otp_email_brevo(recipient_email, otp, recipient_name="Farmer"):
    """
    Send OTP email using Brevo (Sendinblue) API
    
    Args:
        recipient_email (str): Email address to send OTP to
        otp (str): The OTP code
        recipient_name (str): Name of the recipient
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
    
    if not brevo_api_key or brevo_api_key == 'YOUR_BREVO_API_KEY_HERE':
        logger.warning("Brevo API key is not configured")
        return False, "Brevo API key not configured"
    
    try:
        # Configure API key authorization
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        
        # Create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Email subject
        subject = f"🌱 {otp} is your RaithuSetu Login OTP"
        
        # Sender information
        sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'noreply@raithusetu.com')
        sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'RaithuSetu')
        
        # HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f3f4f6;">
            <div style="max-width: 520px; margin: 40px auto; padding: 0;">
                <div style="background-color: #f9fafb; padding: 24px; border-radius: 16px; border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="display: inline-block; background-color: #16a34a; color: white; width: 48px; height: 48px; line-height: 48px; border-radius: 12px; font-size: 24px; font-weight: bold;">🌱</div>
                        <h2 style="color: #111827; margin: 12px 0 4px 0; font-size: 22px;">RaithuSetu Smart Agriculture</h2>
                        <p style="color: #6b7280; font-size: 13px; margin: 0;">Farmer's Friend • రైతు మిత్రుడు • किसान मित्र</p>
                    </div>
                    
                    <!-- Main Content -->
                    <div style="background-color: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <p style="color: #374151; font-size: 16px; margin-bottom: 8px;">Namaste {recipient_name}! 🙏</p>
                        <p style="color: #374151; font-size: 14px; margin-bottom: 12px;">Use the following One-Time Password (OTP) to login to your farmer account:</p>
                        
                        <!-- OTP Box -->
                        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 2px dashed #16a34a; border-radius: 10px; padding: 18px; margin: 20px 0; font-size: 36px; font-weight: 800; letter-spacing: 10px; color: #15803d; text-align: center;">
                            {otp}
                        </div>
                        
                        <p style="color: #9ca3af; font-size: 12px; margin-top: 12px; line-height: 1.5;">
                            ⏰ Valid for <strong>10 minutes</strong><br>
                            🔒 Keep this code confidential<br>
                            ❌ If you didn't request this, please ignore this email
                        </p>
                    </div>
                    
                    <!-- Footer -->
                    <div style="text-align: center; margin-top: 20px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
                        <p style="color: #9ca3af; font-size: 11px; margin: 4px 0; line-height: 1.5;">
                            RaithuSetu • Empowering Indian Agriculture<br>
                            AI Crop Disease Detection • Real-time Mandi Prices • Govt Schemes
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_content = f"""
Namaste {recipient_name}!

Your RaithuSetu login verification code is: {otp}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

If you did not request this code, please ignore this email.

RaithuSetu - Farmer's Friend • Smart Agri
Empowering Indian Agriculture with AI
        """
        
        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": recipient_email, "name": recipient_name}],
            sender={"email": sender_email, "name": sender_name},
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            headers={"charset": "UTF-8"}
        )
        
        # Send the email
        logger.info(f"Sending OTP email via Brevo to {recipient_email}")
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        logger.info(f"✅ Brevo email sent successfully to {recipient_email}. Message ID: {api_response.message_id}")
        return True, None
        
    except ApiException as e:
        error_msg = f"Brevo API Exception: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"❌ Failed to send email via Brevo: {error_msg}")
        return False, error_msg


def send_otp_email_gmail(recipient_email, otp, recipient_name="Farmer"):
    """
    Send OTP email using Django's email backend (Gmail SMTP)
    Fallback option if Brevo is not configured
    
    Args:
        recipient_email (str): Email address to send OTP to
        otp (str): The OTP code
        recipient_name (str): Name of the recipient
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    from django.core.mail import send_mail
    
    try:
        subject = f"🌱 {otp} is your RaithuSetu Login OTP"
        
        plain_message = f"""
Namaste {recipient_name}!

Your RaithuSetu login verification code is: {otp}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

RaithuSetu - Farmer's Friend • Smart Agri
https://raithusetu.agri
        """
        
        html_message = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background-color: #f9fafb; border-radius: 16px; border: 1px solid #e5e7eb;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; background-color: #16a34a; color: white; width: 48px; height: 48px; line-height: 48px; border-radius: 12px; font-size: 24px; font-weight: bold;">🌱</div>
                <h2 style="color: #111827; margin: 12px 0 4px 0; font-size: 22px;">RaithuSetu Smart Agriculture</h2>
                <p style="color: #6b7280; font-size: 13px; margin: 0;">Farmer's Friend • రైతు మిత్రుడు • किसान मित्र</p>
            </div>
            <div style="background-color: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <p style="color: #374151; font-size: 14px; margin-bottom: 12px;">Use the following One-Time Password (OTP) to login to your farmer account:</p>
                <div style="background: #f0fdf4; border: 2px dashed #16a34a; border-radius: 10px; padding: 14px; margin: 16px 0; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #15803d;">
                    {otp}
                </div>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 8px;">Valid for 10 minutes. If you did not request this, please ignore this email.</p>
            </div>
        </div>
        """
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@raithusetu.com')
        
        logger.info(f"Sending OTP email via Gmail SMTP to {recipient_email}")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"✅ Gmail SMTP email sent successfully to {recipient_email}")
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Failed to send email via Gmail SMTP: {error_msg}")
        return False, error_msg


def send_otp_email(recipient_email, otp, recipient_name="Farmer"):
    """
    Send OTP email using the best available method
    Tries Brevo first, falls back to Gmail SMTP if Brevo is not configured
    
    Args:
        recipient_email (str): Email address to send OTP to
        otp (str): The OTP code
        recipient_name (str): Name of the recipient
    
    Returns:
        tuple: (success: bool, method: str, error_message: str or None)
    """
    # Try Brevo first
    success, error = send_otp_email_brevo(recipient_email, otp, recipient_name)
    if success:
        return True, "brevo", None
    
    logger.warning(f"Brevo failed, trying Gmail SMTP fallback. Brevo error: {error}")
    
    # Fallback to Gmail SMTP
    success, error = send_otp_email_gmail(recipient_email, otp, recipient_name)
    if success:
        return True, "gmail", None
    
    # Both methods failed
    return False, None, f"All email methods failed. Last error: {error}"

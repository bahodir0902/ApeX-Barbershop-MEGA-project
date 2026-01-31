"""
Social auth pipeline for Google OAuth.
"""


def save_user_details(backend, user, response, *args, **kwargs):
    """
    Save additional user details from social auth.
    
    This pipeline function is called during the social authentication process
    to save additional user details like name from the provider.
    """
    if backend.name == "google-oauth2":
        if response.get("given_name"):
            user.first_name = response.get("given_name")
        if response.get("family_name"):
            user.last_name = response.get("family_name", "")
        if response.get("picture"):
            # Could save profile picture URL here if needed
            pass
        user.is_verified = True
        user.save()

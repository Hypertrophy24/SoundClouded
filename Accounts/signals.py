from django.dispatch import receiver
from allauth.account.signals import user_signed_up, user_logged_in

@receiver([user_signed_up, user_logged_in])
def populate_spotify_uri(request, user, sociallogin=None, **kwargs):
    if sociallogin and sociallogin.account.provider == 'spotify':
        user.spotifyURI = sociallogin.account.uid
        user.username = sociallogin.account.uid
        user.save()
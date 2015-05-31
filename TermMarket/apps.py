from django.apps import AppConfig
import watson


class TermMarketConfig(AppConfig):
    name = "TermMarket"

    def ready(self):
        offer = self.get_model("Offer")
        watson.register(offer.objects.filter(is_available=True))

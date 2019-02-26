from django.db import models
from django.contrib.postgres.fields import JSONField

from ..propublica import ProPublicaAPI


class BillSources:
    SUNLIGHT = "sunlight"
    PROPUBLICA = "propublica"
    SOURCES = [(SUNLIGHT, SUNLIGHT), (PROPUBLICA, PROPUBLICA)]

class Bill(models.Model):
    id = models.CharField(max_length=255, primary_key=True)  # from sunlight

    title = models.CharField(max_length=1023)
    short_title = models.CharField(max_length=1023)
    short_summary = models.CharField(max_length=1023)
    number = models.IntegerField(default=0)
    b_type = models.CharField(max_length=63)
    source = models.CharField(max_length=50, choices=BillSources.SOURCES, default=BillSources.PROPUBLICA)

    congress_url = models.URLField(null=True, blank=True)
    govtrack_url = models.URLField(null=True, blank=True)

    # status
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def meta(self):
        if self.source == BillSources.PROPUBLICA:
            return self._get_propublica_api_details()
        return {}

    def update(self, data=None):
        if self.source == BillSources.PROPUBLICA:
            self._update_pro_publica_bill(data)

    def _update_pro_publica_bill(self, data=None):
        data = data or self._get_propublica_api_details()
        self.title = data['title']
        self.short_title = data['short_title']
        self.short_summary = data['summary_short']
        self.number = data['number']
        self.b_type = data['bill_type']
        self.congress_url = data['congress_url']
        self.govtrack_url = data['govtrack_url']
        self.save()

    def _get_propublica_api_details(self):
        return ProPublicaAPI().get_by_id(self.id)

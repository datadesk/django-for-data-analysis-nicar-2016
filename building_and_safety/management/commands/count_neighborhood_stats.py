import logging
from django.conf import settings
from building_and_safety.models import NeighborhoodV6
from django.db.models import Count, Avg
from django.core.management.base import BaseCommand, CommandError
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help="Rolls up the various stat counts for our NeighborhoodV6 models"

    def handle(self, *args, **options):
        for hood in NeighborhoodV6.objects.all():
            hood.total_complaints = hood.get_total_complaints()
            hood.open_complaints = hood.get_open_complaints()
            hood.closed_complaints = hood.get_closed_complaints()
            hood.open_over_one_year = hood.get_open_over_one_year()
            hood.closed_over_one_year = hood.get_closed_over_one_year()
            hood.total_unresolved_after_one_year = hood.get_total_unresolved_after_one_year()
            hood.percent_over_one_year_to_response = hood.get_percent_over_one_year_to_response()
            hood.avg_days_to_response = hood.get_avg_days_to_response()
            hood.kmf_median_days_to_response = hood.get_kmf_median_days_to_response()

            logger.debug("Aggregating information for %s" % hood)
            hood.save()

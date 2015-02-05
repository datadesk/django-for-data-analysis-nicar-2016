import os
import csv
import logging
from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos import Point
from building_and_safety.models import Complaint
from ast import literal_eval as make_tuple
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Load complaints filed to the city department of building and safety into the database."

    def parse_booleans(self, value):
        """
        Quick method to return True or False from the text values in the CSV
        """
        if value == "Y":
            return True
        else:
            return False    

    def parse_date(self, d):
        """
        Get a python date object from the date column in CSV
        """
        if d:
            parsed_date = datetime.strptime(d, "%m/%d/%Y").date()
            return parsed_date

    def flush_complaints(self):
        """
        Wipe all the complaints in the database.
        So we don't accidentally dupe ourselves. 
        """
        Complaint.objects.all().delete()

    def parse_lat_lon(self, s):
        """
        Read the latitude/longitude row into a tuple
        and return lat/lon values 
        """
        if s:
            t = make_tuple(s)
            return t[1], t[0]

    def get_is_closed(self, c):
        """
        If there's no closed date, a complaint is still "open"
        """
        if c.date_closed != None:
            return True
        else:
            return False

    def parse_priority(self, p):
        """
        Convert the values in a spreadsheet to integers
        """
        if p == "NORM":
            return 3
        elif p == "HIGH":
            return 2
        elif p == "HAZ":
            return 1
        else:
            return p

    def parse_int(self, s):
        """
        If the cell has a value, strip any possible extra spaces
        and return that value as an integer.
        """
        if s != None:
            try:
                s = s.strip()
                s = int(s)
            except ValueError, AttributeError:
                s = None
            return s
        else:
            return s

    def handle(self, *args, **options):
        """
        Load in our CSVs of open and closed complaints, 
        creating Complaint objects and adding them to a list
        which is then batch loaded into the database.

        We batch load them to keep from hitting the database for every record, 
        which would take approximately forever. 
        """
        self.data_dir = os.path.join(settings.ROOT_DIR, 'building_and_safety', 'data')
        self.flush_complaints()

        complaint_list = []

        # Our two CSVs of open and closed cases
        paths = ['Building_and_Safety_Customer_Service_Request_out.csv', 'Building_and_Safety_Customer_Service_Request__Closed__out.csv']

        for p in paths: 
            path = os.path.join(self.data_dir, p)
            reader = csv.DictReader(open(path, 'r'))
            for row in reader:
                c = Complaint(
                    csr = row["CSR Number"],
                    ladbs_inspection_district = row["LADBS Inspection District"] ,
                    address_house_number = row["Address House Number"],
                    address_house_fraction = row["Address House Fraction Number"],
                    address_street_direction = row["Address Street Direction"],
                    address_street_name = row["Address Street Name"],
                    address_street_suffix = row["Address Street Suffix"],
                    address_street_suffix_direction = row["Address Street Suffix Direction"],
                    address_street_zip = row["Address Street Zip"],
                    date_received = self.parse_date(row["Date Received"]),
                    date_closed = self.parse_date(row["Date Closed"]),
                    date_due = self.parse_date(row["Due Date"]),
                    case_flag = self.parse_booleans(row["Case Flag"]),
                    csr_priority = self.parse_priority(row["CSR Priority"]),
                    gis_pin = row["GIS Parcel Identification Number (PIN)"],
                    csr_problem_type = row["CSR Problem Type"],
                    area_planning_commission = row["Area Planning Commission (APC)"],
                    case_number_csr = row["Case Number Related to CSR"],
                    response_days = self.parse_int(row["Response Days"]),
                    lat = parse_lat_lon(row["Latitude/Longitude"])[1],
                    lon = parse_lat_lon(row["Latitude/Longitude"])[0]
                    )

                c.is_closed = self.get_is_closed(c)

                # TODO
                # We can eliminate a lot of management commands here by setting the values on load
                # set_full_address
                # get_days_since_complaint
                # get_days_past_due
                c.full_address = c.get_full_address(c)
                # c.days_since_complaint = TK

                complaint_list.append(c)

        logger.debug("Loading complaints to database.")

        # Batch upload our complaints to the database, 500 at a time
        Complaint.objects.bulk_create(
            complaint_list,
            batch_size=500
        )
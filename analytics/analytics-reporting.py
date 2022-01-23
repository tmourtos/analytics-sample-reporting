# coding=utf-8
import time
import argparse

from google.cloud import bigquery
from datetime import datetime, timedelta
from pprint import pprint, pformat

from utils import USER_TYPES, ERRORS

KEYFILE = R'.\analytics\analytics-sample-keyfile.json'


class CR(object):
    """
        Conversion rate calculator
    """

    def __init__(self):
        self.conversions = 0
        self.sessions = 0

    def cr(self):
        """
            Calculate the conversion rate
        """
        if self.sessions:
            return round((self.conversions / self.sessions) * 100, 2)
        else:
            return

    def __repr__(self):
        return f'{self.cr()} %'


class Session(object):
    """
        An Analytics session
    """

    def __init__(self, session_id=None, user_id=None, date=None):
        self.session_id = session_id
        self.user_id = user_id
        self.date = date

        self.session_start = None
        self.session_end = None

        # App Tracking
        self.platform = None

        # Metrics
        self.transactions = 0
        self.user_type = None

    def __repr__(self):
        return pformat(vars(self), indent=2, width=1)


class AnalyticsSessions(object):
    def __init__(self, selected_date, platform=False, user_type=False):
        self.selected_date = selected_date
        self.target_table = f'ga_sessions_{self.selected_date}'
        self.platform = platform
        self.user_type = user_type

        self.available_dates = list()

        self.sessions = list()

    def __repr__(self):
        s = '%s' % self.__class__.__name__
        return s

    def run(self):
        """
            Execute Analytics sessions info
        """
        self._instantiate()
        self._validate()
        self._get_sessions()
        self._report()

    def _instantiate(self):
        """
            Instantiate the BigQuery service
        """
        try:
            self.bigquery_client = bigquery.Client.from_service_account_json(KEYFILE)
        except BaseException as exception:
            raise Exception('{} - {} - {} - {}'.format(datetime.now(),
                                                       repr(self),
                                                       ERRORS['ERR01']['CATEGORY'],
                                                       str(exception)))

    def _validate(self) -> bool:
        """
            Check if the provided date exists in the sample dataset
        """

        schema_tables_query = """
            SELECT table_name
            FROM `bigquery-public-data.google_analytics_sample`.INFORMATION_SCHEMA.TABLES;
        """
        data_results = self.bigquery_client.query(schema_tables_query)

        if not data_results:
            raise Exception('{} - {} - {} - {}'.format(datetime.now(),
                                                       repr(self),
                                                       ERRORS['ERR02']['CATEGORY'],
                                                       ERRORS['ERR02']['DESCRIPTION']))

        for row in data_results:
            available_date = row['table_name'].split('_')[-1]
            if self.selected_date == available_date:
                return True
        else:
            raise Exception('{} - {} - {} - {}'.format(datetime.now(),
                                                       repr(self),
                                                       ERRORS['ERR03']['CATEGORY'],
                                                       ERRORS['ERR03']['DESCRIPTION']))

    def _get_sessions(self):
        """'
            Collect Google Analytics data for the selected date
        """

        analytics_data_query = """
            SELECT visitId,
                   visitStartTime,
                   date,
                   device,
                   totals,
                   fullVisitorId               
            FROM `bigquery-public-data.google_analytics_sample.{table_name}`;
        """.format(table_name=self.target_table)
        data_results = self.bigquery_client.query(analytics_data_query)

        if not data_results:
            raise Exception('{} - {} - {} - {}'.format(datetime.now(),
                                                       repr(self),
                                                       ERRORS['ERR02']['CATEGORY'],
                                                       ERRORS['ERR02']['DESCRIPTION']))

        for data_row in data_results:
            if not data_row['visitId']:
                continue
            if not data_row['fullVisitorId']:
                continue

            session = Session(session_id=data_row['visitId'],
                              user_id=data_row['fullVisitorId'],
                              date=self.selected_date)

            session.session_start = datetime.fromtimestamp(data_row['visitStartTime'])
            time_on_site = data_row['totals']['timeOnSite'] if data_row['totals']['timeOnSite'] else 0
            session.session_end = session.session_start + timedelta(seconds=time_on_site)

            session.platform = data_row['device']['deviceCategory']

            if data_row['totals']['transactions']:
                session.transactions = data_row['totals']['transactions']

            session.user_type = USER_TYPES[data_row['totals']['newVisits']]

            self.sessions.append(session)

    def _report(self):
        """
            Produce the required report
        """

        conversion_rate = dict()

        if self.user_type and self.platform:
            for session in self.sessions:
                conversion_rate.setdefault(session.user_type, dict())
                conversion_rate[session.user_type].setdefault(session.platform, CR())
                conversion_rate[session.user_type][session.platform].sessions += 1
                if session.transactions:
                    conversion_rate[session.user_type][session.platform].conversions += 1
        elif self.user_type and not self.platform:
            for session in self.sessions:
                conversion_rate.setdefault(session.user_type, CR())
                conversion_rate[session.user_type].sessions += 1
                if session.transactions:
                    conversion_rate[session.user_type].conversions += 1
        elif not self.user_type and self.platform:
            for session in self.sessions:
                conversion_rate.setdefault(session.platform, CR())
                conversion_rate[session.platform].sessions += 1
                if session.transactions:
                    conversion_rate[session.platform].conversions += 1
        else:
            for session in self.sessions:
                if not conversion_rate:
                    conversion_rate = CR()
                conversion_rate.sessions += 1
                if session.transactions:
                    conversion_rate.conversions += 1

        print('Conversion Rate details:')
        pprint(conversion_rate)


def google_analytics_reporting():
    """
        Collect Analytics Sessions for the required date and report.
    """
    parser = argparse.ArgumentParser(description='Add report parameters')
    parser.add_argument('--date', metavar='date', type=str,
                        help='The selected date in the format YYYYMMDD')
    parser.add_argument('--user', action='store_true', default=False,
                        help='Use to apply User Type granularity')
    parser.add_argument('--platform', action='store_true', default=False,
                        help='Use to apply Platform granularity')
    args = parser.parse_args()

    analytics_reporting = AnalyticsSessions(selected_date=args.date,
                                            platform=args.platform,
                                            user_type=args.user)
    analytics_reporting.run()


if __name__ == '__main__':
    start_time = time.time()
    google_analytics_reporting()
    print("Program completed successfully in {} minutes".format(round((time.time() - start_time) / 60, 2)))

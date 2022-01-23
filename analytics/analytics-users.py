# coding=utf-8
import time
import csv

from google.cloud import bigquery
from datetime import datetime
from pprint import pprint, pformat

from utils import ERRORS

KEYFILE = R'.\analytics\analytics-sample-keyfile.json'


class User(object):
    """
        An Analytics user
    """

    def __init__(self, user_id=None):
        self.user_id = user_id

        self.first_session = None
        self.first_conversion = None
        self.time_to_convert = None

    def __repr__(self):
        return pformat(vars(self), indent=2, width=1)


class AnalyticsUsers(object):
    def __init__(self):
        self.users = list()

    def __repr__(self):
        s = '%s' % self.__class__.__name__
        return s

    @staticmethod
    def _to_dict(_object):
        return _object.__dict__

    def run(self):
        """
            Execute app sessions info
        """
        self._instantiate()
        self._get_user_info()
        self._export()

    @staticmethod
    def _sec_to_mins(view_time: int) -> float:
        """
            Convert milliseconds value to minutes
        :param view_time: The view time in milliseconds
        :return: The view time in minutes
        """
        return view_time / float(60000)

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

    def _get_user_info(self):
        """'
            Collect Google Analytics user data
        """

        analytics_data_query = """
            SELECT fullVisitorId                                   AS user_id,
                   MIN(TIMESTAMP_SECONDS(visitStartTime))          AS first_session,
                   MIN(CASE 
                       WHEN totals.transactions > 0
                       THEN TIMESTAMP_SECONDS(visitStartTime) END) AS first_conversion
            FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
            GROUP BY fullVisitorId
            HAVING first_conversion IS NOT NULL;
        """
        data_results = self.bigquery_client.query(analytics_data_query)

        if not data_results:
            raise Exception('{} - {} - {} - {}'.format(datetime.now(),
                                                       repr(self),
                                                       ERRORS['ERR02']['CATEGORY'],
                                                       ERRORS['ERR02']['DESCRIPTION']))

        for data_row in data_results:
            user = User(user_id=data_row['user_id'])

            user.first_session = data_row['first_session']
            user.first_conversion = data_row['first_conversion']

            if user.first_conversion:
                user.time_to_convert = round((user.first_conversion - user.first_session).seconds, 2)

            self.users.append(user)

    def _export(self):
        """
            Produce the required report
        """
        user_data = list()
        try:
            with open(R'.\user_info.csv', 'w', newline='') as output:
                writer = csv.writer(output)

                header = ['user', 'first_session', 'time_to_convert']
                writer.writerow(header)

                for user_details in self.users:
                    row = [user_details.user_id, user_details.first_session, user_details.time_to_convert]
                    user_data.append(row)
                writer.writerows(user_data)
        except BaseException as exception:
            raise Exception('{} - {} - {} - {}'.format(datetime.now(),
                                                       repr(self),
                                                       ERRORS['ERR04']['CATEGORY'],
                                                       str(exception)))


def google_analytics_users():
    """
        Collect Analytics Users info.
    """
    analytics_reporting = AnalyticsUsers()
    analytics_reporting.run()


if __name__ == '__main__':
    start_time = time.time()
    google_analytics_users()
    print("Program completed successfully in {} minutes".format(round((time.time() - start_time) / 60, 2)))

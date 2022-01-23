# Analytics Sample Reporting

A simple project that uses the Google Analytics 
sample data to perform reporting operations. 

## Requirements

To install dependencies execute the line below in the project directory:
```
pip install -r requirements.txt
```

## Usage

### CR Reporting

To collect Conversion Rate report for a given date
execute the line below in the project directory:
```
python analytics\analytics-reporting.py
```
Required parameters:
* ``--date`` the selected reporting date in YYYYMMDD format

Optional parameters:
* ``--platform`` to apply platform (Desktop, Mobile, Tablet) granularity
* ``--user`` to apply user (New, Returning) granularity

### User Info

To collect user info details report
execute the line below in the project directory:
```
python analytics\analytics-users.py
```

## References
Material used in this project:

[BigQuery APIs and Libraries Overview](https://cloud.google.com/bigquery/docs/reference/libraries-overview)

[BigQuery Export schema](https://support.google.com/analytics/answer/3437719?hl=en)

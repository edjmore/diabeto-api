The goal of this project is to provide easy access to the raw data available
thru the Fitbit API and on the OneTouchReveal website. My theory is that this
combined data may be useful for diabetics interested in relationships between
exercise and blood glucose levels.

Files & packages:
  - api:
      interfaces for accessing the Fitbit API and scraping onetouchreveal.com
  - model:
      datatypes for representing a diabetes profile and log entries
  - server.py:
      the Flask server capable of responding to API requests and front-end site

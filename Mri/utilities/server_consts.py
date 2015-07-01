"""Contains the constants for the Mri-server. These shouldn't be
user-changable but should be editable in source just in case"""


class ServerConsts(object):
    class API_URL(object):
        # Create a new report or view all reports
        REPORT = '/api/reports'
        # Edit or delete a specific report
        REPORT_ID = '/api/report/'
        # Create a new event or list events
        EVENT = '/api/events'
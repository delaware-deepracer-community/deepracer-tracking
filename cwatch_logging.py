from config import settings
from datetime import datetime

class CWatch_logging:
    """
    This class for logging messaged to CloudWatch log stream
    """
    
    def __init__(self, logGroupName=None, logStreamName=None):
        """
        This is a constructor to initialize with log group and logstream
        """
        self.logGroupName = logGroupName if logGroupName is not None else 'deepracer-tracking-log-group'
        self.logStreamName = logStreamName if logStreamName is not None else 'deepracer-tracking-log-stream'
        self.cwLogClient = settings.LOG_CLIENT
        
    def send_log(self, message):
        """
        This is a method to put log events on a log stream
        """
        response = self.cwLogClient.put_log_events(
            logGroupName=self.logGroupName,
            logStreamName=self.logStreamName,
            logEvents=[
                {
                    'timestamp': int(round(datetime.now().timestamp()*1000, 0)),
                    'message': message
                },
            ]
        )
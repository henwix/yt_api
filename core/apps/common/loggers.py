import logging


class LogMetaFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'log_meta'):
            record.log_meta = None
        return True

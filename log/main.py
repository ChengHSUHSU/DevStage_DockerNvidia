




def setup_logger(date, logger_name, log_file, level=logging.INFO):
    try:
        l = logging.getLogger(logger_name)
        formatter = logging.Formatter('{} : %(message)s'.format(date))
        fileHandler = logging.FileHandler('bucket_log/api_log/'+log_file, mode='a')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)
    except Exception as error_message:
        print(error_message)
        GoToSlackAlarm(error_message=error_message)


def add_log_record(message):
    # init
    try:
        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        now_date = now_datetime.split()[0]
        setup_logger(now_datetime, 'log', r'{}.log'.format(now_date))
        log = logging.getLogger('log')
        log.info(message)

    except Exception as error_message:
        print(error_message)
        try:
            GoToSlackAlarm(error_message=error_message)
        except:
            pass



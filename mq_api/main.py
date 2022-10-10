



def MessageQueue(StartDateTime=str, 
                 ClassBrandID=str, 
                 ClassType=str, 
                 ClassPeriod=str, 
                 ClassNumber=str):
    # init
    host = mq_info['host']
    port = mq_info['port']
    queue = mq_info['queue']
    username = mq_info['username']
    password = mq_info['password']
    virtual_host = mq_info['virtual_host']
    ClassNumber = [int(val) for val in ClassNumber.split('-')]
    timestamp = datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S').timestamp()




    try:
        credentials = pika.PlainCredentials(username=username, 
                                            password=password)
        
        connection = pika.ConnectionParameters(host=host, 
                                               port=port,
                                               credentials=credentials,
                                               virtual_host=virtual_host)
        
        connection = pika.BlockingConnection(connection)

        message = str({
                      'StartDateTime' : int(timestamp), 
                      'BrandID' : int(ClassBrandID), 
                      'Type' : int(ClassType), 
                      'Category' : 1, 
                      'Period' : int(ClassPeriod),
                      'Number' : ClassNumber
                      })
        
        channel = connection.channel()
        channel.basic_publish(body=message, 
                              exchange='', 
                              routing_key=queue)
        connection.close()
        
        # add log
        StartDate = StartDateTime
        BrandID_str = str(ClassBrandID)
        Period_str = str(ClassPeriod)
        unique_entity = 'time:{}|brand_id:{}|period:{}'.format(StartDate, 
                                                               BrandID_str, 
                                                               Period_str)
        
        add_log_record(message='[MessageQueue-func] : [1-1]({})'.format(unique_entity))
    
    except Exception as error_message:
        add_log_record(message='[MessageQueue-func] : [1-2]({})#{}'.format(unique_entity, error_message))
        GoToSlackAlarm(error_message=error_message)


# message queue
if ProductStage == 'Stage':
    mq_info = {
               'username' : 'user-dcgs20',
               'password' : 'dcgs20',
               'host' : '172.16.81.77',
               'port' : 5672,
               'virtual_host' : 'vh-dcgs',
               'queue' : 'dcgs20.schedule.queue'
             }
elif ProductStage == 'Product':
    mq_info = {
               'username' : 'user-dcgs20',
               'password' : '1acd013f53',
               'host' : 'tgop-rabbit.tutorabc.com',
               'port' : 5672,
               'virtual_host' : 'vh-dcgs',
               'queue' : 'dcgs20.schedule.queue'
             }




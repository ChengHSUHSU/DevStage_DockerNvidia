

import logging 
from flask_cors import CORS
from multiprocessing import Pool
from ServiceUtil import SchedulingTask
from flask import Flask, request, jsonify
from config import ProductStage, StageIP, GetPort, SchedulingPort, ProductAPI_IP

  

 


 

# set get-api url
if ProductStage == 'Product':
    url_for_external_get = 'http://{}:{}/ExternalGetService'.format(ProductAPI_IP, GetPort)
elif ProductStage == 'Stage':
    url_for_external_get = 'http://{}:{}/ExternalGetService'.format(StageIP, GetPort)




# init
app = Flask(__name__)
CORS(app)

    
 

@app.route('/dcgs20_scheduling_api_post', methods=['POST']) 
def SchedulingServicePost():
    # init
    insertValues = request.get_json()
    StartDate = insertValues['StartDate'] 
    Mode = insertValues['Mode']  
    db_name = insertValues['db_name']  
    Class = insertValues['Class']  


    # fool-proof mechanism
    if 'Period' not in Class:
        Class['Period'] = 1
 

    # if 45min course, then it must be 1-N
    if Class['Period'] == 1 and 'Number' not in Class:
        Class['Number'] = [1]


    # if 25min course
    if Class['Period'] == 2:
        if 'Number' in Class:
            if isinstance(Class['Number'], list) is True:
                # fool-proof mechanism 
                if len(Class['Number']) == 0:
                    # 1-1 and 1-N
                    Class['Number'] = [0, 1]
            else:
                # 1-1 and 1-N
                Class['Number'] = [0, 1]
        else:
            # 1-1 and 1-N
            Class['Number'] = [0, 1]
    
    # 排課
    if Mode == 'scheduling': 
        required_input = {
                          'StartDate' : StartDate, 
                          'db_name' : db_name, 
                          'url_for_external_get' : url_for_external_get, 
                          'Class' : Class, 
                          'mode' : 'run'
                         }
        Pool(1).map_async(SchedulingTask, [required_input])
        return jsonify({'return': 'sucess_scheduling'}) 
    
    # 二階段 預排
    elif Mode == 'pre_scheduling': 
        required_input = {
                          'StartDate' : StartDate, 
                          'db_name' : db_name, 
                          'url_for_external_get' : url_for_external_get, 
                          'Class' : Class, 
                          'mode' : 'pre_run'
                         }
        Pool(1).map_async(SchedulingTask, [required_input])
        return jsonify({'return': 'sucess_scheduling'}) 
   
    else:
        return jsonify({'return': 'Fail(Stage)(StartDate:{})'.format(StartDate)})





import docker
import logging
import requests
import traceback
from datetime import datetime
from datetime import datetime as dt
from mainScheduling import mainScheduling
from config import ProductStage, ProdMongodbUrl, StageMongodbUrl
from collection_stage_util.write_organic_data_to_db import Organic_Data_TO_DB








def SchedulingTask(required_input=dict): 
    # init
    mode = required_input['mode']
    Class = required_input['Class']
    db_name = required_input['db_name']
    StartDate = required_input['StartDate']
    url_for_external_get = required_input['url_for_external_get']
    Number_list = sorted([str(val) for val in Class['Number']])
    ClassNumber = '-'.join(Number_list)
    
    Type_str = str(Class['Type'])
    Period_str = str(Class['Period'])
    BrandID_str = str(Class['BrandID'])
    
    # docker
    client = docker.from_env()
    python_cmd  = '''
                python3 src/mainSchedulingTask.py --StartDate "{}" 
                                                  --db_name "{}" 
                                                  --url_for_external_get "{}" 
                                                  --ClassBrandID "{}" 
                                                  --ClassType "{}" 
                                                  --mode "{}" 
                                                  --ClassPeriod "{}"
                                                  --ClassNumber "{}"
                '''
    try:
        python_cmd = python_cmd.format(StartDate, 
                                       db_name, 
                                       url_for_external_get, 
                                       BrandID_str, 
                                       Type_str, 
                                       mode, 
                                       Period_str, 
                                       ClassNumber)
 
        container = client.containers.run(image='image-hub.tutorabc.com/ai/dcgs_image_model', #image-hub.tutorabc.com/ai/dcgs_image_model
                                          command=python_cmd,
                                          volumes=[
                                            '/app/AiModels/bucket_model:/tmp/DCGS/bucket_model', 
                                            '/app/AiModels/train_data:/tmp/DCGS/train_data', 
                                            '/var/run/docker.sock:/var/run/docker.sock'
                                            ],
                                          network_mode='host',
                                          remove=True,
                                          detach=True,
                                          name='schedulingtask-brandid_{}-type_{}-mode_{}-period_{}'.format(BrandID_str, 
                                                                                                            Type_str, 
                                                                                                            mode, 
                                                                                                            Period_str)) 
        container.logs()
    except Exception as error_message:
        GoToSlackAlarm(error_message=error_message, location='AI_SERVER')


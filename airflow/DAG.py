# 載入套件
  
from datetime import date, timedelta, datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
import pendulum
  
# 將此DAG的時區設定為台北時間
 
local_tz = pendulum.timezone("Asia/Taipei")
 
# 輸入bash指令以及docker指令中的時間，如果為更動的變數，可使用Python中的時間填入
# yesterday = date.today() - timedelta(days=1)為昨日的時間
# 如果Python的執行指令如下，並且昨日為20210809，則
# /usr/local/bin/python main.py Adult 20210809 ai_db
# 可以用以下表示:
# '/usr/local/bin/python main.py Adult ' + str(yesterday.strftime('%Y%m%d')) + ' ai_db'
  
yesterday = date.today() - timedelta(days=1)
  
# 預先輸入的參數
# 所有的DAG啟動都是以start_date為基準，往後第二個時間區間為第一次啟動排程的時間
# 例如: 以下範例start_date為2021/8/5，排程時間為每日早上07:15("15 07 * * *")，因此往後第一個時間區間為2021/8/5 07:15啟動此DAG(但不會執行)
# 等到往後第二個時間區間(2021/8/6 07:15)才會執行此DAG
 
default_args = {
        'owner'                 : 'AI',
        'description'           : 'Karma6.0',
        'depend_on_past'        : False,
        'start_date'            : datetime(2021, 8, 5, tzinfo=local_tz),
        'email'                 : ['AI_helpdesk@tutorabc.com'],
        'email_on_failure'      : True,
        'email_on_retry'        : True,
        'retries'               : 1,
        'retry_delay'           : timedelta(minutes=1)
}
  
# DummyOperator為一個不會執行任何動作的node
# DockerOperator為一個執行其他docker image的指令的node
# BashOperator為一個執行bash指令的node
  
with DAG('karma60-DAG', default_args=default_args, schedule_interval="15 07 * * *", catchup=False) as dag:
    start_dag = DummyOperator(
        task_id='start_dag'
        )
 
    end_dag = DummyOperator(
        task_id='end_dag'
        )
 
    t1 = DockerOperator(
        task_id='uspBatKarma6Adult',
        image='karma60_img',
        auto_remove=True,
        api_version='auto',
        command='/usr/local/bin/python sp_execute.py uspBatKarma6Adult.sql',
        docker_url="unix://var/run/docker.sock",
        network_mode="docker-airflow_default",
        volumes=["/home/tutorabc/DSAI/config:/home/Karma6/config"]
        )
 
    ts1 = BashOperator(
        task_id='T_sleep1',
        bash_command='sleep 5',
        retries=3
    )
 
    t2 = DockerOperator(
        task_id='TutorABC_Data',
        image='karma60_img',
        auto_remove=True,
        api_version='auto',
        command='/usr/local/bin/python main.py Adult ' + str(yesterday.strftime('%Y%m%d')) + ' ai_db',
        docker_url="unix://var/run/docker.sock",
        network_mode="docker-airflow_default",
        volumes=["/home/tutorabc/DSAI/config:/home/Karma6/config"]
        )
         
    ts2 = BashOperator(
        task_id='T_sleep2',
        bash_command='sleep 5',
        retries=3
    )
 
    j1 = DockerOperator(
        task_id='uspBatKarma6jr',
        image='karma60_img',
        auto_remove=True,
        api_version='auto',
        command='/usr/local/bin/python sp_execute.py uspBatKarma6jr.sql',
        docker_url="unix://var/run/docker.sock",
        network_mode="docker-airflow_default",
        volumes=["/home/tutorabc/DSAI/config:/home/Karma6/config"]
        )
 
    js1 = BashOperator(
        task_id='jr_sleep1',
        bash_command='sleep 5',
        retries=3
    )
 
    j2 = DockerOperator(
        task_id='TutorJr_Data',
        image='karma60_img',
        auto_remove=True,
        api_version='auto',
        command='/usr/local/bin/python main.py jr ' + str(yesterday.strftime('%Y%m%d')) + ' ai_db',
        docker_url="unix://var/run/docker.sock",
        network_mode="docker-airflow_default",
        volumes=["/home/tutorabc/DSAI/config:/home/Karma6/config"]
        )
 
    js2 = BashOperator(
        task_id='jr_sleep2',
        bash_command='sleep 5',
        retries=3
    )
 
    gen = DockerOperator(
        task_id='uspRptKarma60GenData',
        image='karma60_img',
        auto_remove=True,
        api_version='auto',
        command='/usr/local/bin/python sp_execute.py uspRptKarma60GenData.sql',
        docker_url="unix://var/run/docker.sock",
        network_mode="docker-airflow_default",
        volumes=["/home/tutorabc/DSAI/config:/home/Karma6/config"]
    )
     
    # 此處為DAG的流程
     
    start_dag >> t1 >> ts1 >> t2 >> ts2 >> gen
    start_dag >> j1 >> js1 >> j2 >> js2 >> gen
    gen >> end_dag
 

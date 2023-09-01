import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

#####################################################################################
# Variables in Airflow

WOLNO_HOST = Variable.get('WOLNO_HOST')
WOLNO_NAME = Variable.get('WOLNO_NAME')
WOLNO_USER = Variable.get('WOLNO_USER')
WOLNO_PASSWORD = Variable.get('WOLNO_PASSWORD')


#####################################################################################
# DAG

wolno_dag = DAG(
    'Wolno',
    start_date=datetime.datetime(2023, 9, 1),
    schedule_interval='*/5 * * * *',
    catchup = False
)

#####################################################################################
# Tasks

wolno_data_download_task = BashOperator(
    task_id='Wolno_data_downloader_task',
    bash_command=f'/opt/airflow/envs/wolno-env/bin/python /opt/airflow/scripts/wolno-czu-project/src/main.py --db_host {WOLNO_HOST} --db_name {WOLNO_NAME} --db_user {WOLNO_USER} --db_password {WOLNO_PASSWORD}',
    retries=3,
    retry_delay=datetime.timedelta(seconds=180),
    dag=wolno_dag
)

#####################################################################################
# Tasks workflow

wolno_data_download_task
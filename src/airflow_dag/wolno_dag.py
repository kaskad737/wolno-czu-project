import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

#####################################################################################
# Variables in Airflow

DB_HOST = Variable.get('DB_HOST')
DB_NAME = Variable.get('DB_NAME')
DB_USER = Variable.get('DB_USER')
DB_PASSWORD = Variable.get('DB_PASSWORD')


#####################################################################################
# DAG

wolno_dag = DAG(
    'Wolno',
    start_date=datetime.datetime(2023, 8, 26),
    schedule_interval='0 12 * * *',
    catchup = False
)

#####################################################################################
# Tasks

wolno_data_download_task = BashOperator(
    task_id='Wolno_data_downloader_task',
    bash_command=f'/opt/airflow/envs/wolno-env/bin/python /opt/airflow/scripts/wolno-czu-project/src/main.py --db_host {DB_HOST} --db_name {DB_NAME} --db_user {DB_USER} --db_password {DB_PASSWORD}',
    retries=3,
    retry_delay=datetime.timedelta(seconds=180),
    dag=wolno_dag
)

#####################################################################################
# Tasks workflow

wolno_data_download_task

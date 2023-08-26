import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

DB_HOST = Variable.get('DB_HOST')
DB_NAME = Variable.get('DB_NAME')
DB_USER = Variable.get('DB_USER')
DB_PASSWORD = Variable.get('DB_PASSWORD')



#####################################################################################
# DAG


wolno_dag = DAG(
    'Wolno',
    start_date=datetime.datetime(2023, 8, 26),
    schedule_interval='*/5 * * * *',
    catchup = False

)

#####################################################################################
# Tasks

wolno_data_download_task = BashOperator(
    task_id='Wolno data downloader task',
    bash_command=f'/opt/airflow/envs/wolno-env/bin/python /opt/airflow/scripts/wolno-czu-project/src/main.py -h {DB_HOST} -n {DB_NAME} -u {DB_USER} -p {DB_PASSWORD}',
    retries=3,
    retry_delay=datetime.timedelta(seconds=180),
    dag=wolno_dag
)

#####################################################################################
# Tasks workflow

wolno_data_download_task

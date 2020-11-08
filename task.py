import os
import boto3
import getpass
from invoke import Collection, task, Config
import docker

client = docker.from_env()
sudo_pass = getpass.getpass('Enter your sudo password: ' )


@task
def start_ssh(c):
    
    global AWS_ACCESS_KEY_ID
    global AWS_SECRET_ACCESS_KEY
    
    AWS_ACCESS_KEY_ID = getpass.getpass('Enter your AWS_ACCESS_KEY_ID: ' )
    AWS_SECRET_ACCESS_KEY = getpass.getpass('Enter your AWS_SECRET_ACCESS_KEY: ' )
    print(AWS_ACCESS_KEY_ID)
    print(AWS_SECRET_ACCESS_KEY)
    
    
    
    #get_docker_parms(c)
    build_image(c)
    #run_container(c)



def get_docker_parms(c):
    print('get parameter')

    ssm = boto3.client('ssm',
    region_name="us-east-2",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    parameters = ssm.describe_parameters()['Parameters']
    print(parameters)

def build_image(c):
    #result = c.sudo('docker build --no-cache -t ssh_reverse .')
    #print(result)
    print(client.containers.list())
    try:
        obj_container = client.containers.get('ssh_reverse')
        obj_container.stop()
        obj_container.remove()
        client.containers.run(
        image='ssh_reverse',
        network_mode='host',
        restart_policy={"Name":"always"},
        name="ssh_reverse",
        volumes=['/home/obedmacallums/Desktop/ssh_docker', '/home'],
        command='ssh_reverse ssh -o StrictHostKeyChecking=no -N -i /home/id_rsa -R 8080:localhost:22 ssh_reverse@3.23.171.10')

        print(client.containers.list())
        print('run container')
    except Exception as e:
        print(e)
        client.containers.run(
        image='ssh_reverse',
        network_mode='host',
        restart_policy={"Name":"always"},
        name="ssh_reverse",
        volumes=['/home/obedmacallums/Desktop/ssh_docker', '/home'],
        command='ssh_reverse ssh -o StrictHostKeyChecking=no -N -i /home/id_rsa -R 8080:localhost:22 ssh_reverse@3.23.171.10')
        
        print(e)

    #result = c.sudo('docker build -t ssh_reverse .')
    




ns = Collection(start_ssh)
ns.configure({'sudo': {'password': sudo_pass}})

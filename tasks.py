import getpass
from invoke import Collection, task, Config
import requests
import time
import docker
import configparser




@task
def config(c):
    global parkingfile_username
    global parkingfile_token
    global sudo_password
    
    parkingfile_username = getpass.getpass(prompt='parkingfile_username: ', stream=None)
    parkingfile_token = getpass.getpass(prompt='parkingfile_token: ', stream=None)
    sudo_password = getpass.getpass(prompt='Sudo Password: ', stream=None)
    
    c['sudo']['password']= sudo_password

    config = configparser.ConfigParser()

    config['DEFAULT'] = {'sudo_password': sudo_password, 
                        'parkingfile_username':parkingfile_username,
                        'parkingfile_token':parkingfile_token}
    
    with open('configfile', 'w') as configfile:
        config.write(configfile)

    server_request(c)
    


@task
def server_request(c):
    
    
    config = configparser.ConfigParser()
    config.read('configfile')
    
    sudo_password = config['DEFAULT']['sudo_password']
    parkingfile_username = config['DEFAULT']['parkingfile_username']
    parkingfile_token = config['DEFAULT']['parkingfile_token']
    
    c['sudo']['password'] = sudo_password
    
    headers={'Authorization': f'Token {parkingfile_token}'}

    while True:
        try:
            url = 'http://127.0.0.1:8000/api/server_request'
            r = requests.get(url, headers=headers, params={'username':parkingfile_username})
            print (r.json())
            time.sleep(5)
        except Exception as e:
            print(e)
            update_docker(c)
            time.sleep(5)


@task
def update_docker(c):
    ok = c.sudo('ls /root')
    print(ok)





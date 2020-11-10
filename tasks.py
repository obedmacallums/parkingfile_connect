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
    public_key =  make_ssh_keys(c)

    config['DEFAULT'] = {'sudo_password': sudo_password, 
                        'parkingfile_username':parkingfile_username,
                        'parkingfile_token':parkingfile_token}
    config['AGENT'] = {'public_key_agent': public_key}
    with open('configfile', 'w') as configfile:
        config.write(configfile)
    
    
    server_request(c)


@task   
def make_ssh_keys(c):
    c.sudo('sudo ssh-keygen -t rsa -b 2048 -f /root/.ssh/parkingfile -N ""')
    public_key = c.sudo('cat /root/.ssh/parkingfile.pub').stdout
    return public_key

    
@task
def allow_key(c, key):
    try:
        
        c.sudo(f'sudo bash -c "echo "{key}" > /root/.ssh/authorized_keys"')
        return True
    except Exception as e:
        print(e)
        return False



@task
def server_request(c):
    
    
    config = configparser.ConfigParser()
    config.read('configfile')
    
    sudo_password = config['DEFAULT']['sudo_password']
    parkingfile_username = config['DEFAULT']['parkingfile_username']
    parkingfile_token = config['DEFAULT']['parkingfile_token']
    public_key_agent = config['AGENT']['public_key_agent']

    c['sudo']['password'] = sudo_password
    
    headers={'Authorization': f'Token {parkingfile_token}'}

    while True:

        try:
            url = 'http://127.0.0.1:8000/api/server_request'
            r = requests.post(url, headers=headers, data={'username':parkingfile_username, 'public_key': public_key_agent})
            r_json = r.json()
            print(r_json)
            if r_json.get('created', False):
                allow_key(c, r_json['public_key_to_agents'])
                print ('se ha creado objeto agente')
                print('levantando todo')
                server_params = {}
                up_docker(c, server_params)

            else:
                print('dejar el mismo container')
            time.sleep(5)


        except Exception as e:
            print(e)
            time.sleep(5)


@task
def up_docker(c, server_params):
    
    print('se ha creado container')





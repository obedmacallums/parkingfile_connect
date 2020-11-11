import getpass
from invoke import Collection, task, Config
import requests
import time
import docker
import configparser

client = docker.from_env()



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
    public_key, private_key =  make_ssh_keys(c)

    config['DEFAULT'] = {'sudo_password': sudo_password, 
                        'parkingfile_username':parkingfile_username,
                        'parkingfile_token':parkingfile_token}
    config['AGENT'] = {'public_key_agent': public_key}
    with open('configfile', 'w') as configfile:
        config.write(configfile)
    
    
        

    build_image(c, private_key)
    server_request(c)


@task   
def make_ssh_keys(c):
    #c.sudo('sudo ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa -N ""')
    public_key = c.sudo('cat /root/.ssh/id_rsa.pub').stdout
    private_key = c.sudo('cat /root/.ssh/id_rsa').stdout
    return public_key, private_key

    
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
def build_image(c, private_key):
    with open("id_rsa", "w") as file1: 
        file1.write(private_key)

    try:

        client.images.build(path=".", tag='ssh_reverse')
        c.sudo('rm id_rsa')
        return True
        
    except Exception as e:
            print(e)
            return False

@task
def up_docker(c, server_params):
    
    try:
        obj_container = client.containers.get('ssh_reverse')
        obj_container.stop()
        obj_container.remove()
        client.containers.run(
            image='ssh_reverse',
            detach=True,
            network_mode='host',
            restart_policy={"Name":"always"},
            name="ssh_reverse",
            command='ssh -o StrictHostKeyChecking=no -N -i id_rsa -R 8080:localhost:22 ubuntu@3.138.223.39'
            )
    except Exception as e:
        print(e)
        client.containers.run(
            image='ssh_reverse',
            detach=True,
            network_mode='host',
            restart_policy={"Name":"always"},
            name="ssh_reverse",
            command='ssh -o StrictHostKeyChecking=no -N -i id_rsa -R 8080:localhost:22 ubuntu@3.138.223.39'
            )
 





import json
import requests
from enum import Enum


class Health(Enum):
    unknown = 0
    ok = 1
    conn_err = 2
    bad_status = 3
    bad_protocol = 4

# cool trick found here:
# http://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__HEALTH__": str(obj)}
        return json.JSONEncoder.default(self, obj)
        

def as_enum(d):
    if "__HEALTH__" in d:
        name, member = d["__HEALTH__"].split(".")
        return getattr(globals()[name], member)
    else:
        return d


def create_default_conf():
    conf = {
        'gpredict_home': '~/gpredict',
        'mccs': [
            {
                'api_root': 'https://coolmcc.at/api/',
                'health': Health.unknown,
                'skip': True
            },
            {
                'api_root': 'https://supermcc.com/',
                'health': Health.ok,
                'skip': False
            },
            {
                'api_root': 'https://grandmcc.edu.uk/',
                'health': Health.conn_err,
                'skip': True
            }
        ]
    }

    with open('bridgeconf.json', 'w') as f:
        json.dump(conf, f, cls=EnumEncoder, indent=4)
    
    return conf


def read_config():
    try:
        with open('bridgeconf.json', 'r') as f:
            return json.load(f, object_hook=as_enum)
    except FileNotFoundError:
        print('No config found - creating new one')
        return create_default_conf()


def check_server_health(config=None):
    if config is None:
        config = read_config()
    
    for mcc in config['mccs']:
        print(mcc['api_root'])
        if mcc['skip']:
            print('Skipped')
            continue
        try:
            r = requests.get(mcc['api_root'])
            if r.status_code == 200:
                mcc['health'] = Health.ok
            else:
                mcc['health'] = Health.bad_status
        except ConnectionError:
            mcc['health'] = Health.conn_err
        except:
            mcc['health'] = Health.unknown
        finally:
            print("Health: {}".format(mcc['health']))
        
    
#    r = requests.get("{}api".format(config['mcc_roots'][0]))


def main():
    print('Utility initialized as a script!')


if __name__ == '__main__':
    main()
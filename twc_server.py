
from sanic import Sanic, response
import subprocess
import pdb
import os
import random
import time
import json
import socket


# Create the http server app
server = Sanic("test_upload")


API_NOTIFY_SERVER="https://www.taskswithcode.com/api_stats/"
APP_NAME = "twc/salient_object_detection"


def init_seed():
    random.seed(time.time_ns) 

init_seed()


# Healthchecks verify that the environment is correct on Banana Serverless
@server.route('/check', methods=["GET"])
def healthcheck(request):
    return response.json({"ip_address": request.ip,"status":"okay"})

def notify_api_usage(ip_address,user_agent):
    try:
        sys_call = f"./twc_notify_use.sh {ip_address} {user_agent} {APP_NAME} POST {API_NOTIFY_SERVER}"
        ret_code = os.system(sys_call)
        print(f"API use ret code:{ret_code}")
    except Exception as e:
        print(f"Failed connect to API notify server. Exception:{e.args[0]}")

valid_masks = ["blur","green","rgba","map"]

@server.route('/', methods=["POST"]) 
async def inference(request):
    test_file = request.files.get('test')
    mask_type = request.form.get("mask")
    if (mask_type is not None):
        mask_type = mask_type.lower()
    if (mask_type is None or mask_type not in valid_masks):
        mask_type = "green"
        print(f"Invalid mask type. Mapping to {mask_type}")
    file_parameters = {
        'body': len(test_file.body),
        'name': test_file.name,
        'type': test_file.type,
    }

    temp_file_name = f"{random.randint(0,10000)}_{time.time_ns()}_{test_file.name.split('/')[-1]}"
    output_dir = "output"
    in_file  = f"input/{temp_file_name}"
    out_file  = f"{output_dir}/{temp_file_name.split('.')[-2]}.png"
    #hostname = socket.gethostname()
    #ip_address = socket.gethostbyname(hostname)
    print(in_file,out_file,mask_type,request.ip,request.headers['user-agent'])
    content_type = "image/png"
    with open(in_file,"wb") as fp:
        fp.write(test_file.body)

    sys_call = f"python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source {in_file}  --dest {output_dir} --type {mask_type}  --verbose"
    ret_code = os.system(sys_call)
    print(f"Ret code:{ret_code}")
    if (ret_code == 0):
        with open(f"{out_file}","rb") as fp:
            data = fp.read()
            print(f"Created file of size {len(data)}")
    else:
            data = {"desc": "Request failed","code":ret_code}
            data = json.dumps(data)
            content_type = "text/json"
    os.remove(in_file)
    os.remove(out_file)
    notify_api_usage(request.ip,request.headers['user-agent'])

    print("Processed response")
    return response.HTTPResponse(body=data,content_type=content_type)
    #return response.HTTPResponse(body=test_file.body,content_type=test_file.type)
    #return response.ResponseStream(streaming_fn, content_type='text/plain')
    #return response.json({ "received": True, "test_file_parameters": file_parameters })
#    print(request.files.keys())
    #return response.json({ "received": True, "file_names": request.files.keys()})
#    return response.json({"ip_address": request.ip,"status":"okay"})

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=9001, workers=1)

# coding=utf-8

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models

from TaskReader import TaskReader

import os
import base64
import json

class ASRRunner(object):
    def __init__(self, dir_path, folder_name):
        super().__init__()
        self.dir_path = dir_path
        self.folder_name = folder_name

    def run(self):
        # Get all files under folder
        file_path = os.path.join(self.dir_path, self.folder_name)
        for file_name in os.listdir(file_path):
            if os.path.isdir(os.path.join(file_path, file_name)):
                continue
            print("Start Handle" + file_name)
            self.process_file(file_name, file_path)

    # process a single file
    def process_file(self, file_name, file_path):
        try:
            # encode audio to base64 format string
            file = open(os.path.join(file_path, file_name), 'rb+')
            sound_wav_rb = file.read()
            file.close()
            encodestr = base64.b64encode(sound_wav_rb).decode()

            # set up request params
            # https://cloud.tencent.com/document/api/1093/37823
            secret_id =  os.environ.get("TENCENTCLOUD_SECRET_ID")
            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY")

            cred = credential.Credential(
                secret_id,
                secret_key)

            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            clientProfile.signMethod = "TC3-HMAC-SHA256"
            client = asr_client.AsrClient(cred, "ap-shanghai", clientProfile)

            req = models.CreateRecTaskRequest()
            params = {
                "EngineModelType":"8k_zh",
                "ChannelNum":1,
                "ResTextFormat":0,
                "SourceType":1,
                "Data": encodestr
                }
            req._deserialize(params)

            # send request and get response json
            resp = client.CreateRecTask(req)
            resp_json_str = resp.to_json_string()

            resp_json = json.loads(resp_json_str)
            if resp_json["Data"]["TaskId"]:
                task_id = resp_json["Data"]["TaskId"]
                output_file_name = file_name.split(".")[0] + '.txt'
                output_folder = os.path.join(file_path, "result")
                output_file_path = os.path.join(output_folder, output_file_name)

                # use response json(TaskId) to retrieve final text file
                task_reader = TaskReader(secret_id, secret_key, task_id, output_file_path)
                task_reader.run()

        except TencentCloudSDKException as err:
            print(file_name, err)

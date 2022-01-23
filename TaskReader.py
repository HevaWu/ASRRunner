# coding=utf-8

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models

import json
import os
import time

class TaskReader(object):
    def __init__(self, secret_id, secret_key, task_id, output_path):
        super().__init__()
        self.output_path = output_path
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.task_id = task_id

    def run(self):
        try:
            # setup request params
            # https://cloud.tencent.com/document/api/1093/37822
            cred = credential.Credential(
                self.secret_id,
                self.secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = asr_client.AsrClient(cred, "ap-shanghai", clientProfile)

            # send request and get response json
            req = models.DescribeTaskStatusRequest()
            params = '{"TaskId":' + str(self.task_id) +'}'
            req.from_json_string(params)

            # read result, since process time might be long
            # here is keep watching "status" to be sure the process is finished
            # status code: https://cloud.tencent.com/document/api/1093/37824#TaskStatus
            resp_status = 0
            while resp_status != 2 and resp_status != 3:
                time.sleep(20)
                print("Under Handling ", self.task_id, resp_status)
                resp = client.DescribeTaskStatus(req)
                resp_json_str = resp.to_json_string()
                resp_json = json.loads(resp_json_str)
                resp_status = resp_json["Data"]["Status"]

            # retrieve successful parsed text
            # save it to new file
            if resp_status == 2 and resp_json["Data"]["Result"]:
                resp_data = resp_json["Data"]["Result"]
                with open(self.output_path, 'w') as f:
                    f.write(resp_data)
                print("Finish " + self.output_path)
            else:
                print("Error: cannot find json data for " + self.output_path)
                print(resp_json)

        except TencentCloudSDKException as err:
            print(self.output_path, self.task_id)
            print(err)


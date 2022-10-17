import json
from random import sample
import string
import subprocess
import boto3
import os

"""
input 
acountid:string (required)
s3_path:string (required)
cluster_name:string (required)
"""

# Notes :
# the lambda running time out need to greater than 1min.
# the memory need  to at least 1024M.
# need add a sts Role and give resource policy
# inside the image  make dir "/home/sbx_user1051/.parellecluster/" in advance


def lambda_handler(event, context):
    # thread_id = threading.get_ident()
    # print("thread_id is " + str(thread_id))
    print(event)
    method, bucketName, file_name, file_path, body = "", "", "", "", ""
    cluster_name, account_id, s3_path, region = "", "", "", ""
    response = ""

    try:
        tmp = event["body"].replace("\n", "").replace(" ", "").replace("\r", "")
        body = eval(tmp)
        method = event["httpMethod"]
        account_id = body["account_id"]
        cluster_name = body["cluster_name"]
        region = body["region"]
        s3_path = body["s3_path"]
    except Exception as e:
        return {
            "statusCode": 403,
            "body": json.dumps(
                'input data format is not correct. account_id,s3_path,cluster_name,region are required.\n \
                and their format shoud like \{ "account_id": "123456789012", "s3_path": "s3://{busket name}{object name}", \n "cluster_name": "testpcluster1", "region":"us-east-2" }'
            ),
        }

    # valid input need to add.
    if cluster_name == "" or region == "" or account_id == "" or s3_path == "":
        print(
            "account_id={0}\ns3_path={1}\ncluster_name={2}\nregion={3}\n".format(
                account_id, s3_path, cluster_name, region
            )
        )
        return {
            "statusCode": 403,
            "body": json.dumps(
                "account_id, s3_path, cluster_name and region are required."
            ),
        }

    # assumeRole get credencial， here need to add premission to perform sts.assumleRole on resource RoleArn.
    stsclient = boto3.client("sts")
    assumedRoleObject = stsclient.assume_role(
        RoleArn="arn:aws:iam::" + account_id + ":role/OrganizationAccountAccessRole",
        RoleSessionName="RoleSessionName",
    )

    credentials = assumedRoleObject["Credentials"]
    # print(credentials)

    # conments
    # environ credencial priority is higher than credencial file.
    # lambda envirment don't have local credencial, here we write the credencial envirment varables.
    cur_env = os.environ.copy()
    cur_env["AWS_ACCESS_KEY_ID"] = credentials["AccessKeyId"]
    cur_env["AWS_SECRET_ACCESS_KEY"] = credentials["SecretAccessKey"]
    cur_env["AWS_SESSION_TOKEN"] = credentials["SessionToken"]

    s3 = boto3.client('s3')

    if method == "POST":
        strarray = s3_path.split("/")
        bucketName = strarray[2]
        file_name = strarray[-1]
        len_strarray = len(strarray)
        obj_name = ""
        for i in range(3, len_strarray):
            obj_name += "/" + strarray[i]
        obj_name = obj_name[1:]

        random_name = "".join(sample(string.ascii_letters + string.digits, 8))
        file_path = "/tmp/{0}_{1}_{2}".format(account_id, random_name, file_name)
        print("s3 config file is saved at {0}".format(file_path))
        print("obj_name is {0}".format(obj_name))
        # download file from s3
        try:
            s3.download_file(bucketName, obj_name, file_path)
            print(
                "bucketName is {0}\n file_name is {1} \n file_path is {2}\n".format(
                    bucketName, obj_name, file_path
                )
            )
        except Exception as e:
            print("download file error.")
            print(e)
            return {"statusCode": 403, "body": json.dumps("download file error.")}

        command = (
            "pcluster create-cluster --cluster-name "
            + cluster_name
            + " --cluster-configuration "
            + file_path
        )
        command = command.split(" ")
        try:
            sub = subprocess.Popen(
                command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=cur_env
            )
            response = sub.stdout.read()
            sub.communicate()

        except Exception as e:
            print("some error happend {0}".format(e))
        finally:
            command = "rm " + file_path
            sub = os.system(command)
            command = "ls /tmp/"
            sub = os.system(command)
            print("config file has been deleted.")
            return {
                "statusCode": 200,
                # create or delete cluster_name at region + account_id.
                "body": response,
            }

    elif method == "DELETE":
        command = (
            "pcluster delete-cluster --cluster-name "
            + cluster_name
            + " --region "
            + region
        )
        command = command.split(" ")
        try:
            sub = subprocess.Popen(
                command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=cur_env
            )
            response = sub.stdout.read()
            sub.communicate()
        except Exception as e:
            print("some error happend {0}".format(e))
        finally:
            return {
                "statusCode": 201,
                # create or delete cluster_name at region + account_id.
                "body": response,
            }

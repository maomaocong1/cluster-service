# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template


need   to install docker.io

sudo apt install docker.io


if docker logging permission denied , running the following command

sudo newgroup docker
sudo chmod 666 /var/run/docker.sock
sudo usermod -aG docker ${USER}


data body input format
{ "accountid": "123456789012", "s3_path": "s3://{busket name}{object name}", "cluster_name": "testpcluster1", "region":"us-east-2" }

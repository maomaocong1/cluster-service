import * as cdk from 'aws-cdk-lib';
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as lambda from "aws-cdk-lib/aws-lambda";
//import * as s3 from "aws-cdk-lib/aws-s3";
import * as iam from "aws-cdk-lib/aws-iam";
import * as path from 'path';



import { Construct } from 'constructs';
import { Duration } from 'aws-cdk-lib';
import { PolicyStatement } from 'aws-cdk-lib/aws-iam';

export class ClusterServiceTypescriptStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const handler = new lambda.DockerImageFunction(this, 'AssetFunction', {
      memorySize: 1024,
      timeout: Duration.seconds(60),
      code: lambda.DockerImageCode.fromImageAsset(

        path.join(__dirname, '../lib/applications/cluster-service/'),
        {
          entrypoint: ["/lambda-entrypoint.sh"],
        },

      ),


    });
    //const bucket = s3.Bucket.fromBucketName(this, 'Bucket', 'clusterservice');
    //bucket.grantReadWrite(handler);//???
    const cluster_webservice_api = new apigateway.RestApi(this, "cluster service API", {
      restApiName: "cluster service API",
    });
    const createClusterIntegration = new apigateway.LambdaIntegration(handler);
    cluster_webservice_api.root.addMethod("POST", createClusterIntegration);
    cluster_webservice_api.root.addMethod("DELETE", createClusterIntegration);
    const stsRole_policy = new PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'sts:AssumeRole'
      ],
      resources: [
        'arn:aws:iam::*:role/OrganizationAccountAccessRole'
      ],
    }
    );

   

    const userBucketsPolicyStatement = new PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ["s3:Get*",
      "s3:List*",
      "s3-object-lambda:Get*",
      "s3-object-lambda:List*"],
      resources: ["arn:aws:s3:::*"],
    });

   
    handler.addToRolePolicy(stsRole_policy);
    handler.addToRolePolicy(userBucketsPolicyStatement);

  }
}

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_s3_deployment as s3deploy,
    aws_cloudfront_origins as origins
)
from constructs import Construct


class FrontendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # =========================
        # 1. S3 Bucket
        # =========================
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            website_index_document="index.html",
            public_read_access=False,   # safer
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # =========================
        # 2. CloudFront Distribution
        # =========================
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(frontend_bucket)
            ),
            default_root_object="index.html"
        )

        # =========================
        # 3. Upload Frontend Files
        # =========================
        s3deploy.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[s3deploy.Source.asset("../../frontend")],
            destination_bucket=frontend_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # Output a public URL
        self.cloudfront_url = distribution.distribution_domain_name
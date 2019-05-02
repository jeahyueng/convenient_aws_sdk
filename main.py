from aws import AWSCredential
from aws.services import EC2
from aws.services import S3


def main():
    credential = AWSCredential(
        aws_access_key_id='Access_Key',
        aws_secret_access_key='Secret_Key',
        region_name='Region'
    )

    ec2 = EC2(credential)
    s3 = S3(credential, 'Bucket_Name')


if __name__ == '__main__':
    main()
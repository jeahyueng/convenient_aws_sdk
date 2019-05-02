import boto3


class AWSCredential(object):
    # AWS credential 을 관리하는 class
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.__region_name = region_name

    @property
    def region_name(self):
        return self.__region_name

    @region_name.setter
    def region_name(self, new_region_name):
        # region 을 중간에 변경할때
        self.__region_name = new_region_name


class AWSObject(object):
    def __init__(self, credential):
        self.client = (credential)
        self.resource = (credential)

    @property
    def client(self):
        return self.__client

    @client.setter
    def client(self, new_credential):
        self.region_name = new_credential.region_name
        self.__client = boto3.client(
            self.service_name,
            aws_access_key_id=new_credential.aws_access_key_id,
            aws_secret_access_key=new_credential.aws_secret_access_key,
            region_name=new_credential.region_name
        )

    @property
    def resource(self):
        return self.__resource

    @resource.setter
    def resource(self, new_credential):
        self.region_name = new_credential.region_name
        self.__resource = boto3.resource(
            self.service_name,
            aws_access_key_id=new_credential.aws_access_key_id,
            aws_secret_access_key=new_credential.aws_secret_access_key,
            region_name=new_credential.region_name
        )


from aws import AWSObject
from aws.parsers import Instance
from aws.parsers import ReservedInstances
from aws.parsers import NetDetail
from aws.parsers import EIP


class EC2(AWSObject):
    service_name = 'ec2'

    def get_instances(self, running_only=False):
        '''
        모든 인스턴스 정보를 가져옵니다.
        :param running_only: 실행/정지
        :return: 인스턴스 정보
        '''

        Filters = [{'Name': 'instance-state-name', 'Values': ['running']}] if running_only else []
        for reservations in self.client.describe_instances(Filters=Filters)['Reservations']:
            for instance in reservations['Instances']:
                yield Instance(instance)
    
    def reserved_instances(self, active_only=False):
        '''
        예약 인스턴스 정보를 가져옵니다.
        :param active_only: 활성/비활성
        :return: 예약 인스턴스 정보
        '''

        Filters = [{'Name': 'state', 'Values': ['active']}] if active_only else []
        return [ReservedInstances(instance, self.region_name) 
                for instance in self.client.describe_reserved_instances(Filters=Filters)['ReservedInstances']]
    
    def get_net_ids(self, id):
        '''
        고정 아이피에 할당된 ID 정보를 가져옵니다.
        :param id: 네트워크 인터페이스 ID 값
        :return: 고정 아이피 할당 ID, 고정 아이피 연결 ID
        '''
        yield from [NetDetail(interface) for interface in self.resource.NetworkInterface(id).private_ip_addresses]

    def get_elastic_ips(self, disabled_only=False):
        '''
        모든 고정 아이피 정보를 가져옵니다.
        :param disabled_only: 활성화/비활성화
        :return: 고정 아이피 리스트
        '''
        elastic_ips = []
        for ip in self.client.describe_addresses()['Addresses']:
            if 'NetworkInterfaceId' in ip.keys() and disabled_only:
                continue

            elastic_ips.append(EIP(ip))

        return elastic_ips

    def disable_elastic_ip(self, id):
        '''
        고정 아이피 연결을 해제합니다.
        :param id: 고정 아이피 연결 ID
        :return: 성공/실패
        '''
        response = self.client.disassociate_address(
            AssociationId=id
        )

        return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

    def delete_elastic_ip(self, id):
        '''
        고정 아이피를 제거 합니다.
        :param id: 고정 아이피 할당 ID
        :return: 성공/실패
        '''
        response = self.client.release_address(
            AllocationId=id
        )

        return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

    def create_elastic_ip(self):
        '''
        고정 아이피를 생성 합니다.
        :return: Elastic IP, 고정아이피 할당 ID
        '''
        allocation = self.client.allocate_address(Domain='vpc')

        return EIP(allocation)

    def enable_elastic_ip(self, net_id, association_id, private_ip):
        '''
        고정 아이피를 연결 합니다.
        :param net_id: 네트워크 인터페이스 ID 값
        :param association_id: 고정 아이피 할당 ID
        :param private_ip: 내부 프라이빗 IP
        :return: 성공/실패
        '''
        response = self.client.associate_address(
            AllocationId=association_id,
            NetworkInterfaceId=net_id,
            PrivateIpAddress=private_ip
        )

        return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

    def create_private_ip(self, count, net_id):
        '''
        내부 프라이빗 IP를 생성합니다.
        :param count: 생성할 갯수
        :param net_id: 네트워크 인터페이스 ID 값
        :return: 성공/실패
        '''
        network_interface = self.resource.NetworkInterface(net_id)

        response = network_interface.assign_private_ip_addresses(
            SecondaryPrivateIpAddressCount=count
        )

        return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False


class S3(AWSObject):
    service_name = 's3'

    def __init__(self, credential, bucket):
        super().__init__(credential)
        self.__bucket = bucket

    @property
    def bucket(self):
        return self.__bucket

    @bucket.setter
    def bucket(self, new_bucket):
        self.__bucket = new_bucket

    def upload(self, src, dst):
        '''
        S3 파일 업로드
        :param src: 로컬 파일 경로
        :param dst: S3 파일 경로
        :return: None
        '''
        self.client.upload_file(src, self.__bucket, dst)

    def put(self, data, dst):
        '''
        파일 저장 없이 S3 다이렉트 업로드
        :param data: 업로드 데이터
        :param dst: S3 파일 경로
        :return: None
        '''
        self.client.put_object(Bucket=self.__bucket, Body=data, Key=dst)

    def get(self, src):
        '''
        S3 파일 읽기
        :param src: S3 파일 경로
        :return: S3 파일 데이터
        '''
        try:
            obj = self.resource.Object(self.__bucket, src)
            data = obj.get()['Body'].read()
            return data
        except:
            return None

    def download(self, src, dst):
        '''
        S3 파일 다운로드
        :param src: 로컬 다운로드 경로
        :param dst: S3 파일 경로
        :return: None
        '''
        data = self.get(dst)
        if data is None:
            return False
        
        with open(src, 'wb') as f:
            f.write(data)
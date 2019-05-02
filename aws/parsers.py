from collections import namedtuple
from datetime import datetime


class Instance(object):
    def __init__(self, instance):
        self.__ebs = namedtuple('Disk', 'name attach_time volume_id')
        self.__net_info = namedtuple('Network', 'id private public')
        self.__net_conn = namedtuple('NetworkInfo', 'ip dnsname ')

        self.__id = instance['InstanceId']
        self.__name = self._name(instance['Tags'])
        self.__type = instance['InstanceType']
        self.__image_id = instance['ImageId']
        self.__region = instance['Placement']['AvailabilityZone']
        self.__launch_time = instance['LaunchTime']
        self.__state = instance['State']['Name']
        self.__key_pair = instance['KeyName']
        self.__vpc_id = instance['VpcId']
        self.__disk = self._disk(instance['BlockDeviceMappings'])
        self.__network = self._network(instance['NetworkInterfaces'])


    def _name(self, tags):
        for tag in tags:
            if tag['Key'] == 'Name':
                return tag['Value']
            else:
                continue

        return None

    def _disk(self, disks):
        return [
            self.__ebs(
                name=disk['DeviceName'],
                attach_time=disk['Ebs']['AttachTime'],
                volume_id=disk['Ebs']['VolumeId']
            ) for disk in disks
        ]

    def _network(self, interfaces):
        networks = []

        for interface in interfaces:
            for net in interface['PrivateIpAddresses']:
                try:
                    networks.append(self.__net_info(
                        id=interface['NetworkInterfaceId'],

                        private=self.__net_conn(
                            ip=net['PrivateIpAddress'],
                            dnsname=net['PrivateDnsName']
                        ),

                        public=self.__net_conn(
                            ip=net['Association']['PublicIp'],
                            dnsname=net['Association']['PublicDnsName']
                        )
                    ))
                except KeyError:
                    continue

        return networks

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def image_id(self):
        return self.__image_id

    @property
    def region(self):
        return self.__region

    @property
    def launch_time(self):
        return self.__launch_time

    @property
    def state(self):
        return self.__state

    @property
    def key_pair(self):
        return self.__key_pair

    @property
    def vpc_id(self):
        return self.__vpc_id

    @property
    def disk(self):
        return self.__disk

    @property
    def network(self):
        return self.__network


class ReservedInstances(object):
    def __init__(self, instance, region):
        self.__id = instance['ReservedInstancesId']
        self.__start_time = instance['Start']
        self.__expire_time = instance['End']
        self.__count = instance['InstanceCount']
        self.__type = instance['InstanceType']
        self.__description = instance['ProductDescription']
        self.__state = instance['State']
        self.__duration = instance['Duration']
        self.__region = region

    @property
    def id(self):
        return self.__id

    @property
    def start_time(self):
        return self.__start_time

    @property
    def expire_time(self):
        return self.__expire_time

    @property
    def count(self):
        return self.__count

    @property
    def type(self):
        return self.__type

    @property
    def description(self):
        return self.__description

    @property
    def state(self):
        return self.__state

    @property
    def duration(self):
        return self.__duration

    @property
    def remain_time(self):
        return self.__expire_time.replace(tzinfo=None) - datetime.utcnow()

    @property
    def region_name(self):
        return self.__region


class NetDetail(object):
    def __init__(self, detail):
        self.__detail = detail

    @property
    def association_id(self):
        try:
            return self.__detail['Association']['AssociationId']
        except IndexError:
            return None

    @property
    def allocation_id(self):
        try:
            return self.__detail['Association']['AllocationId']
        except IndexError:
            return None

class EIP(object):
    def __init__(self, eip):
        self.__eip = eip

    @property
    def public_ip(self):
        return self.__eip['PublicIp']

    @property
    def allocation_id(self):
        return self.__eip['AllocationId']
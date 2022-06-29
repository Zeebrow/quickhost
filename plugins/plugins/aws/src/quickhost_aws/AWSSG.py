from typing import List, Union
from dataclasses import dataclass
import logging
import json

import botocore.exceptions

from .constants import *
from .utilities import QH_Tag
from .temp_data_collector import store_test_data


logger = logging.getLogger(__name__)

class AWSPort:
    """This will be fun"""
    pass

class SG:
    def __init__(self, client: any, app_name: str, vpc_id: str, ports: List[int], cidrs: List[str], dry_run: bool):
        self.client = client
        self.app_name = app_name
        self.vpc_id = vpc_id
        self.ports = None
        self.cidrs = None
        self.dry_run = dry_run
        self.sgid = None

    def get_security_group(self):
        _dsg = None
        try:
            _dsg = self.client.describe_security_groups(
                GroupNames=[self.app_name],
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [ self.vpc_id, ]
                    },
                ],
            )
        except botocore.exceptions.ClientError:
            return None
        if len(_dsg['SecurityGroups']) > 1:
            raise RuntimeError(f"More than 1 security group was found with the name '{self.app_name}': {_sg['GroupId'] for _sg in _dsg['SecurityGroups']}")
        #store_test_data(resource='SG', action='describe', response_data=_dsg)
        return _dsg['SecurityGroups'][0]['GroupId']

    def create(self, cidrs, ports):
        print('creating sg...', end='')
        _sg = self.client.create_security_group(
            Description="Made by quickhost",
            GroupName=self.app_name,
            VpcId=self.vpc_id,
            TagSpecifications=[{ 'ResourceType': 'security-group',
                'Tags': [
                    { 'Key': 'Name', 'Value': self.app_name },
                    QH_Tag
            ]}],
            DryRun=self.dry_run
        )
        print(f"done ({_sg['GroupId']})")
        self.sgid = _sg['GroupId']
        self._add_ingress(cidrs, ports)
        #store_test_data(resource='SG', action='create', response_data=_sg)
        return _sg['GroupId']

    def delete(self):
        #store_test_data(resource='SG', action='create', response_data=_sg)

        pass

    def _add_ingress(self, cidrs, ports):
        print('adding sg ingress...', end='')
        perms = []
        for port in ports:
            perms.append({
                'FromPort': int(port),
                'IpProtocol': 'tcp',
                'IpRanges': [ { 'CidrIp': cidr, 'Description': 'made with quickhosts' } for cidr in cidrs ],
                'ToPort': int(port),
            })
        response = self.client.authorize_security_group_ingress(
            GroupId=self.sgid,
            IpPermissions=perms,
            DryRun=self.dry_run,
        )
        print(f"done ({[i for i in self.cidrs]}:{[p for p in self.ports]})")
        #store_test_data(resource='SG', action='_add_ingress', response_data=response)

    def describe(self):
        response = None
        self.ports = []
        self.cirds = []
        try:
            response = self.client.describe_security_groups(
                GroupNames=[self.app_name],
                Filters=[
                    { 'Name': 'vpc-id', 'Values': [ self.vpc_id, ] },
                ],
            )
            self.sgid = response['SecurityGroups'][0]['GroupId']
            ec2 = boto3.resource('ec2')
            sg = ec2.SecutiryGroup()
            for p in response['SecurityGroups'][0]['IpPermissions']:
                if p['ToPort'] == p['FromPort']:
                    self.ports.append("{}/{}".format(
                        p['ToPort'],
                        p['IpProtocol']
                    ))
                else:
                    self.ports.append("{0}/{2}-{1}/{2}".format(
                        p['ToPort'],
                        p['FromPort'],
                        p['IpProtocol']
                    ))

        except botocore.exceptions.ClientError as e:
            if 'InvalidGroup.NotFound' in e.response:
                self.sgid = None
                logger.error(f"No security group found for app '{self.app_name}' (does the app exist?)")
        print(json.dumps(response, indent=2))
        exit(2)
        return response

if __name__ == '__main__':
    import boto3
    import json
    try:
        from .utilities import get_my_public_ip
    except:
        from utilities import get_my_public_ip

    client = boto3.client('ec2')
    sg = SG(
        client=client,
        app_name='test-sg',
        vpc_id='vpc-7c31a606',
        ports=['22'],
        cidrs=[f"{get_my_public_ip()}/32"],
        dry_run=False
    )
    print(json.dumps(sg.describe(), indent=2))
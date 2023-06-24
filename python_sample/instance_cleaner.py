import boto3

TERMINATABLE_STATES = ['pending', 'running', 'stopping', 'stopped']

class InstanceCleaner(object):
    def __init__(self) -> None:
        self.client = self.create_client()

    @staticmethod
    def create_client() -> boto3.client:
        return boto3.client('ec2', region_name='us-west-2')

    def terminate_instances(self) -> None:
        instances = self.client.describe_instances(
            Filters=[{
                'Name': 'instance-state-name',
                'Values': TERMINATABLE_STATES,
            }]
        )
        instance_list = []
        if not instances['Reservations']:
            return False

        for instance in instances['Reservations'][0]['Instances']:
            instance_list.append(instance['InstanceId'])

        if instance_list:
            self.client.terminate_instances(InstanceIds=instance_list)

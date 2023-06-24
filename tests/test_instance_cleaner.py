import pytest

from python_sample.instance_cleaner import InstanceCleaner, TERMINATABLE_STATES
from botocore.stub import Stubber

INSTANCE_CODE_MAPPING = {
    'pending': 0,
    'running': 16,
    'shutting-down': 32,
    'terminated': 48,
    'stopping': 64,
    'stopped': 80
}
INSTANCE_ID = 'i-1234567890abcdef0'

test_data = [(x, True) for x in INSTANCE_CODE_MAPPING.keys() if x != 'terminated' and x != 'shutting-down']
test_data.append(('shutting-down', False))
test_data.append(('terminated', False))

def generate_instance_response(code_name: str) -> dict:
    return {
        'Reservations': [
            {
                'Instances': [
                    {
                        'InstanceId': INSTANCE_ID,
                        'State': {
                            'Code': INSTANCE_CODE_MAPPING[code_name],
                            'Name': code_name
                        }
                    },
                ],
            }
        ]
    }

def generate_termination_response(code_name: str) -> dict:
    return {
        'TerminatingInstances': [
            {
                'CurrentState': {
                    'Code': 32,
                    'Name': 'shutting-down'
                },
                'InstanceId': INSTANCE_ID,
                'PreviousState': {
                    'Code': INSTANCE_CODE_MAPPING[code_name],
                    'Name': code_name,
                },
            },
        ]
    }

@pytest.mark.parametrize('code_name,should_terminate', test_data)
def test_instance_cleanup(code_name, should_terminate) -> None:
    instance_cleanup = InstanceCleaner()
    with Stubber(instance_cleanup.client) as stubber:
        if should_terminate:
            stubber.add_response('describe_instances', generate_instance_response(code_name), {'Filters':[{'Name': 'instance-state-name', 'Values': TERMINATABLE_STATES }]})
            stubber.add_response('terminate_instances', generate_termination_response(code_name), {'InstanceIds': [INSTANCE_ID]})
        else:
            stubber.add_response('describe_instances', {'Reservations': [{'Instances': []}]}, {'Filters':[{'Name': 'instance-state-name', 'Values': TERMINATABLE_STATES }]})
        instance_cleanup.terminate_instances()

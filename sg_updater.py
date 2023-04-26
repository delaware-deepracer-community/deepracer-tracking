from config import settings
import boto3
from cwatch_logging import CWatch_logging as cwl
import traceback

def sgupdate():
    sg_id = settings.SG_ID
    pl_id = settings.PL_ID
    ingress_count = 0
    egress_count = 0
    cwlog = cwl()
    
    cwlog.send_log('SG: Checking Default Security Group')
    try:
        client = boto3.client('ec2', region_name='us-east-1')
        sg_rules = client.describe_security_group_rules(Filters=[{"Name": "group-id", "Values": [sg_id]}])
        for rule in sg_rules['SecurityGroupRules']:
            if rule['IsEgress']:
                egress_count += 1
            else:
                ingress_count += 1
                
        if ingress_count == 0:
            print("Updating Ingress")
            cwlog.send_log('SG: Updating Inbound rule')
            client.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[
                        {"FromPort": 0,
                        "IpProtocol": "tcp",
                        "PrefixListIds":
                            [
                                {"PrefixListId": pl_id}
                            ],"ToPort": 65535
                        }
                    ])
        if egress_count == 0:
            print("Updating Egress")
            cwlog.send_log('SG: Updating Outbound rule')
            client.authorize_security_group_egress(
                    GroupId=sg_id,
                    IpPermissions=[
                        {"FromPort": 0,
                        "IpProtocol": "tcp",
                        "PrefixListIds":
                            [
                                {"PrefixListId": pl_id}
                            ],"ToPort": 65535
                        }
                    ])
    except Exception as ex:
        print(ex)
        cwlog.send_log(f'SG: Encountered exception: {ex}')
        cwlog.send_log(f'SG: Exception Stacktrace: {traceback.extract_stack()}')
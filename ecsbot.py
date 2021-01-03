import discord, asyncio, os, boto3, socket, traceback

client = discord.Client()

ecs = boto3.client('ecs')
waiter = ecs.get_waiter('services_stable')

def get_cluster():
    return next(item for item in ecs.list_clusters()['clusterArns'] if 'minebot' in item)

def get_service(guild, cluster=get_cluster()):
    # find first cluster name containing 'minebot' (should only be one)
    services = ecs.describe_services(cluster=cluster, 
                                     services=ecs.list_services(cluster=cluster)['serviceArns'], 
                                     include=['TAGS'])['services']
    if (len(services) == 0):
        return None
    else:
        return next((item for item in services if (is_for_guild(item, guild))), None)

def is_for_guild(service, guild):
    tag = next((item for item in service['tags'] if item['key'] == 'guild'), None)
    return (tag != None and tag['value'] == guild)

def start_service(service):
    ecs.update_service(cluster=service['clusterArn'],
                       service=service['serviceArn'],
                       desiredCount=1)

def stop_service(service):
    ecs.update_service(cluster=service['clusterArn'],
                       service=service['serviceArn'],
                       desiredCount=0)

def get_tasks(service):
    tasks = ecs.list_tasks(cluster=service['clusterArn'], serviceName=service['serviceName'])['taskArns']
    if tasks == None or len(tasks) == 0:
        return []
    else:
        return ecs.describe_tasks(cluster=service['clusterArn'], tasks=tasks)['tasks']

def task_ip(task):
    eni = next((item for item in task['attachments'] if item['type'] == 'ElasticNetworkInterface'), None)
    if (eni == None):
        return None
    eni_id = next((item for item in eni['details'] if item['name'] == 'networkInterfaceId'), None)
    if (eni_id == None):
        return None 
    intf = boto3.resource('ec2').NetworkInterface(eni_id['value'])
    if (intf == None or intf.association_attribute == None):
        return None
    else:
        return intf.association_attribute['PublicIp']

def status(service):
    if (service == None):
        print("Cannot find service")
    else:
        print(f'Found service with {service["runningCount"]} running tasks and {service["desiredCount"]} desired tasks')
        tasks = get_tasks(service)
        if (len(tasks) > 0):
            print(f'Service has {len(tasks)} task, first task accessible at {task_ip(tasks[0])}')

def wait_for_stable(service):
    waiter.wait(cluster=service['clusterArn'], services=[service['serviceArn']], WaiterConfig={'Delay': 5, 'MaxAttempts': 40})
    return

# temporary for testing
guild_id="786042802630950984"

cluster = get_cluster()
service = get_service(guild_id, cluster)
status(service)

import discord, asyncio, os, boto3, socket, traceback

client = discord.Client()
ecs = boto3.client('ecs')

START='start'
STOP='stop'
STATE='state'
BOUNCE='bounce'
INFO='info'
COMMANDS=[START,STOP,STATE,BOUNCE,INFO]
COMMANDS_STR=', '.join(COMMANDS)

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

def print_status(service):
    if (service == None):
        print("Cannot find service")
    else:
        print(f'Found service with {service["runningCount"]} running tasks and {service["desiredCount"]} desired tasks')
        tasks = get_tasks(service)
        if (len(tasks) > 0):
            print(f'Service has {len(tasks)} task, first task accessible at {task_ip(tasks[0])}')

async def wait_until_stable(guild, cluster=get_cluster()):
    state = get_service(guild, cluster)
    while state['runningCount'] != state['desiredCount']:
        await asyncio.sleep(5)
        state = get_service(guild, cluster)
    return

def current_state(service):
    if (service == None):
        return 'Cannot find service'
    else:
        if service['runningCount'] == 1 and service['desiredCount'] == 1:
            return 'Minecraft is running and ready at ' + task_ip(get_tasks(service)[0])
        elif service['runningCount'] == 1 and service['desiredCount'] == 0:
            return 'Minecraft is stopping ...'
        elif service['runningCount'] == 0 and service['desiredCount'] == 1:
            return 'Minecraft is starting ...'
        elif service['runningCount'] == 0 and service['desiredCount'] == 0:
            return 'Minecraft is stopped'
        else:
            return 'FUBAR'

@client.event
async def on_ready():
    print('Logged into discord as')
    print(client.user.name)
    print(client.user.id)
    print('------------')

@client.event
async def on_message(message):
    memberIDs = (member.id for member in message.mentions)
    guild = str(message.channel.guild.id)
    service = get_service(guild)
    if service == None:
        print(f'Unrecognised guild {guild} sent command "{message.content}" from user {client.user.id}')
        return
    elif (client.user.id in memberIDs):
        print(f'Processing message "{message.content}" from user {client.user.id} and guild {guild}')
        if STOP in message.content:
            try:
                stop_service(service)
                await message.channel.send('Minecraft stopping ...')
                await wait_until_stable(guild)
                await message.channel.send(current_state(get_service(guild)))
            except Exception as e:
                print(traceback.format_exc())
                await message.channel.send('Error stopping minecraft: ' + str(e))
        elif START in message.content:
            try:
                start_service(service)
                await message.channel.send('Minecraft starting ...')
                await wait_until_stable(guild)
                await message.channel.send(current_state(get_service(guild)))
            except Exception as e:
                print(traceback.format_exc())
                await message.channel.send('Error starting minecraft: ' + str(e))
        elif STATE in message.content:
            try:
                await message.channel.send(current_state(service))
            except Exception as e:
                print(traceback.format_exc())
                await message.channel.send('Error getting status: ' + str(e))
        elif BOUNCE in message.content:
            try:
                stop_service(service)
                await message.channel.send('Minecraft stopping ...')
                await wait_until_stable(guild)
                start_service(service)
                await message.channel.send('Minecraft starting again...')
                await wait_until_stable(guild)
                await message.channel.send(current_state(get_service(guild)))
            except Exception as e:
                await message.channel.send('Error restarting minecraft:' + str(e))
        elif INFO in message.content:
            await message.channel.send(f'Minecraft server start/stop bot. Commands are {COMMANDS_STR}')
            await message.channel.send(current_state(service))
        else:
            await message.channel.send(f'Unrecognised command. Commands are {COMMANDS_STR}')
        return
    else:
        # do nothing, message not for me
        return

client.run(os.environ['AWSDISCORDTOKEN'])

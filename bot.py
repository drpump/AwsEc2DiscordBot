import discord, asyncio, os, boto3, socket

client = discord.Client()

ec2 = boto3.resource('ec2')
#Temp
instance = ec2.Instance(os.environ['AWSINSTANCEID'])
guild_id = int(os.environ['AWSDISCORDGUILD'])

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------')

@client.event
async def on_message(message):
    memberIDs = (member.id for member in message.mentions)
    if (message.channel.guild.id == guild_id and client.user.id in memberIDs):
        channel = message.channel
        if 'stop' in message.content:
            if turnOffInstance():
                await message.channel.send('AWS Instance stopping')
            else:
                await message.channel.send('Error stopping AWS Instance')
        elif 'start' in message.content:
            if turnOnInstance():
                await message.channel.send('AWS Instance starting')
            else:
                await message.channel.send('Error starting AWS Instance')
        elif 'state' in message.content:
            await message.channel.send('AWS Instance state is: ' + getInstanceState())
        elif 'reboot' in message.content:
            if rebootInstance():
                await message.channel.send('AWS Instance rebooting')
            else:
                await message.channel.send('Error rebooting AWS Instance')
        elif 'info' in message.content:
            await message.channel.send('Server start/stop bot. Commands are `start`, `stop`, `state`, `reboot` and `info`')

def turnOffInstance():
    try:
        instance.stop(False, False)
        return True
    except:
        return False

def turnOnInstance():
    try:
        instance.start()
        return True
    except:
        return False

def getInstanceState():
    aws_state = instance.state
    if (aws_state['Name'] == 'running'):
        return getPortState(aws_state['public_ip_address'], 25565)
    else:
        return aws_state['Name']

def getPortState(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    ready = sock.connect_ex((ip, port))
    if ready == 0:
        return 'ready at ' + ip 
    else:
        return 'game startup in progress, please wait'

def rebootInstance():
    try:
        instance.reboot()
        return True
    except:
        return False


client.run(os.environ['AWSDISCORDTOKEN'])

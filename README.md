# AWS Controller Discord Bot
Fork of https://github.com/leobeosab/AwsEc2DiscordBot with a few mods to make it easy for 
my kids and friends to start/stop a minecraft server, including:
* fixed some issues arising from newer discord module
* replaced hard coding with environment variables
* added similar bot script for ECS bots (more flexible, faster to start, cheaper if you use Fargate spot)
* bot limited to guild-tagged EC2 instances or ECS services
* added `info` command
* `state` checks to see if minecraft running and reports appropriately
* templates for a `systemd` linux service added

## Tools Used
* Python 3 (v3.8 or higher) and pip3
* AWS CLI : ```pip3 install awscli ```
* AWS BOTO library : ``` pip3 install boto3 ```
* Discord Bot library : ``` pip3 install discord ```

## AWS setup
* for ECS (Docker/Fargate) bots, see http://github.com/drpump/minebot-cdk
* for EC2 bots:
  - create an EC2 instance and configure minecraft to run as a daemon. I used msm (https://msmhq.com)
  - add a `guild` tag to your ec2 instance with your Discord guild ID as the value
  
## Bot Usage | Installation
1. Install and setup the required tools above on your bot server
2. Setup AWS CLI with ``` aws configure ```
3. Go to Discord's developer site and setup a bot [here](https://discordapp.com/developers)
4. Clone this repo into a desired folder
5. Set the discord token environment variable with the name 'AWSDISCORDTOKEN'
6. Start bot for EC2 or ECS:
   * For EC2, run python3 bot.py
   * for ECS, run python3 ecsbot.py
## Run daemon in cloud
Assuming you've already got it running locally using the instructions above ...
1. Create cloud VM using an Ubuntu image and login
2. Install python3 ```sudo apt install python3```
3. Install AWS cli ```sudo pip3 install awscli```. You might need to use ```--target /usr/lib/python3.X``` to ensure it is installed system-wide.
4. Install required libs ```sudo pip3 install boto3 discord```. 
5. Create a daemon user with a home dir ```sudo useradd --service -m ec2bot```
6. Su to that user ```sudo su - ec2bot```
7. Setup AWS using ```aws configure``` (you will need suitable AWS credentials, preferably locked down to limit capabilities), or copy an already configured `.aws` directory for this user (chmod'ed so ec2bot owns the dir and files)
8. Copy/download `bot.py` or `ecsbot.py` into the home directory
9. Exit from your `su` session (```^D```)
10. Copy/download `ec2bot.service` or `ecsbot.service`
11. Edit and set the `AWSDISCORDTOKEN` environment variable
12. Copy service file to systemd, e.g. ```sudo cp ec2bot.service /etc/systemd/system/```
13. Load and enable 
```
  sudo systemctl daemon-reload 
  sudo systemctl enable ec2bot # or ecsbot
  sudo systemctl start ec2bot # or ecsbot
```
14. Use `tail /var/log/syslog` to check output and make sure it is running

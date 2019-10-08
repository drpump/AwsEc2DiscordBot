# AWS EC2 Controller Discord Bot
Fork of https://github.com/leobeosab/AwsEc2DiscordBot with a few mods to make it easy for 
my kids and friends to start/stop a minecraft server, including:
* fixed some issues arising from newer discord module
* replaced hard coding with environment variables
* bot limited to a single guild
* added `info` command
* `state` checks to see if minecraft port is accessible and reports appropriately
* template for a `systemd` linux service added

## Tools Used
* Python 3 and pip3
* AWS CLI : ```pip3 install awscli ```
* AWS BOTO library : ``` pip3 install boto3 ```
* Discord Bot library : ``` pip3 install discord ```

## Usage | Installation
1. Install and setup the required tools above
2. Setup AWS CLI with ``` aws configure ```
3. Go to Discord's developer site and setup a bot [here](https://discordapp.com/developers)
4. Clone this repo into a desired folder
5. Set the AWS EC2 instance ID with environment variable 'AWSINSTANCEID'
6. Set the discord token environment variable with the name 'AWSDISCORDTOKEN'
7. Set the discord guild id in environment variable 'AWSDISCORDGUILD'
8. python3 bot.py :)

## Run daemon in cloud
Assuming you've already got it running locally using the instructions above ...
1. Create cloud VM using an Ubuntu image and login
2. Install python3 ```sudo apt install python3```
3. Install AWS cli ```sudo pip3 install awscli```. You might need to use ```--target /usr/lib/python3.X``` to ensure it is installed system-wide.
4. Install required libs ```sudo pip3 install boto3 discord```. 
5. Create a daemon user with a home dir ```sudo useradd -m ec2bot```
6. Su to that user ```sudo su - ec2bot```
7. Setup AWS using ```aws configure``` (you will need suitable AWS credentials, preferably locked down to limit capabilities), or copy an already configured `.aws` directory for this user (chmod'ed so ec2bot owns the dir and)
8. Copy/download `bot.py` into the home directory
9. Exit from your `su` session (```^D```)
10. Copy/download `ec2bot.service` 
11. Edit and set the `AWSINSTANCEID`, `AWSDISCORDTOKEN` and `AWSDISCORDGUILD` environment variables
12. Copy for systemd ```sudo cp ec2bot.service /etc/systemd/system/```
13. Load and enable 
```
  sudo systemctl daemon-reload 
  sudo systemctl enable ec2bot
  sudo systemctl start ec2bot
```
14. Use `tail /var/log/syslog` to check output and make sure it is running
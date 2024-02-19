
# Self-Hosted Vaultwarden with Nginx Proxy Manager + DuckDNS + Let's Encrypt and Ngrok

```markdown
> Austin.Lai |
> -----------| February 05th, 2024
> -----------| Updated on February 18th, 2024
```

---

## Table of Contents

<!-- TOC -->

- [Self-Hosted Vaultwarden with Nginx Proxy Manager + DuckDNS + Let's Encrypt and Ngrok](#self-hosted-vaultwarden-with-nginx-proxy-manager--duckdns--lets-encrypt-and-ngrok)
    - [Table of Contents](#table-of-contents)
    - [Disclaimer](#disclaimer)
    - [Description](#description)
    - [Pre-requisites for this setup](#pre-requisites-for-this-setup)
        - [Windows Network Interfaces](#windows-network-interfaces)
        - [DuckDNS Configuration](#duckdns-configuration)
        - [vaultwarden docker compose file](#vaultwarden-docker-compose-file)
        - [NGROK Account](#ngrok-account)
        - [ngrok docker compose file](#ngrok-docker-compose-file)
        - [env file](#env-file)
    - [init script](#init-script)
    - [Additional Information](#additional-information)
        - [Powershell Function added to Powershell Profile](#powershell-function-added-to-powershell-profile)
            - [vaultwarden-python](#vaultwarden-python)
            - [vaultwarden-restart](#vaultwarden-restart)
        - [Configure Nginx Reverse Proxy Manager for Vaultwarden](#configure-nginx-reverse-proxy-manager-for-vaultwarden)
        - [Ngrok Web Interface and Status](#ngrok-web-interface-and-status)

<!-- /TOC -->

<br>

## Disclaimer

<span style="color: red; font-weight: bold;">DISCLAIMER:</span>

This project/repository is provided "as is" and without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

This project/repository is for <span style="color: red; font-weight: bold;">Educational</span> purpose <span style="color: red; font-weight: bold;">ONLY</span>. Do not use it without permission. The usual disclaimer applies, especially the fact that me (Austin) is not liable for any damages caused by direct or indirect use of the information or functionality provided by these programs. The author or any Internet provider bears NO responsibility for content or misuse of these programs or any derivatives thereof. By using these programs you accept the fact that any damage (data loss, system crash, system compromise, etc.) caused by the use of these programs is not Austin responsibility.

<br>

## Description

<!-- Description -->

This project/repository is a local setup of <span style="color: red; font-weight: bold;">Self-Hosted Vaultwarden with Nginx Reverse Proxy Manager (that using DuckDNS and Let's Encrypt) and Ngrok</span>.

<span style="color: orange; font-weight: bold;">Note:</span>

- The configurations in this project/repository are for your reference ONLY (the reasons are as follows):
    - The setup is hosted in <span style="color: green; font-weight: bold;">docker container</span> environment on a <span style="color: green; font-weight: bold;">Windows</span> host.
    - You can register a free subdomain with <span style="color: green; font-weight: bold;">DuckDNS</span> just for the purpose of getting a certificate signed by <span style="color: green; font-weight: bold;">Let's Encrypt</span>.
    - However, there is no need to change the DNS configuration in your firewall or home router since this setup is purely hosted locally. If there is a need to access <span style="color: green; font-weight: bold;">vaulwarden publicly</span>, that's where the <span style="color: green; font-weight: bold;">Ngrok</span> service will be spinning up.
    - This setup has two separate docker compose files:
        - One for <span style="color: green; font-weight: bold;">Ngrok (ngrok-docker-compose.yml)</span>.
        - One for <span style="color: green; font-weight: bold;">Vaultwarden and Nginx Reverse Proxy Manager (vaultwarden-docker-compose.yml)</span>.
    - Please change the configuration accordingly to suits your hosting environment.

<!-- /Description -->

<br>

This project/repository has the following files and directories in the structure as below:

- Directories

  ```bash
  .
  ├── nginx-proxy-manager
  │   ├── data
  │   └── letsencrypt
  ├── ngrok
  └── vaultwarden
      └── data
  ```

- All files and directories

  ```bash
  .
  ├── .env
  ├── init.py
  ├── nginx-proxy-manager
  │   ├── data
  │   └── letsencrypt
  ├── ngrok
  │   ├── ngrok.json
  │   └── ngrok.yml
  ├── LICENSE.md
  ├── ngrok-docker-compose.yml
  ├── README.md
  ├── vaultwarden
  │   └── data
  └── vaultwarden-docker-compose.yml
  ```

<!-- /Description -->

<br>

## Pre-requisites for this setup

### Windows Network Interfaces

This setup requires you to have a network interface that is configured with static IP addresses. For example, `192.168.56.0/24` or `192.168.138.0/24`.

This can be either you have:

- Hyper-V installed with Internal Network
- VirtualBox installed with Host-Only Network

For setup shown in this repository, we are using VirtualBox installed with Host-Only Network with the network of `192.168.56.0/24`.

<br>

### DuckDNS Configuration

1. Go to DuckDNS website and sign-up/login.
2. Add your domain.
3. Assigned the IP address of your selection in the [Windows Network Interfaces](#windows-network-interfaces).
4. Note down the FQDN and your DuckDNS token.

<br>

### vaultwarden docker compose file

The `vaultwarden-docker-compose.yml` file can be found [here](./vaultwarden-docker-compose.yml) or below:

<details>

<summary><span style="padding-left:10px;">Click here to expand for the "vaultwarden-docker-compose.yml" !!!</span>

</summary>

```yml
version: "3.9"

networks:
  example-network:
    name: example-network
    driver: bridge
    ipam:
      driver: default

services:
  nginx-proxy-manager:
    env_file:
      - path: ./.env
        required: true
    image: ${NPM_IMAGE_TAG}
    container_name: ${NPM_CONTAINER_NAME}
    volumes:
      - "./nginx-proxy-manager/data:/data"
      - "./nginx-proxy-manager/letsencrypt:/etc/letsencrypt"
    environment:
      # Uncomment this if you want to change the location of the SQLite DB file within the container
      # - DB_SQLITE_FILE="/data/database.sqlite"
      - DISABLE_IPV6=${DISABLE_IPV6}
      - PUID=${PUID}
      - PGID=${PGID}
    restart: ${RESTART_STATUS}
    networks:
      - example-network
    ports:
      # These ports are in format <host-port>:<container-port>
      - '80:80' # Public HTTP Port
      - '443:443' # Public HTTPS Port
      - '81:81' # Admin Web Port
      # Add any other Stream port you want to expose
      # - '21:21' # FTP
    healthcheck:
      test: ["CMD", "/usr/bin/check-health"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 90s
    security_opt:
      - no-new-privileges:${NO_NEW_PRIVILEGES}

  vaultwarden:
    env_file:
      - path: ./.env
        required: true
    image: ${VAULTWARDEN_IMAGE_TAG}
    container_name: ${VAULTWARDEN_CONTAINER_NAME}
    volumes:
      - "./vaultwarden/data/:/data/"
    environment:
      - PUID=${PUID}
      - PGID=${PGID}
      - ADMIN_TOKEN=${ADMIN_TOKEN} # Disable admin page by not issue any admin token
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_FROM=${SMTP_FROM}
      - SMTP_SECURITY=${SMTP_SECURITY} # The security method used by your SMTP server. Possible values: “starttls” / “force_tls” / “off”.
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - LOGIN_RATELIMIT_MAX_BURST=10
      - LOGIN_RATELIMIT_SECONDS=60
      - ADMIN_RATELIMIT_MAX_BURST=10
      - ADMIN_RATELIMIT_SECONDS=60
      - SENDS_ALLOWED=${SENDS_ALLOWED} # This setting determines whether users are allowed to create Bitwarden Sends – a form of credential sharing.
      - SIGNUPS_ALLOWED = ${SIGNUPS_ALLOWED} # This setting controls whether or not new users can register for accounts without an invitation. Possible values: true / false. Can change to false to disable anyone create account - for better security
      - SIGNUPS_VERIFY=${SIGNUPS_VERIFY} # This setting determines whether or not new accounts must verify their email address before being able to login to Vaultwarden. Possible values: true / false.
      - SIGNUPS_VERIFY_RESEND_TIME=${SIGNUPS_VERIFY_RESEND_TIME}
      - SIGNUPS_VERIFY_RESEND_LIMIT=${SIGNUPS_VERIFY_RESEND_LIMIT}
      - SIGNUPS_DOMAINS_WHITELIST=${SIGNUPS_DOMAINS_WHITELIST}
      - EMERGENCY_ACCESS_ALLOWED=${EMERGENCY_ACCESS_ALLOWED} # This setting controls whether users can enable emergency access to their accounts. This is useful, for example, so a spouse can access a password vault in the event of death so they can gain access to account credentials. Possible values: true / false.
      - WEBSOCKET_ENABLED=${WEBSOCKET_ENABLED}
      - WEB_VAULT_ENABLED=${WEB_VAULT_ENABLED} # This setting determines whether or not the web vault is accessible. Stopping your container then switching this value to false and restarting Vaultwarden could be useful once you’ve configured your accounts and clients to prevent unauthorized access. Possible values: true/false.
      - DOMAIN=${DOMAIN}
      - LOG_FILE=${LOG_FILE}
      - INVITATIONS_ALLOWED=${INVITATIONS_ALLOWED}
      - SHOW_PASSWORD_HINT=${SHOW_PASSWORD_HINT}
      - PASSWORD_HINTS_ALLOWED=${PASSWORD_HINTS_ALLOWED}
      - PUSH_ENABLED=${PUSH_ENABLED}
      - PUSH_INSTALLATION_ID=${PUSH_INSTALLATION_ID}
      - PUSH_INSTALLATION_KEY=${PUSH_INSTALLATION_KEY}
    restart: ${RESTART_STATUS}
    networks:
      - example-network
    ports:
      - 8880:80
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 90s
    depends_on:
      nginx-proxy-manager:
        condition: service_healthy
    security_opt:
      - no-new-privileges:${NO_NEW_PRIVILEGES}
```

</details>

<br>

<span style="color: red; font-weight: bold;">Things to take note:</span>

- <span style="color: green; font-weight: bold;">Please replace the naming of "example-network" to the name you want across the docker compose file.

<br>

### NGROK Account

This setup required you to have NGROK Account.

- Go to <https://ngrok.com/>.
- Go to <span style="color: green">"CloudEdge"</span> > <span style="color: green">"Domain"</span>, NGROK given one free domain (subdomain) for the account. Please note down the domain, you will need it later.
- Then go to <span style="color: green">"CloudEdge"</span> > <span style="color: green">"Edges"</span> > <span style="color: green">"Create an edge"</span> (If the edge does not exist)
- Create <span style="color: green">"HTTPS"</span> edge, enabled <span style="color: green">"compression"</span> and leave everything as default.
- Then you will have the option to start a tunnel with config file.
- We need copy the configuration to <span style="color: green">a temporary file that to be used in "/ngrok/ngrok.yml"</span>.

We provide you a sample of <span style="color: green">"ngrok.yml"</span> that can be found [here](./ngrok/ngrok.yml) or below:

<details>

<summary><span style="padding-left:10px;">Click here to expand for the "ngrok.yml" !!!</span></summary>

```yml
# https://ngrok.com/docs/secure-tunnels/ngrok-agent/reference/config/#metadata
# https://ngrok.com/docs/api/
authtoken: YOUR_NGROK_AUTH_TOKEN
api_key: YOUR_NGROK_API_KEY
connect_timeout: 30s
console_ui: true
console_ui_color: transparent
dns_resolver_ips:
  - 1.1.1.1
  - 8.8.8.8
heartbeat_interval: 1m
heartbeat_tolerance: 5s
inspect_db_size: 50000000 # 50MB
# log_level: debug
log_level: info
log_format: json
log: /var/log/ngrok.json
metadata: '{"name": "example"}'
version: 2
web_addr: 0.0.0.0:4040
tunnels:
  example:
    labels:
      - edge=YOUR_EDGE_ID
    addr: http://vaultwarden:80
    inspect: false
```

</details>

<br>

Please REPLACE the following with the configuration from NGROK:

- "authtoken"
- "api_key"
- "name" - under `metadata` and `tunnels`
- "edge"

You cane refer to the official guide:

- <https://ngrok.com/docs/secure-tunnels/ngrok-agent/reference/config/#metadata>
- <https://ngrok.com/docs/api/>

<br>

### ngrok docker compose file

The `ngrok-docker-compose.yml` file can be found [here](./ngrok-docker-compose.yml) or below:

<details>

<summary><span style="padding-left:10px;">Click here to expand for the "ngrok-docker-compose.yml" !!!</span></summary>

```yml
version: "3.9"

networks:
  example-network:
    external: true

services:
  ngrok:
    env_file:
      - path: ./.env
        required: true
    image: ${NGROK_IMAGE_TAG}
    container_name: ${NGROK_CONTAINER_NAME}
    volumes:
      - "./ngrok/ngrok.yml:/etc/ngrok.yml"
      - "./ngrok/ngrok.json:/var/log/ngrok.json:rw"
    environment:
      # Uncomment this if you want to change the location of the SQLite DB file within the container
      # - DB_SQLITE_FILE="/data/database.sqlite"
      - DISABLE_IPV6=${DISABLE_IPV6}
      - PUID=${PUID}
      - PGID=${PGID}
    restart: ${RESTART_STATUS}
    networks:
      - example-network
    ports:
      - 8881:4040
    security_opt:
      - no-new-privileges:${NO_NEW_PRIVILEGES}
    command:
      - "start"
      - "--all"
      - "--config"
      - "/etc/ngrok.yml"
```

</details>

<br>

<span style="color: red; font-weight: bold;">Things to take note:</span>

- <span style="color: green; font-weight: bold;">Please replace the naming of "example-network" to the name you want across the docker compose file!</span>

<br>

### .env file

The `.env` file store all the variables and values to be used in `ngrok-docker-compose.yml` and `vaultwarden-docker-compose.yml`.

Change variables in the `.env` to meet your requirements. There is `# CHANGE HERE !!!` in the `.env` shown below to remind you to make the change.

<span style="color: red; font-weight: bold;">Note</span> that the `.env` file should be in the same directory as  `ngrok-docker-compose.yml` and `vaultwarden-docker-compose.yml`.

The `.env` file can be found [here](./.env) or below:

<details>

<summary><span style="padding-left:10px;">Click here to expand for the ".env" !!!</span></summary>

```sh
# GLOBAL VARIABLES
RESTART_STATUS=always
NO_NEW_PRIVILEGES=true
PUID=1000
PGID=1000



# NGINX PROXY MANAGER VARIABLES
NPM_IMAGE_TAG=jc21/nginx-proxy-manager:latest
NPM_CONTAINER_NAME=nginx-proxy-manager
DISABLE_IPV6=true



# VAULTWARDEN VARIABLES
VAULTWARDEN_IMAGE_TAG=vaultwarden/server:latest
VAULTWARDEN_CONTAINER_NAME=vaultwarden
VAULTWARDEN_HOSTNAME=YOUR_VAULTWARDEN_HOSTNAME_FQDN # CHANGE HERE !!!

# You can randomly generated string of characters, for example running "openssl rand -base64 48"
# Or you can run "docker run --rm -it vaultwarden/server /vaultwarden hash"
# OR using command below for Bitwarden defaults
# echo -n "MySecretPassword" | argon2 "$(openssl rand -base64 32)" -e -id -k 65540 -t 3 -p 4
# Output: $argon2id$v=19$m=65540,t=3,p=4$bXBGMENBZUVzT3VUSFErTzQzK25Jck1BN2Z0amFuWjdSdVlIQVZqYzAzYz0$T9m73OdD2mz9+aJKLuOAdbvoARdaKxtOZ+jZcSL9/N0
# Or using command below for OWASP minimum recommended settings
# echo -n "MySecretPassword" | argon2 "$(openssl rand -base64 32)" -e -id -k 19456 -t 2 -p 1
# Output: $argon2id$v=19$m=19456,t=2,p=1$cXpKdUxHSWhlaUs1QVVsSStkbTRPQVFPSmdpamFCMHdvYjVkWTVKaDdpYz0$E1UgBKjUCD2Roy0jdHAJvXihugpG+N9WcAaR8P6Qn/8
# Need to accomodate the password to docker compose
# echo 'your-authentication-token-here' | sed 's#\$#\$\$#g'
# echo -n "MySecretPassword" | argon2 "$(openssl rand -base64 32)" -e -id -k 19456 -t 2 -p 1 | sed 's#\$#\$\$#g'
ADMIN_TOKEN=YOUR_ADMIN_TOKEN # CHANGE HERE !!!

# As for this example, we are using Google SMTP. You can change to any email provider as of your choice.
SMTP_HOST=smtp.gmail.com # CHANGE HERE !!!
SMTP_FROM=YOUR_SMTP_FROM # CHANGE HERE !!!
SMTP_SECURITY=starttls # CHANGE HERE !!!
SMTP_PORT=587 # CHANGE HERE !!!
SMTP_USERNAME=YOUR_SMTP_USERNAME # CHANGE HERE !!!

# Go to Google Account > Security > 2FA > Generate App Password
SMTP_PASSWORD=YOUR_SMTP_PASSWORD # CHANGE HERE !!!

SENDS_ALLOWED=false
SIGNUPS_ALLOWED=false
SIGNUPS_VERIFY=true
SIGNUPS_VERIFY_RESEND_TIME=3600
SIGNUPS_VERIFY_RESEND_LIMIT=5
SIGNUPS_DOMAINS_WHITELIST=YOUR_SIGNUPS_DOMAINS_WHITELIST # CHANGE HERE !!!
EMERGENCY_ACCESS_ALLOWED=false
WEBSOCKET_ENABLED=true
WEB_VAULT_ENABLED=true
DOMAIN=https://YOUR_VAULTWAARDEN_FQDN # CHANGE HERE !!!
LOG_FILE=/data/bitwarden.log
INVITATIONS_ALLOWED=false
SHOW_PASSWORD_HINT=false
PASSWORD_HINTS_ALLOWED=false
PUSH_ENABLED=true

# Go to https://bitwarden.com/host/ to request PUSH_INSTALLATION_ID and PUSH_INSTALLATION_KEY
PUSH_INSTALLATION_ID=YOUR_PUSH_INSTALLATION_ID # CHANGE HERE !!!
PUSH_INSTALLATION_KEY=YOUR_PUSH_INSTALLATION_KEY # CHANGE HERE !!!



# NGROK VARIABLES
NGROK_IMAGE_TAG=ngrok/ngrok:latest
NGROK_CONTAINER_NAME=ngrok
```

</details>

<br>

## init script

`init.py` is a python helper script for you to manage Vaultwarden, Nginx Reverse Proxy Manager and Ngrok docker container.

The script will START or STOP the container specified in the selected docker compose file based on various condition to avoid configuration or accessibility error.

It can also pull the latest image for the selected docker compose file.

The `init.py` file can be found [here](./init.py) or below:

<details>

<summary><span style="padding-left:10px;">The script description and usage as shown below:</span></summary>

```python
#! /usr/bin/python3
#! /usr/bin/env python3

import sys
import os
import subprocess
import signal

# Define docker compose files
vaultwarden = "vaultwarden-docker-compose.yml"
ngrok = "ngrok-docker-compose.yml"

# Get the current path of the script
script_path = os.path.dirname(__file__)

# Append the current path to the docker compose files
vaultwarden_path = os.path.join(script_path, vaultwarden)
ngrok_path = os.path.join(script_path, ngrok)


# Define a function to display help message
def display_help():
    print("Description:")
    print("     This is a helper script for managing Docker containers.")
    print("     This script can perform [START] or [STOP] action for the container specified in the selected docker compose file.")
    print("     It can also pull the latest image for the selected docker compose file.")
    print("Usage:")
    print("     ./init.py [file] [command]")
    print("Options:")
    print("     file: The Docker compose file to use (vaultwarden, ngrok)")
    print("               *vaultwarden - Start Vaultwarden container using")
    print(f"                using {vaultwarden_path}.")
    print("               *ngrok - Start Ngrok container using")
    print(f"                {ngrok_path}.")
    print("  command: The command to execute (up, down, pull)")
    print("               *up - docker-compose -f [file] up --timestamps --wait --detach")
    print("               *down - docker-compose -f [file] down")
    print("               *pull - docker-compose -f [file] pull")
    print("       -h: Display this help message (--help, /?)")
    sys.exit(0)


# Define a function to capture Ctrl+C and exit
def signal_handler(signal, frame):
    sys.exit(1)


# Define a function to check if a container is running
def is_container_running(name):
    container_id = subprocess.check_output(
        ["docker", "ps", "-qf", f"name=^/{name}$"]
    ).decode().strip()
    return bool(container_id)


# Define a function to start a container with a selected file
def start_container(file, name):
    print(f"The {name} container is not running.")
    subprocess.run(
        ["docker-compose", "-f", file, "up", "--timestamps",
         "--wait", "--detach"]
    )


# Define a function to stop a container with a selected file
def stop_container(file, name):
    # print(f"The {name} container is running!")
    subprocess.run(
        ["docker-compose", "-f", file, "down"]
    )




# Define a function to run command
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")




# Define a function to pull Docker images for a selected file
def pull_images(file):
    # run_command('sudo -S <<< "kali" apt update -y')
    # run_command('sudo -S <<< "kali" apt install -y gnupg2 pass')
    subprocess.run(["docker-compose", "-f", file, "pull"])




# Define a function to prompt user enter yes or no for confirmation of next action
def yes_or_no():
    while True:
        answer = input("Would you like to continue? ('yes|y|Yes|Y|YES' or 'no|n|No|N|N'): ").lower()
        if answer in ["yes", "y", "Yes", "Y", "YES"]:
            return True
        elif answer in ["no", "n", "No", "N", "NO"]:
            return False
        else:
            print("Invalid input. Please enter 'yes|y|Yes|Y|YES' or 'no|n|No|N|N'.")


# Set valid_arg1 to False as default arg1 or sys.argv[1] is not exist
valid_arg1 = False

# Check for command line arguments
if len(sys.argv) < 2:
    arg1 = "-h"
else:
    arg1 = sys.argv[1]

# Display help message
if arg1 in ["/?", "-h", "--help"]:
    display_help()

# Capture Ctrl+C and exit
signal.signal(signal.SIGINT, signal_handler)

# Allow user to select which file to use
if arg1 == "vaultwarden":
    selected_file = vaultwarden_path
    valid_arg1 = True
elif arg1 == "ngrok":
    selected_file = ngrok_path
    valid_arg1 = True
else:
    print()
    print("Error: Invalid input. Please select a valid file.")
    print()
    display_help()
    sys.exit(1)

# Only proceed if there is a valid first argument!
if valid_arg1:
    # Check if second argument exists, if not display error and help
    # message
    if len(sys.argv) < 3:
        print()
        print("Error: Missing second option/argument.")
        print()
        display_help()
        sys.exit(1)
    else:
        arg2 = sys.argv[2]

        # Add pull image action here:
        if arg2 == "pull":
            pull_images(selected_file)

        # Execute the command based on the second argument
        elif arg2 == "up":
            if arg1 == "vaultwarden":
                # Check if vaultwarden container is already running
                if is_container_running("vaultwarden"):
                    # If yes, do nothing and inform the user
                    print(f"The {arg1} container is already running!")
                else:
                    # If no, start the vaultwarden container with the
                    # selected file
                    start_container(selected_file, arg1)
            elif arg1 == "ngrok":
                # Check if ngrok container is already running
                if is_container_running("ngrok"):
                    # If yes, do nothing and inform the user
                    print(f"The {arg1} container is already running!")
                else:
                    # If no, check if vaultwarden container is running
                    # Since ngrok need to attach to the same docker
                    # network as vaultwarden container
                    if is_container_running("vaultwarden"):
                        # If yes, start the ngrok container with the
                        # selected file
                        print("The vaultwarden container is running!")
                        start_container(selected_file, arg1)
                    else:
                        # If no, do not start the ngrok container and
                        # inform the user
                        print("The vaultwarden container is not running.")
                        print("Will not proceed to start ngrok container.")
                        print("Please ensure vaultwarden container is running first.")
                        print("Since ngrok need to attach to the same docker network as vaultwarden container.")
        elif arg2 == "down":
            if arg1 == "vaultwarden":
                # Check if ngrok container is running
                # Since ngrok is attached to the same docker network as vaultwarden container
                if is_container_running("ngrok"):
                    # If yes, do not stop the vaultwarden container and inform the user
                    print("The ngrok container is running!")
                    print("Will not proceed to stop vaultwarden container.")
                    print("Please ensure ngrok container is not running first.")
                    print("Since ngrok is attached to the same docker network as vaultwarden container.")
                elif is_container_running("vaultwarden"):
                    # If yes, stop the vaultwarden container with the selected file
                    print("The vaultwarden container is running!")
                    if yes_or_no():
                        stop_container(selected_file, arg1)
                else:
                    print("The vaultwarden container is not running!")
            elif arg1 == "ngrok":
                # Check if ngrok container is running
                if is_container_running("ngrok"):
                    # If yes, stop the ngrok container with the selected file and inform the user
                    print("The ngrok container is running!")
                    stop_container(selected_file, arg1)
                else:
                    print("The ngrok container is not running!")
        else:
            # Display error and help message if invalid second argument
            print()
            print("Error: Invalid option/argument. Please select a valid option/argument.")
            print()
            display_help()
            sys.exit(1)
```

</details>

<br>

## Additional Information

### Powershell Function added to Powershell Profile

As this setup hosted on Windows, we have a few powershell functions which leveraging WSL2; you can add into your powershell profile that will allow you easy access to the `init.py`.

<br>

#### vaultwarden-python

```powershell
Function vaultwarden-python {
  wsl --set-default kali-linux; wsl bash -c "cd /mnt/YOUR_INIT.PY_LOCATION && ./init.py $args"
}
```

**Replace YOUR_INIT.PY_LOCATION**

<br>

#### vaultwarden-restart

```powershell
Function vaultwarden-restart {

  $FirstCommand = "vaultwarden-python vaultwarden down"

  $SecondCommand = "vaultwarden-python vaultwarden up"

  # Run the first command
  Invoke-Expression -Command $FirstCommand

  # Check if the first command was successful, then run the second command
  if ($? -and ($SecondCommand -ne $null)) {
      Invoke-Expression -Command $SecondCommand
      Write-Host "Both commands executed successfully"
  } elseif ($SecondCommand -eq $null) {
      Write-Host "No second command provided"
  } else {
      Write-Host "The first command failed"
  }
}
```

<br>

### Configure Nginx Reverse Proxy Manager for Vaultwarden

Once the **Vaultwarden** and **Nginx Reverse Proxy Manager** are up.

You can access to Web Interface as following:

- Vaultwarden = <http://127.0.0.1:8880>
- Vaultwarden Admin Portal = <http://127.0.0.1:8880/admin>
- Nginx Reverse Proxy Manager = <http://127.0.0.1>
- Nginx Reverse Proxy Manager Admin Portal = <http://127.0.0.1:81>

Now, let's configure the Nginx Reverse Proxy Manager for Vaultwarden in order to have SSL certificates.

---

Login to Nginx Reverse Proxy Manager (<http://127.0.0.1:81>).

---

> :sparkles:
>
> - You can add more users if you want via "`Users`" tab.
> - If you want to have access control, then you can configure your access control policies via "`Access Lists`" tab.

---

**To setup SSL for Vaultwarden:**

- Go to "`SSL Certificates`" tab.
- Click "`Add SSL Certificate`" and select "`Let's Encrypt`".
- In the "`Domain Names`" field, you can key-in the domain name from DuckDNS.
- If you want to use wildcard signing certificate, you can key-in something like below:
  - `example.duckdns.org`
  - `*.example.duckdns.org`
- Key-in your email address used by Let's Encrypt.
- Enable "`Use DNS Challenge`".
- Select "`DuckDNS`" as "`DNS Provider`".
- Replace the "`DuckDNS_TOKEN`"
- For "`Propagation Seconds`", set to "`60`"
- Agree the "`term`"

> **Note: You have to setup DuckDNS first, this allow the DNS record to be updated across all the servers in the world before we setup the SSL certificate.**

---

**To Proxy Host for Vaultwarden:**

- Go to "`Hosts`" and select "`Proxy Hosts`".
- Click "`Add Proxy Host`".
- In the "`Domain Names`" field, you can key-in the FQDN for Vaultwarden of your choice (this need to be the same as stated in `.env`).
- Select "`http`" in the "`Scheme`".
- Key-in "`YOUR_IP`" in the "`Forward Hostname/IP`" ("`YOUR_IP`" - this will be your network interface stated in  [Windows Network Interfaces](#windows-network-interfaces)).
- Key-in "`8880`" in the "`Forward Port`" (this need to be the same as stated in `vaultwarden-docker-compose.yml`).
- Enable "`Block Common Exploits`".
- Enable "`Websockets Support`".
- Then, go to "`SSL`" tab and select the certificate we have configured in the previous step.
- Enable "`Force SSL`".
- Enable "`HTTP/2 Support`".
- Enable "`HSTS Enabled`".
- Enable "`HSTS Subdomains`".
- Once done, click "`Save`" to complete the configuration.

<br>

### Ngrok Web Interface and Status

Once NGROK is up, you can access Ngrok Web Interface via "`http://YOUR_IP:8881/status`"

To check NGROK status, go to "`http://YOUR_IP:8881/api/tunnels`"

> **"`YOUR_IP`" - this will be your network interface stated in  [Windows Network Interfaces](#windows-network-interfaces)**

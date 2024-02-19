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

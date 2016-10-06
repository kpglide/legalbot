import os
import time
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
GENERAL_COMMANDS = {"unsupported": ('Not sure what you mean. These are the' 
                                    'commands I understand: \n\ncontract:  I ' 
                                    'can draft contracts for you. Type '
                                    '"contract" to get started.'
                            ),
                    "contract": ('Sure thing.  These are the contracts I can '
                                 'draft:\n\nNDA: Type "NDA" for a '
                                 'non-disclosure agreement.'
                        ) 
            }
CONTRACT_COMMANDS = {'nda': 'Great, what\'s the name of the other party?'}

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = GENERAL_COMMANDS["unsupported"]
    
    if command.lower() in CONTRACT_COMMANDS:
        response = CONTRACT_COMMANDS[command.lower()]

    elif command.lower() in GENERAL_COMMANDS:
        response = GENERAL_COMMANDS[command.lower()]
    
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        print 'output list is: ', output_list
        for output in output_list:
            
            if (output and 'text' in output and AT_BOT in output['text'] 
                and output['channel'].startswith('D')
                ):
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']

            elif (output and 'text' in output and output['channel'].startswith('D')
                    and output['user'] != BOT_ID):
                return output['text'], output['channel'], output['user']

    return None, None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel and user:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
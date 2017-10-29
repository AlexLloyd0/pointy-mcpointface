from slackclient import SlackClient
import time
import os
import re
import json

from typing import Tuple

token = os.environ.get('SLACKBOT_POINTY_TOKEN')

slack_client = SlackClient(token)

change_score = re.compile('^([^+\-=])+ ((\+\+|--)$|((\+=|-=) [0-9]+)$)')


with open('scores.json', 'r') as file:
    scores = json.load(file)


def main():
    try:
        if slack_client.rtm_connect():
            print('Running...')
            while True:
                events = slack_client.rtm_read()
                for event in events:
                    if (
                        'channel' in event and
                        'text' in event and
                        event.get('type') == 'message' and
                        event.get('user') != 'U7QNFJKEH'
                    ):
                        channel = event['channel']
                        text = event['text']
                        # Don't do it if it's pointy doing the pointing:
                        if change_score.match(text):
                            subject, points = parse_message(text)
                            if subject not in scores:
                                scores[subject] = 0
                            scores[subject] += points
                            if scores[subject] == 0:
                                del scores[subject]
                            with open('scores.json', 'w+') as file:
                                json.dump(scores, file)
                            response = f'{points} point{"s" if score != 1 else " "} for {subject}!\n{subject} has {scores.get(subject, 0)} point{"s" if score != 1 else " "}!'
                            slack_client.api_call(
                                'chat.postMessage',
                                channel=channel,
                                text=response,
                                as_user='true:'
                            )
                        elif text.startswith('score '):
                            subject = 'score '.join(text.split('score ')[1:])
                            score = scores.get(subject, 0)
                            response = f'Points make prizes!\n{subject} has {score} point{"s" if score != 1 else " "}'
                            slack_client.api_call(
                                'chat.postMessage',
                                channel=channel,
                                text=response,
                                as_user='true:'
                            )
                        elif text == 'scoreboard':
                            scored_tuples = [(subject, scores[subject]) for subject in scores]
                            ordered_tuples = sorted(scored_tuples, key=lambda x: x[1], reverse=True)
                            response = f'Here\'s a list of my favourite people:'
                            for i in range(len(ordered_tuples)):
                                subject, score = ordered_tuples[i]
                                response += f'\n{i+1}. {subject} [{score} point{"s" if score != 1 else ""}]'
                                if i == 0:
                                    response += ' :crown:'
                                elif i+1 == len(ordered_tuples):
                                    response += ' :hankey:'
                            slack_client.api_call(
                                'chat.postMessage',
                                channel=channel,
                                text=response,
                                as_user='true:'
                            )
                time.sleep(1)
        else:
            print('Connection failed, invalid token? Retrying...')
    except Exception as e:
        print(e)
        print('Oops, exception... retrying')
        main()


def parse_message(message: str) -> Tuple[str, int]:
    if message.endswith('++'):
        subject = message.split('+')[0][:-1]
        return subject, 1
    elif message.endswith('--'):
        subject = message.split('-')[0][:-1]
        return subject, -1
    else:
        split_message = message.split('=')
        subject = split_message[0][:-2]
        sign = split_message[0][-1]
        return subject, int(sign + split_message[1][1:])


def add_points(count: int):
    pass

# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.text import slugify

from core.models import Class

from random import random
import requests
import os


TimtecUser = get_user_model()
rocket = os.getenv('ROCKET_CHAT_API')
api_user = {
    'username': os.getenv('ROCKET_CHAT_USER'),
    'password': os.getenv('ROCKET_CHAT_PASS')
}

def create_chat_user(username):
    user = TimtecUser.objects.get(username=username)
    create_req = requests.post(rocket + 'users.create', headers=auth_headers, json={
        'name'    : user.username,
        'email'   : user.email,
        'password': '%d%f' % (user.id, random()),
        'username': user.username,
        'verified': True,
    })
    return create_req

def sync_room(user_list, group):
    rocket_group_req = requests.get(rocket + 'groups.info?roomName=' + group, headers=auth_headers)
    rocket_group = rocket_group_req.json()
    if not rocket_group["success"]:
        rocket_group = requests.post(rocket +  'groups.create', json={"name" : group}, headers=auth_headers).json()

    rocket_group_req = requests.get(rocket + 'groups.members?roomName=' + group, headers=auth_headers)
    try:
        rocket_group["group"]["members"] = rocket_group_req.json()["members"]
    except KeyError:
        rocket_group["group"]["members"] = []

    try:
        rocket_group["group"]["usernames"] = [u["username"] for u in rocket_group["group"]["members"]]
    except KeyError:
        rocket_group["group"]["usernames"] = []

    # For compatibility reasons with the Rocket Chat permissions system, the user making the requests needs to be a member of the room to control it
    # The next line ensures that the main user won't be removed from any group by this script
    user_list += [api_user['username']]

    # Anyone that is in the group, but isn't in the user_list, must be removed
    for group_member in rocket_group['group']['usernames']:
        if group_member not in user_list:
            # Get the userId
            user = requests.get(rocket + 'users.info?username=' + group_member, headers=auth_headers)

            # Kick him from the room
            kick = requests.post(rocket + 'groups.kick', headers=auth_headers, json={
                'roomId': rocket_group['group']['_id'],
                'userId': user.json()['user']['_id']
            })
            if not kick.ok:
                print("Couldn't kick " + group_member + " from " + rocket_group['group']['name'])

    # Anyone in the user_list that isn't in the group, must be invited
    for timtec_user in user_list:
        if timtec_user not in rocket_group['group']['usernames']:

            # Get the userId
            user = requests.get(rocket + 'users.info?username=' + timtec_user, headers=auth_headers)
            if not user.ok:
                # If Rocket.Chat couldn't find the user, he probably isn't there yet
                # So create a profile for him now
                user = create_chat_user(timtec_user)
                if not user.ok:
                    # If creation failed as well, human attention is needed for him
                    print("Couldn't locate or create " + timtec_user)
                    continue
            # Include him in the room
            invite = requests.post(rocket + 'groups.invite', headers=auth_headers, json={
                'roomId': rocket_group['group']['_id'],
                'userId': user.json()['user']['_id']
            })
            if not invite.ok:
                print("Couldn't invite " + group_member + " for " + rocket_group['group']['name'])


class Command(BaseCommand):
    help = 'Synchronize Django user groups with Rocket Chat Rooms taking specific grouping rules into account.'

    def handle(self, **options):

        global api_user_data
        api_user_data = requests.post(rocket + 'login', json=api_user).json()

        global auth_headers
        auth_headers = {
            'X-Auth-Token': api_user_data['data']['authToken'],
            'X-User-Id': api_user_data['data']['userId']
        }

        from paralapraca.models import Contract

        contracts = Contract.objects.all()
        for contract in contracts:
            is_staff_users = list(TimtecUser.objects
                                  .filter(is_staff=True)
                                  .values_list('username', flat=True))

            contract_users = list(TimtecUser.objects \
                .filter(groups=contract.groups.all()) \
                .distinct() \
                .values_list('username', flat=True))

            for cclass in contract.classes.exclude(name__contains="ARQUIVO_"):
                users = list(cclass.students.all()
                             .values_list('username', flat=True))
                users = list(set(users).intersection(set(contract_users)))
                users += list(cclass.assistants.all()
                              .values_list('username', flat=True))
                users += is_staff_users
                class_name = cclass.name.replace('Turma', '')
                sync_room(users,
                          slugify("Turma %s-%d" % (class_name, cclass.id)))

            for unity in contract.unities:
                users = list(TimtecUser.objects.filter(city=unity)
                             .values_list('username', flat=True))
                users = list(set(users).intersection(set(contract_users)))
                users += is_staff_users
                sync_room(users, slugify(unity))

            sync_room(contract_users, slugify(contract.name))

import re
import os
import sys
import download_page
import url
import irc_message
import check_valid
import periodical_jobs
import refresh

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)
check_num = lambda string: check_valid.check_num(string)
check_temp_perjob_variable = lambda ticket, command: periodical_jobs.check_temp_perjob.check_temp_perjob_variable(ticket, command)
periodical_job_args = lambda filename, args: refresh.periodical_job_args(filename, args)

service_name = 'website or webpage'
service_commands = ['webpage']

def add_url(url, ticket_id, user):
    yield(['add', 'url', '\'' + url + '\''])
    yield(['add', 'type', service_commands])
    yield(['message', user + ': Added URL \'' + url + '\' to ticket ID \'' + ticket_id + '\'.'])
    yield(['message', user + ': Set the commands. For help use \'!perjob help <Ticket ID>\'. To finish ticket ID use command \'finish\'.'])

def periodical_job(service_name, command, user):
    default_commands = ['url', 'type']
    required_commands = ['refreshtime', 'depth', 'description']
    optional_commands = []
    if command[1] == 'refreshtime':
        if check_num(command[3]):
            yield(['add', 'refreshtime', command[3]])
            yield(['message', user + ': Added refreshtime ' + command[3] + ' to ticket ID \'' + command[2] + '\'.'])
        else:
            yield(['message', user + ': Refreshtime should be a number for a ' + service_name + '.'])
    elif command[1] == 'depth':
        if check_num(command[3]):
            yield(['add', 'depth', command[3]])
            yield(['message', user + ': Added crawl depth ' + command[3] + ' to ticket ID \'' + command[2] + '\'.'])
        else:
            yield(['message', user + ': Crawl depth should be a number for a ' + service_name + '.'])
    elif command[1] == 'description':
        description = ' '.join(command[3:]).replace('\'', '\\\'')
        yield(['add', 'description', '\'' + description + '\''])
        yield(['message', user + ': Added description \'' + description + '\' to ticket ID \'' + command[2] + '\'.'])

    # Do not change this.
    elif command[1] == 'help':
        yield(['help', required_commands, optional_commands, user])
    elif command[1] == 'finish':
        yield(['finish', required_commands, default_commands, user])
    else:
        yield(['bad_command', command[1], user])

def periodical_job_start(filename, user, _):
    depth, url = periodical_job_args(filename, ['depth', 'url'])
    yield(['execute', '~/.local/bin/grab-site ' + url + ' --level=' + str(depth) + ' --ua="ArchiveTeam; Googlebot/2.1" --concurrency=1 --warc-max-size=524288000 --wpull-args="--no-check-certificate --timeout=300" > /dev/null 2>&1'])

def format_response(response):
    events = response['events']
    messages = []
    for e in events:
        message_init = e['message'].split(' ')[0]
        if message_init == 'REPORT':
            message_head = e['message'].split(' ')
            request_id = message_head[2].split('\t')[0]
            message_body = e['message'].split('\t')[1:]
        elif message_init == 'START':
            lambda_version = e['message'].split(' ')[-1]

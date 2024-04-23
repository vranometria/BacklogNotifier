import json, requests, os, boto3, time

def lambda_handler(event, context):
    body = json.loads(event['body'])
    error, error_msg = is_not_available_backlog_request(body)
    if error:
        return {
            'statusCode': 200,
            'body': json.dumps( { 'message': error_msg } )
        }
    
    
    project = body['project']
    content = body['content']
    error = ''
    
    try:
        proc(project, content)
    except Exception as e:
        print({"error": e})
        error = e.__class__.__name__
         
    return {
        'statusCode': 200,
        'body': json.dumps({"error": error})
    }
    
 
 
# 処理できるリクエストか判定する
def is_not_available_backlog_request(body_dict):
    if 'content' not in body_dict:
        return True, 'not backlog request'
        
    content = body_dict['content']
    
    if not 'id' in content['assignee']:
        return True, 'assignee id is not set'
        
    if not 'name' in content['status']:
        return True, 'status is not set'
        
    return False, None

# メイン処理
def proc(project, content):
    
    # 環境変数に未登録ユーザーではないかチェック
    assignee_id = content['assignee']['id']
    assignee_key = f'user_id{assignee_id}'
    if not assignee_key in  os.environ:
        raise "no registerd user_id(user_idXXXXX)"
    
    status_name = content['status']['name']
    ticket_key = f'{project["projectKey"]}-{content["key_id"]}'
    
    
    dynamoDB = boto3.resource('dynamodb')
    table= dynamoDB.Table('backlog-ready-call')
    data = table.get_item(Key={'ticket_id': ticket_key})
    
    is_waiting = status_name == "処理待ち" or status_name == "指摘あり"
    is_new_rec = not 'Item' in data
    text = create_message(assignee_key, ticket_key, project, content, status_name)
    
    if is_new_rec and is_waiting: # 新規で処理待ちか指摘ありは、レコード作ってslack
        put_item(table, ticket_key, status_name)
        notice_to_slack(text)
        return
 
# Slackに通知するメッセージを作成する
def create_message(assignee_key, ticket_key, project, content, status_name):
    
    slack_user = os.environ[assignee_key]
    backlog_url = os.environ['BACKLOG_TICKET']
    
    ticket_url = backlog_url + ticket_key
    
    prefix = '未設定'
    if status_name == '処理待ち':
        prefix = "が処理待ちになりました"
    elif status_name == '指摘あり':
        prefix = "に指摘がありました"
    
    return f'<@{slack_user}> <{ticket_url} | {ticket_key}>{prefix}' 
    
def notice_to_slack(text):
    slack_url = os.environ['WEBHOOK_URL']
    username = os.environ['USER_NAME']
    channel = os.environ['CHANNEL']
    icon = os.environ['ICON']
    
    param = {
        "channel": channel,
        "username": username, 
        "text": text,
        "icon_emoji": icon
    }
    param = json.dumps(param)
    response = requests.post(slack_url, param)



def put_item(table, ticket_key, status_name):
    table.put_item(
        Item={
            'ticket_id': ticket_key,
            'status': status_name,
            'created_at': int(time.time())
        }
    )



# mainの時実行する
if __name__ == "__main__":
    lambda_handler(None, None)
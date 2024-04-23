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


# mainの時実行する
if __name__ == "__main__":
    lambda_handler(None, None)
import json, requests, os, boto3, time

def lambda_handler(event, context):
    body = json.loads(event['body'])
    error, error_msg = is_not_available_backlog_request(body)
    if error:
        return {
            'statusCode': 200,
            'body': json.dumps( { 'message': error_msg } )
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



# mainの時実行する
if __name__ == "__main__":
    lambda_handler(None, None)
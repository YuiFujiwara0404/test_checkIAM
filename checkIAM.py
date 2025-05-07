"""
checkMFA.py in AWS Lambda Check MFA devices

Programmed By: Yui.Fujiwara@sony.com
Date: 2025/05/02
Last update: 2025/05/02

Description:
    - AWS Lambda function to check if users have MFA devices configured in IAM.
    - If a user does not have an MFA device, the function will send an email notification.
    - The function uses the Boto3 library to interact with AWS IAM service.

    - MFA : Multi-Factor Authentication
    - SES : Simple Email Service
    - IAM : Identity and Access Management
    - Boto3 : AWS SDK for Python
    - Lambda : Serverless compute service by AWS
"""
import boto3 

# user情報の取得, MFA設定の確認
def check_mfa_certification(client):
    # MFA未設定のユーザーを格納するリスト
    users_without_mfa = []

    # ユーザーリストの取得
    response = client.list_users()
    users = response['Users']

    for user in users:
        username = user['UserName']
        
        # 各ユーザーのMFAデバイスのリストを取得
        mfa_devices = client.list_mfa_devices(UserName=username)
        
        # MFAデバイスがない場合、リストに追加
        if not mfa_devices['MFADevices']:
            users_without_mfa.append(username)

    return users_without_mfa

# メールを外部テキストファイルから取得
def get_mail_content():
    try:
        with open('mail.txt', 'r', encoding='utf-8') as file:
            mail_content_all = file.read()
            if not mail_content_all:
                raise FileNotFoundError("メールの内容が取得できませんでした。mail.txtが空、もしくは存在しません。") # 例外を送出
            mail_content_split = mail_content_all.split('\n-----ここからメール本文-----\n') # メールを件名と本文で分割. 
            return mail_content_split
    except FileNotFoundError as e:
        print(f"Error: {e}") # エラーログ出力
        raise  # 例外を再送出することでLambdaにエラーを伝える

def send_mail(users_without_mfa, client_mail):
    # メールの件名と本文の取得
    mail_content_split = get_mail_content()
    mail_subject = mail_content_split[0]
    mail_body = mail_content_split[1]

    # 送信元メールアドレスの取得
    from_address = "Yui.Fujiwara@sony.com"
    
    # 送信先メールアドレスのリスト作成
    to_addresses = []
    email = f"Yui.Fujiwara@sony.com"
    to_addresses.append(email)

    """
    このコードを有効にすると、MFAデバイスを持っていないユーザーにメールを送る気がするので無効にしておく
    to_addresses = []
    for username in users_without_mfa:
        # ユーザー名からメールアドレスを生成
        email = f"username"
        to_addresses.append(email)
    """

    # メール送信結果を格納するリスト
    send_results = []
    
    # 各ユーザーにメールを送信
    for to_address in to_addresses:
        try:
            response = client_mail.send_email(
                Source=from_address,
                Destination={
                    'ToAddresses': [to_address]
                },
                Message={
                    'Subject': {
                        'Data': mail_subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': mail_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            send_results.append({
                'to': to_address,
                'status': 'success',
                'message_id': response['MessageId']
            })
        except Exception as e:
            send_results.append({
                'to': to_address,
                'status': 'failed',
                'error': str(e)
            })
    
    return send_results

# main
def lambda_handler(event, context):
    # userのMFAデバイス設定状況確認
    client_user = boto3.client('iam')
    users_without_mfa = check_mfa_certification(client_user)

    # MFAデバイスが無いユーザーにメールを送信
    client_mail = boto3.client('ses')
    mail_results = send_mail(users_without_mfa, client_mail)

    return {
        'users_without_mfa': users_without_mfa,
        'mail_results': mail_results
    }
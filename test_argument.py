def get_mail_content():
    # ファイルをUTF-8エンコーディングで開く
    with open('mail.txt', 'r', encoding='utf-8') as file:
        mail_content_all = file.read()
        if not mail_content_all:
            print("メールの内容が取得できませんでした。")
            exit()
        else:
            print("メールの取得が完了しました。")
        # メールを件名と本文で分割
        mail_content_split = mail_content_all.split('\n-----ここからメール本文-----\n') 
        return mail_content_split 
    
def main():
    # メールの件名と本文を取得
    mail_content_split = get_mail_content()
    mail_subject = mail_content_split[0]
    mail_body = mail_content_split[1]
    
    print(mail_subject, mail_body)

if __name__ == "__main__":
    main()
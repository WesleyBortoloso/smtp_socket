import socket
import ssl
import base64
import getpass

MAIL_SERVER = ("smtp.gmail.com", 465)
BOUNDARY = "myboundary123"

def connect_to_server(mailserver):
    context = ssl.create_default_context()
    client_socket = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=mailserver[0])
    client_socket.connect(mailserver)
    recv = client_socket.recv(1024).decode()
    print("[recv] ok " + recv)
    if recv[:3] != '220':
        raise ConnectionError("220 reply not received from server.")
    return client_socket

def send_command(client_socket, command, expected_code):
    client_socket.send(command.encode())
    recv = client_socket.recv(1024).decode()
    print(f"[recv] rd ath {recv}")
    if recv[:3] != expected_code:
        raise ConnectionError(f"{expected_code} reply not received from server.")
    return recv

def authenticate(client_socket, username, password):
    auth_msg = f"\000{username}\000{password}".encode()
    auth_msg = base64.b64encode(auth_msg).decode()
    send_command(client_socket, f"AUTH PLAIN {auth_msg}\r\n", '235')

def send_email(client_socket, sender_email, receiver_email, subject, msg_text, image_path):
    send_command(client_socket, f"MAIL FROM: <{sender_email}>\r\n", '250')
    
    send_command(client_socket, f"RCPT TO: <{receiver_email}>\r\n", '250')
    
    send_command(client_socket, "DATA\r\n", '354')
    
    email_message = build_mime_message(sender_email, receiver_email, subject, msg_text, image_path)
    client_socket.send(email_message.encode())
    client_socket.send("\r\n.\r\n".encode())
    send_command(client_socket, "", '250')

def build_mime_message(sender_email, receiver_email, subject, msg_text, image_path):
    with open(image_path, "rb") as img_file:
        image_data = base64.b64encode(img_file.read()).decode()
    
    return f"""\
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/related; boundary="{BOUNDARY}"

--{BOUNDARY}
Content-Type: text/html; charset="utf-8"

<html>
  <body>
    <p>{msg_text}</p>
    <img src="cid:image1">
  </body>
</html>

--{BOUNDARY}
Content-Type: image/jpeg
Content-Transfer-Encoding: base64
Content-ID: <image1>

{image_data}
--{BOUNDARY}--
"""

def main():
    client_socket = connect_to_server(MAIL_SERVER)
    
    send_command(client_socket, "HELO example.com\r\n", '250')
    
    username = input("Insert username: ")
    password = getpass.getpass(prompt="\nInsert Password: ")
    authenticate(client_socket, username + "@gmail.com", password)
    
    receiver_email = input("Send email to: ")
    subject = input("Subject: ")
    msg_text = input("Message: ")
    image_path = "redes.png" 
    
    send_email(client_socket, username + "@gmail.com", receiver_email, subject, msg_text, image_path)
    
    send_command(client_socket, "QUIT\r\n", '221')
    client_socket.close()

if __name__ == "__main__":
    main()

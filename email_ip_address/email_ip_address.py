import smtplib
import requests
import logging
import time
from logging import handlers
from email.mime.text import MIMEText
from email.header import Header
_logger = logging.getLogger("email_ip_address")
_logger.setLevel(logging.INFO)
_handler = handlers.TimedRotatingFileHandler(filename='email_ip_address.log', when='D', backupCount=3)
_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
_logger.addHandler(_handler)

class IpEmail:
    def __init__(self, subject):
        # 发送邮件
        self.ip = None
        self.subject = subject
        self.smtp_server = 'smtp.qq.com'
        self.smtp_port = 587
        self.sender_email = '1549971272@qq.com'
        self.password = 'nzkclehyxbcrihcg'  # 在QQ邮箱设置里拿到的码

    def get_msg_info(self):
        # 构建邮件
        ip = self.get_ip_address()
        if ip:
            _msg = MIMEText(self.ip, 'plain', 'utf-8')
            _msg['Subject'] = Header(self.subject, 'utf-8')
            _msg['From'] = '1549971272@qq.com'
            _msg['To'] = '1549971272@qq.com'
            return _msg
        return False

    def get_ip_address(self):
        ip = requests.get('https://checkip.amazonaws.com').text.strip()
        if ip == self.ip:
            return False
        self.ip = ip
        return ip

    def login(self, server):
        try:
            server.starttls()
            server.login(self.sender_email, self.password)
            _logger.info('登录成功')
        except smtplib.SMTPException as e:
            _logger.error('登录失败:%s' % str(e))

    def send_message(self, server):
        try:
            msg = self.get_msg_info()
            if msg:
                server.sendmail(self.sender_email, [msg['To']], msg.as_string())
                _logger.info('邮件发送成功: %s' % self.ip)
            else:
                _logger.info('当前IP未发生变化')
        except smtplib.SMTPException as e:
            _logger.error('邮件发送失败:%s' % str(e))

    def run(self):
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            self.login(server)
            while True:
                self.send_message(server)
                time.sleep(1 * 60)


if __name__ == '__main__':
    # 邮件内容
    email = IpEmail('阿里云IP')
    email.run()

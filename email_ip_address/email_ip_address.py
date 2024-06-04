import time
import smtplib
import requests
import socket
import struct
import fcntl
import logging
import configparser
from logging import handlers
from email.header import Header
from email.mime.text import MIMEText

_config = configparser.ConfigParser()
_config.read("/root/smart_home_public_net/service.conf")
_logger = logging.getLogger("email_ip_address")
_logger.setLevel(logging.INFO)
_handler = handlers.TimedRotatingFileHandler(filename="email_ip_address.log", when="D", backupCount=3)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))
_logger.addHandler(_handler)

class IpEmail:
    def __init__(self):
        # 发送邮件
        self.ip = None
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 587
        self.net_type = _config.get("common", "net_type")
        self.title = _config.get("common", "title")
        self.email = _config.get("email", "user") + "@qq.com"
        self.email_smtp = _config.get("email", "smtp_key")

    def get_msg_info(self):
        # 构建邮件
        ip = self.get_ip_address()
        if ip:
            _msg = MIMEText(self.ip, "plain", "utf-8")
            _msg["Subject"] = Header(self.title, "utf-8")
            _msg["From"] = self.email
            _msg["To"] = self.email
            return _msg
        return False

    @staticmethod
    def get_ip_with_in():
        # 创建一个UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到公共的DNS服务器（8.8.8.8）
        sock.connect(("8.8.8.8", 80))
        # 获取本地IP地址
        return sock.getsockname()[0]

    @staticmethod
    def get_ip_with_out(url="https://checkip.amazonaws.com"):
        return requests.get(url).text.strip()

    def get_ip_address(self):
        ip = ""
        if self.net_type == "in":
            ip = self.get_ip_with_in()
        else:
            ip = self.get_ip_with_out()
        if ip == self.ip:
            return False
        self.ip = ip
        return ip

    def login(self, server):
        try:
            server.starttls()
            server.login(self.email, self.email_smtp)
            _logger.info("登录成功")
        except smtplib.SMTPException as e:
            _logger.error("登录失败:%s" % str(e))

    def send_message(self, server):
        try:
            msg = self.get_msg_info()
            if msg:
                server.sendmail(self.email, [msg["To"]], msg.as_string())
                _logger.info("邮件发送成功: %s" % self.ip)
            else:
                _logger.info("当前IP未发生变化")
        except Exception as e:
            _logger.error("邮件发送失败:%s" % str(e))

    def run(self):
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            self.login(server)
            while True:
                self.send_message(server)
                time.sleep(1 * 60)


if __name__ == "__main__":
    # 邮件内容
    email = IpEmail()
    email.run()


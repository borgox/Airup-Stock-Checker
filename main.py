from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests
import time
from datetime import datetime
from enum import Enum
import os
from plyer import notification
from colorama import Fore, Style, init
from abc import ABC, abstractmethod

# Initialize colorama
init(autoreset=True)

class NotificationStatus(Enum):
    """Enumeration for possible notification statuses"""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

@dataclass
class ProductConfig:
    """Configuration for the product to check"""
    url: str
    cart_id: str
    bottle_handle: str
    flavor_handle: str
    country: str
    language: str

@dataclass
class Statistics:
    """Track check statistics"""
    total_checks: int = 0
    in_stock_count: int = 0
    out_of_stock_count: int = 0
    error_count: int = 0

    def update_title(self) -> None:
        """Update console title with current statistics"""
        title = f"AirUp Checker | No Stock: {self.out_of_stock_count} | Stock: {self.in_stock_count}"
        # Make sure to escape special characters for Windows
        title = title.replace("(", "^(").replace(")", "^)").replace("!", "^!").replace("^", "^^").replace("&", "^&").replace("|", "^|").replace("<", "^<").replace(">", "^>")
        if os.name == "nt":
            os.system(f"title {title}")
        else:
            os.system(f"echo -en '\033]0;{title}\a'")

class NotificationService(ABC):
    """Abstract base class for notification services"""
    @abstractmethod
    def send_notification(self, title: str, message: str, status: NotificationStatus) -> None:
        pass

class DesktopNotificationService(NotificationService):
    """Desktop notification implementation"""
    def send_notification(self, title: str, message: str, status: NotificationStatus) -> None:
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )

class DiscordNotificationService(NotificationService):
    """Discord webhook notification implementation"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_notification(self, title: str, message: str, status: NotificationStatus) -> None:
        color_map = {
            NotificationStatus.SUCCESS: 0x00FF00,  # Green
            NotificationStatus.ERROR: 0xFF0000,    # Red
            NotificationStatus.INFO: 0x00FFFF,     # Cyan
            NotificationStatus.WARNING: 0xFFFF00    # Yellow
        }

        emoji_map = {
            NotificationStatus.SUCCESS: "✅",
            NotificationStatus.ERROR: "❌",
            NotificationStatus.INFO: "ℹ️",
            NotificationStatus.WARNING: "⚠️"
        }

        embed = {
            "title": f"{emoji_map[status]} {title}",
            "description": message,
            "color": color_map[status],
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Check Statistics",
                    "value": f"Total Checks: {self.statistics.total_checks}\n"
                            f"In Stock Count: {self.statistics.in_stock_count}\n"
                            f"Out of Stock Count: {self.statistics.out_of_stock_count}\n"
                            f"Error Count: {self.statistics.error_count}",
                    "inline": False
                }
            ]
        }

        payload = {"embeds": [embed]}
        requests.post(self.webhook_url, json=payload)

class ConsoleLogger:
    """Handles console output with colors"""
    @staticmethod
    def log(message: str, status: NotificationStatus) -> None:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        color_map = {
            NotificationStatus.SUCCESS: Fore.GREEN,
            NotificationStatus.ERROR: Fore.RED,
            NotificationStatus.INFO: Fore.CYAN,
            NotificationStatus.WARNING: Fore.YELLOW
        }
        print(f"{color_map[status]}[{timestamp}] {message}")

class AirUpChecker:
    """Main class for checking AirUp bottle availability"""
    def __init__(
        self,
        product_config: ProductConfig,
        notification_services: list[NotificationService],
        logger: ConsoleLogger,
        statistics: Statistics
    ):
        self.product_config = product_config
        self.notification_services = notification_services
        self.logger = logger
        self.statistics = statistics
        self.headers = self._get_default_headers()
        
        # Share statistics with notification services
        for service in self.notification_services:
            if isinstance(service, DiscordNotificationService):
                service.statistics = statistics

    def _get_default_headers(self) -> Dict[str, str]:
        return {
            "accept": "text/x-component",
            "accept-language": "it-IT,it;q=0.8",
            "cache-control": "no-cache",
            "content-type": "text/plain;charset=UTF-8",
            "next-action": "0bcc478922f9079b84673665f217b86d54bdfbb4",
            "sec-ch-ua": "\"Brave\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
        }

    def _get_request_body(self) -> str:
        return f'[{{"cartId":"{self.product_config.cart_id}",' \
               f'"bottleHandle":"{self.product_config.bottle_handle}",' \
               f'"flavorHandle":"{self.product_config.flavor_handle}",' \
               f'"country":"{self.product_config.country}",' \
               f'"language":"{self.product_config.language}"}}]'

    def check_availability(self) -> bool:
        self.statistics.total_checks += 1
        try:
            response = requests.post(
                self.product_config.url,
                headers=self.headers,
                data=self._get_request_body()
            )
            
            if response.status_code == 200:
                if "OUT_OF_STOCK" in response.text:
                    self.statistics.out_of_stock_count += 1
                    self.logger.log("Still out of stock...", NotificationStatus.WARNING)
                    self.statistics.update_title()
                    return False
                else:
                    self.statistics.in_stock_count += 1
                    self.logger.log("IN STOCK! Sending notifications...", NotificationStatus.SUCCESS)
                    self._notify_all("AirUp Charcoal Grey Bottle Available!",
                                   "The classic AirUp bottle in Charcoal Grey is now in stock. Go buy it!",
                                   NotificationStatus.SUCCESS)
                    self.statistics.update_title()
                    return True
            else:
                self.statistics.error_count += 1
                self.logger.log(f"Unexpected status code: {response.status_code}", NotificationStatus.ERROR)
                self.statistics.update_title()
                return False

        except requests.exceptions.RequestException as e:
            self.statistics.error_count += 1
            self.logger.log(f"Error checking availability: {e}", NotificationStatus.ERROR)
            self.statistics.update_title()
            return False

    def _notify_all(self, title: str, message: str, status: NotificationStatus) -> None:
        for service in self.notification_services:
            try:
                service.send_notification(title, message, status)
            except Exception as e:
                self.logger.log(f"Error sending notification via {service.__class__.__name__}: {e}",
                              NotificationStatus.ERROR)

def main() -> None:
    # Clear console
    os.system("cls" if os.name == "nt" else "clear")

    # Initialize statistics
    statistics = Statistics()
    statistics.update_title()

    # Initialize configuration and services
    product_config = ProductConfig(
        url="https://shop.air-up.com/it/en/bottles/classic/bottle-tritan-650ml-charcoal-grey-us", # Replace with POST url link
        cart_id="your_cart_id_here",
        bottle_handle="bottle-tritan-650ml-charcoal-grey-us", # Replace with other bottles
        flavor_handle="3-pod-variety-pack-vivid-vibes-udb", # Replace with other flavors if needed
        country="it", # Replace w your country
        language="en" # Replace w your language
    )

    notification_services = [
        DesktopNotificationService(),
        DiscordNotificationService("your_webhook_link_here")
    ]

    logger = ConsoleLogger()
    checker = AirUpChecker(product_config, notification_services, logger, statistics)

    # Start checking
    logger.log("Starting availability checker for AirUp Charcoal Grey bottle...", NotificationStatus.INFO)
    
    while True:
        if checker.check_availability():
            logger.log("Stopping script as item is in stock.", NotificationStatus.SUCCESS)
            break
            
        logger.log("Waiting 5 minutes before the next check...", NotificationStatus.INFO)
        print()
        time.sleep(300)

if __name__ == "__main__":
    main()

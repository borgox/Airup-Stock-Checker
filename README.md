# AirUp Availability Checker

A professional, object-oriented Python script that monitors the availability of AirUp bottles and notifies you through desktop notifications and Discord webhooks when they become available.

## Features

- 🔄 Real-time availability monitoring
- 🖥️ Desktop notifications
- 📱 Discord webhook integration with rich embeds
- 📊 Statistics tracking
- 🎨 Color-coded console output
- 💻 Cross-platform support (Windows/Linux/macOS)

## Requirements

```bash
pip install requests plyer colorama
```

## Configuration
### (You can get all the values from inspecting airup's requests when pressing "Add to cart")
1. Replace the following values in `main()`:
   ```python
   product_config = ProductConfig(
       url="your_airup_post_url",
       cart_id="your_cart_id",
       bottle_handle="desired_bottle_handle",
       flavor_handle="desired_flavor_handle",
       country="your_country_code",
       language="your_language_code"
   )
   ```

2. Set up Discord notifications (optional):
   ```python
   DiscordNotificationService("your_discord_webhook_url")
   ```

## Usage

1. Clone the repository
2. Install dependencies
3. Configure the script
4. Run:
   ```bash
   python main.py
   ```

## Features Breakdown

### Notification Systems
- Desktop notifications via `plyer`
- Discord webhook integration with:
  - Color-coded embeds
  - Emoji status indicators
  - Real-time statistics

### Statistics Tracking
- Total checks performed
- In-stock count
- Out-of-stock count
- Error count
- Live console title updates

### Console Output
- Color-coded status messages
- Timestamp for each check
- Clear status indicators

## Class Structure

### Main Components
- `AirUpChecker`: Core checking logic
- `NotificationService`: Abstract base for notifications
- `Statistics`: Tracks checking statistics
- `ProductConfig`: Stores product configuration
- `ConsoleLogger`: Handles console output

### Status Types
```python
class NotificationStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
```

## Error Handling

The script includes comprehensive error handling for:
- Network issues
- API response errors
- Notification service failures
- Invalid configurations

## Customization

You can easily extend the script by:
1. Adding new notification services
2. Modifying check intervals
3. Customizing notification formats
4. Adding new statistics tracking

## License

MIT License

## Contributing

Feel free to submit issues and pull requests for:
- New features
- Bug fixes
- Documentation improvements
- Code optimization

## Disclaimer

This script is for educational purposes only. Please respect AirUp's terms of service and API usage guidelines.

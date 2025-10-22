# Discord Trading Bot - Finviz Elite Integration

A sophisticated Discord bot that monitors top-performing stocks from Finviz Elite and sends intelligent, automated alerts when significant price changes occur. Built for active traders who need real-time notifications with actionable insights.

## ✨ Features

✅ **Live Finviz Elite API Integration** - Fetches real-time data directly from your Finviz Elite account (no CSV delays)  
✅ **Smart Threshold Notifications** - Only sends alerts when a stock's change increases by +3% or more (prevents spam)  
✅ **Delta Display** - Shows exact increase amount: "ACRS increased by +3.5% from last check"  
✅ **Before/After Tracking** - Visual comparison: "Previous: 12.02% → Current: 15.52%"  
✅ **Comprehensive Performance Metrics** - Price, Monthly Performance, YTD Performance, and more  
✅ **Top 3 Latest News** - Full summaries from YahooNews.csv with links for each ticker  
✅ **Intelligent Change Tracking** - Persistent tracking to detect significant movements over time  
✅ **Earnings Date Display** - Shows upcoming earnings dates for planning  
✅ **Discord Commands** - Manual triggers and control commands for testing and management  
✅ **Error Handling** - Gracefully handles missing data, API errors, and network issues  

## 📋 Requirements

- Python 3.7+
- Discord Bot Token
- Finviz Elite Account (with auth token)
- YahooNews.csv file

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project directory:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_trading_channel_id_here

# Optional (defaults already set in code)
FINVIZ_AUTH_TOKEN=512b187b-b9f5-4762-bed0-661ffd5a71c1
FINVIZ_PORTFOLIO_PID=1000799188
```

**How to get Channel ID:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click on your trading channel
3. Click "Copy Channel ID"

### 3. Run the Bot

```bash
python main.py
```

## 🎮 Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `!top5` | Show current top 5 performers (bypasses threshold) | Check current leaders anytime |
| `!force` | Force send notification with all metrics (bypasses threshold) | Testing or immediate update |
| `!reset` | Reset change tracking (next update will notify all) | Start fresh after market changes |
| `!help` | Show help message with all commands | Quick reference guide |

### Command Details

#### `!top5`
- **Purpose**: Manual check of current top performers
- **Behavior**: Fetches live data and displays all top 5 tickers
- **Threshold**: Bypassed (shows all regardless of change)
- **Use When**: You want to see current market leaders on demand

#### `!force`
- **Purpose**: Force a notification similar to automated alerts
- **Behavior**: Same as `!top5` but prefixed with "Forced Update" message
- **Threshold**: Bypassed
- **Use When**: Testing bot functionality or wanting formatted output

#### `!reset`
- **Purpose**: Clear tracking history
- **Behavior**: Deletes `ticker_tracking.json` file
- **Next Check**: Will treat all tickers as new and send notifications
- **Use When**: 
  - After market close/open to reset for new trading day
  - When you want fresh baseline tracking
  - After adjusting threshold settings

#### `!help`
- **Purpose**: Display command reference
- **Behavior**: Shows all commands with brief descriptions
- **Also Shows**: Current check interval and threshold settings

## ⚙️ Configuration

### Customizable Settings in `main.py`

```python
# Change threshold for notifications (in percentage points)
CHANGE_THRESHOLD = 3.0  # Notify only if change increased by 3% or more

# Update interval (in minutes)
UPDATE_INTERVAL_MINUTES = 1  # Testing: 1, Production: 2

# News items per ticker
count=3  # Shows top 3 latest news items (in get_ticker_news function)
```

### Threshold Adjustment Guide

Choose your threshold based on market volatility and trading strategy:

| Threshold | Frequency | Best For |
|-----------|-----------|----------|
| `1.0` | Very High | Day traders, volatile markets |
| `2.0` | High | Active traders, tech stocks |
| `3.0` | **Recommended** | Balanced approach, quality signals |
| `5.0` | Medium | Swing traders, less noise |
| `10.0` | Low | Long-term positions, major moves only |

### Interval Adjustment Guide

| Interval | API Calls/Hour | Best For |
|----------|----------------|----------|
| `1 min` | 60 | Testing, ultra-active trading |
| `2 min` | 30 | **Recommended** - Real-time monitoring |
| `5 min` | 12 | Conservative, less frequent updates |
| `10 min` | 6 | Casual monitoring |

**Note**: Finviz Elite has no rate limits, so choose based on your needs!

## 🔄 How It Works

### Monitoring Flow

**Every 1 minute** (configurable), the bot executes this sequence:

1. **Fetches Live Data** from Finviz Elite API
   - Uses your exact screener filters and columns
   - Retrieves comprehensive stock data
   - No rate limits (Elite allows unlimited requests)

2. **Identifies Top 5 Performers** by "Change from Open"
   - Parses percentage values accurately
   - Sorts by highest gainers
   - Handles edge cases (NaN, missing data)

3. **Compares with Previous Values**
   - Loads tracking data from `ticker_tracking.json`
   - Calculates exact delta for each ticker
   - Determines if threshold is met

4. **Sends Smart Notifications**
   - **Only notifies** if a ticker increased by +3% or more
   - Shows exact increase amount in alert
   - Displays before/after comparison
   - Includes performance metrics and news

### Notification Display

**For each qualifying ticker**, the bot shows:

#### 🔔 Threshold Alert Section
- **Exact increase**: "+3.5% from last check"
- **Before/After**: "Previous: 12.02% → Current: 15.52%"
- **Reason**: NEW entry, THRESHOLD met, or manual trigger

#### 📊 Performance Metrics
- Current price with ticker symbol
- Change from open percentage
- Monthly performance
- Year-to-date (YTD) performance
- Earnings date and time

#### 📰 Latest News (Top 3)
- News title (truncated to 100 chars)
- Full summary (truncated to 250 chars)
- Source and publication date
- Direct link to read more

### Smart Threshold Logic

The bot prevents notification spam with intelligent tracking:

| Scenario | Bot Action | Example |
|----------|------------|---------|
| **First Run** | Notifies all top 5 | Initial baseline established |
| **No Change** | Silent check | ACRS: 10% → 10.5% (only +0.5%) |
| **Threshold Met** | 🔔 Notification | ACRS: 10% → 13.5% (+3.5%) |
| **New to Top 5** | 🔔 Notification | ABCL enters top 5 at 12% |
| **Below Threshold** | Silent check | Multiple small increases |

**Example Timeline:**
```
Minute 0: ACRS at 10.0% → Notification (first run)
Minute 1: ACRS at 10.5% → Silent (only +0.5%)
Minute 2: ACRS at 11.2% → Silent (only +1.2% from last)
Minute 3: ACRS at 13.8% → Notification (+3.8% from 10.0%)
Minute 4: ACRS at 14.0% → Silent (only +0.2% from 13.8%)
```

### Data Persistence

- **Tracking File**: `ticker_tracking.json` (auto-created)
- **Stored Data**: Ticker symbol → Last notified change %
- **Update Frequency**: Every check cycle
- **Reset**: Use `!reset` command to start fresh

## 📊 Data Sources

- **Stock Data**: Finviz Elite API (live, unlimited requests)
- **News Data**: YahooNews.csv (local file)

## 🔧 Finviz Elite Integration

The bot uses your existing Finviz Elite configuration from `fetch_finviz_data.sh`:
- Auth Token: Authenticates with Finviz Elite
- Same filters: Uses identical screener filters as your shell script
- Same columns: Fetches the same data columns

This means:
- ✅ Unlimited API calls (Finviz Elite allows it)
- ✅ Real-time data every 1-2 minutes
- ✅ No CSV dependency (fetches fresh data each time)
- ✅ Consistent with your existing data pipeline

## 📝 Example Output

### Threshold Alert (Stock Increased by 3%+)

```
📈 Top Performers - Live from Finviz Elite
🔔 2 ticker(s) met the +3.0% threshold
Updated: 2025-10-22 04:30:15

🚀 #1 - ACRS - $2.35 (+3.5% increase)

🔔 Threshold Alert:
• Increased by +3.5% from last check
• Previous: 12.02% → Current: 15.52%

📊 Performance:
• Change from Open: 15.52%
• Monthly: 21.50%
• YTD: 39.58%
• Earnings: 8/7/2025 8:30:00 AM

📰 Latest News:

1. ACRS Announces Positive Phase 2 Trial Results
ACRS Corporation reported strong preliminary data from its Phase 2 clinical trial, 
showing significant improvement in patient outcomes compared to placebo group. 
The company expects to publish full results next quarter...
Read More • 2025-10-22 03:45 UTC

2. Healthcare Sector Rally Continues as Biotech Gains
Multiple biotechnology stocks including ACRS saw substantial gains today as 
investors responded positively to sector-wide developments...
Read More • 2025-10-22 02:15 UTC

3. Analyst Upgrades ACRS to Buy Rating
Major investment firm upgraded ACRS from Hold to Buy with a price target...
Read More • 2025-10-22 01:30 UTC
```

### New Entry Alert

```
🆕 #2 - ABCL - $5.62 (New to Top 5)

🔔 Threshold Alert:
• NEW entry to top 5
• Previous: Not tracked → Current: -3.02%

📊 Performance:
• Change from Open: -3.02%
• Monthly: 16.46%
• YTD: 12.73%
• Earnings: 11/6/2025 4:30:00 PM

📰 Latest News:
...
```

### Manual Trigger (!top5 command)

```
📊 #1 - ACRS - $2.35

📊 Performance:
• Change from Open: 15.52%
• Monthly: 21.50%
• YTD: 39.58%
• Earnings: 8/7/2025 8:30:00 AM

📰 Latest News:
...
```

## 🛠️ Troubleshooting

### Common Issues

#### Bot not sending notifications?

**Symptoms**: Bot runs but no Discord messages appear

**Solutions**:
1. **Check threshold logic**: Changes might not meet +3% increase
   - View console: Look for "No significant changes" messages
   - Use `!force` to test notification system
   - Use `!reset` to clear tracking and start fresh

2. **Verify Discord permissions**:
   - Bot needs "Send Messages" permission
   - Bot needs "Embed Links" permission
   - Check bot role in server settings

3. **Check Channel ID**:
   - Verify `CHANNEL_ID` in `.env` is correct
   - Console shows "Could not find channel" if incorrect

#### Can't fetch Finviz data?

**Symptoms**: Console shows "Error fetching from Finviz Elite API"

**Solutions**:
1. **Verify auth token**:
   - Check `FINVIZ_AUTH_TOKEN` in `.env` or `main.py`
   - Ensure token hasn't expired
   - Test in browser: Use same URL from `fetch_finviz_data.sh`

2. **Network issues**:
   - Check internet connection
   - Test: `curl https://elite.finviz.com`
   - Check firewall settings

3. **Subscription status**:
   - Ensure Finviz Elite subscription is active
   - Login to Finviz Elite to verify access

#### News not showing?

**Symptoms**: Performance data shows but "No recent news available"

**Solutions**:
1. **File location**:
   - Verify `YahooNews.csv` exists in same directory as `main.py`
   - Check file path in `NEWS_CSV` variable

2. **Symbol mismatch**:
   - News CSV uses `symbol` column matching ticker names
   - Compare ticker format between Finviz and news CSV
   - Check for symbol aliases (e.g., "BRK.B" vs "BRK-B")

3. **Data format**:
   - Ensure CSV has required columns: `date`, `symbol`, `title`, `summary`, `link`
   - Check for corrupted CSV data

#### Error: "object of type 'float' has no len()"

**Status**: ✅ **Fixed** in latest version

**What was it**: Some news summaries were NaN (null values)

**Solution applied**: Added null checks and type conversion

#### Pandas SettingWithCopyWarning

**Status**: ✅ **Fixed** in latest version

**What was it**: DataFrame modification warning

**Solution applied**: Using `.copy()` and proper `.loc[]` assignment

### Debug Mode

Enable detailed logging by checking console output:

```bash
python main.py
```

Console will show:
- `📡 Fetching live data from Finviz Elite API...`
- `✅ Fetched X tickers from Finviz Elite`
- `📝 First run - tracking all tickers`
- `🆕 TICKER is new to top 5: X.XX%`
- `🔔 TICKER change increased by X.XX%`
- `[TIMESTAMP] No significant changes`
- `[TIMESTAMP] Report sent! X ticker(s) met threshold`

### Getting Help

If issues persist:
1. Check console logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test with `!top5` command to isolate the issue
4. Check Discord bot permissions in server settings
5. Ensure all dependencies are installed: `pip install -r requirements.txt`

## 📁 Project Structure

```
DiscordBots/
├── main.py                      # Main bot application (466 lines)
├── requirements.txt             # Python dependencies
├── README.md                    # This file - comprehensive documentation
├── .env                         # Environment variables (YOU CREATE THIS)
├── .gitignore                   # Git ignore file (recommended)
│
├── ticker_tracking.json         # Auto-generated tracking data
├── YahooNews.csv               # News data source (127K+ lines)
├── finviz_data.csv             # Optional: Local Finviz data cache
│
├── fetch_finviz_data.sh        # Your existing data fetching script (reference only)
└── bot.log                     # Auto-generated log file (if logging enabled)
```

### File Descriptions

#### Core Files (Required)

**`main.py`** (466 lines)
- Main bot application with all logic
- Fetches data from Finviz Elite API
- Manages Discord connection and commands
- Handles threshold detection and notifications
- Includes error handling and logging

**`requirements.txt`**
```
discord.py      # Discord API wrapper
python-dotenv   # Environment variable management
pandas          # Data processing and CSV handling
requests        # HTTP requests to Finviz Elite
```

**`.env`** (You must create)
```env
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ID=1234567890123456789
# Optional overrides:
# FINVIZ_AUTH_TOKEN=your_token
# FINVIZ_PORTFOLIO_PID=your_pid
```

**`YahooNews.csv`** (127,289+ lines)
- News data source with columns: date, symbol, title, summary, source, link
- Updated by your data pipeline
- Bot reads this for news display

#### Auto-Generated Files

**`ticker_tracking.json`**
- Created on first run
- Stores last known change % for each ticker
- Updated every check cycle
- Format: `{"ACRS": 12.02, "AAOI": 8.35, ...}`
- Can be deleted with `!reset` command

**`bot.log`** (Optional)
- Created if logging is enabled
- Contains timestamped events and errors
- Useful for debugging and monitoring

#### Reference Files (Optional)

**`fetch_finviz_data.sh`**
- Your existing shell script
- Downloads Finviz data to CSV
- **Not used by bot** (bot uses API directly)
- Kept as reference for filters and configuration

**`finviz_data.csv`** (Optional)
- Static snapshot from shell script
- **Not used by bot** (bot fetches live data)
- Can be used for testing or backup

## 🔐 Security Notes

- Never commit your `.env` file to git
- Keep your Discord token and Finviz auth token private
- The auth tokens are stored as defaults in code for convenience, but can be overridden via .env

## 🎯 Production Recommendations

### Before Going Live

1. **Adjust Timing** (Line 32 in `main.py`)
   ```python
   UPDATE_INTERVAL_MINUTES = 2  # Change from 1 to 2
   ```
   - Reduces API calls while maintaining real-time monitoring
   - Still checks every 2 minutes (30 calls/hour)

2. **Fine-tune Threshold** (Line 29 in `main.py`)
   ```python
   CHANGE_THRESHOLD = 3.0  # Adjust based on your trading style
   ```
   - Start with 3.0% and adjust based on notification frequency
   - Higher = fewer notifications, lower = more alerts

3. **Test Thoroughly**
   ```bash
   # Test manual commands
   # In Discord: !top5, !force, !reset, !help
   
   # Monitor console output
   python main.py
   
   # Watch for first automated notification
   # Verify threshold logic works correctly
   ```

4. **Run as Background Service**
   
   **Option A: Using `screen` (simple)**
   ```bash
   screen -S discord-bot
   python main.py
   # Press Ctrl+A, then D to detach
   # Reconnect with: screen -r discord-bot
   ```
   
   **Option B: Using `systemd` (recommended)**
   ```bash
   # Create service file: /etc/systemd/system/discord-bot.service
   [Unit]
   Description=Discord Trading Bot
   After=network.target
   
   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/DiscordBots
   ExecStart=/usr/bin/python3 /path/to/DiscordBots/main.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   
   # Enable and start
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   sudo systemctl status discord-bot
   ```
   
   **Option C: Using `pm2` (Node.js-based)**
   ```bash
   npm install -g pm2
   pm2 start main.py --name discord-bot --interpreter python3
   pm2 save
   pm2 startup
   ```

5. **Set Up Logging**
   
   Add to `main.py` (after imports):
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('bot.log'),
           logging.StreamHandler()
       ]
   )
   ```

6. **Monitor Performance**
   - Check `bot.log` regularly for errors
   - Monitor `ticker_tracking.json` for data integrity
   - Watch Discord for notification accuracy
   - Review console output for API issues

7. **Security Hardening**
   - Never commit `.env` file to git
   - Add to `.gitignore`:
     ```
     .env
     ticker_tracking.json
     bot.log
     __pycache__/
     *.pyc
     ```
   - Restrict file permissions: `chmod 600 .env`
   - Use environment variables in production (not hardcoded tokens)

8. **Backup Strategy**
   - Backup `ticker_tracking.json` periodically
   - Keep `YahooNews.csv` updated via your pipeline
   - Document your configuration settings

### Performance Optimization

- **For 24/7 operation**: Use `UPDATE_INTERVAL_MINUTES = 2`
- **For market hours only**: Add time-based checks to skip off-hours
- **For multiple channels**: Duplicate bot or add channel list support
- **For different thresholds**: Create multiple tracking files per strategy

### Monitoring Checklist

Daily:
- [ ] Check console/log for errors
- [ ] Verify notifications are being sent
- [ ] Confirm threshold logic is working

Weekly:
- [ ] Review notification frequency (too many/few?)
- [ ] Check Finviz Elite API response times
- [ ] Update YahooNews.csv if needed

Monthly:
- [ ] Verify Finviz Elite subscription is active
- [ ] Review and adjust threshold if needed
- [ ] Clean up old log files
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`

## 📞 Support

If the bot encounters errors, check:
1. Console logs for detailed error messages
2. Discord bot permissions (send messages, embed links)
3. Finviz Elite API status
4. YahooNews.csv file accessibility

---

## 🔑 Key Features Explained

### 1. Real-Time Delta Display
Shows exactly why a notification was triggered:
- `"+3.5% increase"` - Clear, actionable information
- `"Previous: 12.02% → Current: 15.52%"` - Visual before/after
- Helps you understand momentum and timing

### 2. Smart Threshold Logic
Prevents notification fatigue:
- Tracks changes over time, not just current values
- Only alerts on significant moves (+3% default)
- Distinguishes between new entries and threshold triggers

### 3. Comprehensive Data Display
Everything you need in one message:
- Price, change %, monthly, YTD performance
- Top 3 news items with full context
- Earnings dates for planning
- Direct links to news articles

### 4. Flexible Commands
Control the bot your way:
- Manual checks with `!top5`
- Testing with `!force`
- Reset tracking with `!reset`
- Help reference with `!help`

## 📊 Technical Details

### API Integration
- **Endpoint**: Finviz Elite Export API
- **Method**: GET request with authentication token
- **Response Format**: CSV data
- **Columns**: 44 data points per stock
- **Filters**: Matches your existing `fetch_finviz_data.sh` configuration
- **Rate Limit**: None (Finviz Elite allows unlimited)

### Data Processing
- **Library**: Pandas for efficient CSV parsing
- **Sorting**: By "Change from Open" column (descending)
- **Top N**: Selects top 5 performers
- **Type Handling**: Robust parsing of percentage strings
- **Error Handling**: Graceful handling of NaN, missing data

### Threshold Algorithm
```python
For each ticker in top 5:
    current_change = ticker.change_from_open
    
    If ticker not in tracking:
        → Notify (NEW entry)
    Else:
        previous_change = tracking[ticker]
        delta = current_change - previous_change
        
        If delta >= CHANGE_THRESHOLD:
            → Notify (THRESHOLD met)
        Else:
            → Skip (below threshold)
    
    Update tracking[ticker] = current_change
```

### Discord Integration
- **Library**: discord.py (async)
- **Message Type**: Rich Embeds
- **Color Coding**: Gold for alerts, Blue for manual
- **Character Limits**: 
  - Embed title: 256 chars
  - Embed description: 4096 chars
  - Field name: 256 chars
  - Field value: 1024 chars (handled with truncation)
  - Total embeds: 10 per message

## 🆚 Comparison: API vs CSV Approach

| Aspect | Live API (Current) | CSV Approach (Alternative) |
|--------|-------------------|---------------------------|
| Data Freshness | Real-time (1-2 min) | Depends on update script |
| Latency | Low (~1 sec) | Varies |
| Dependencies | None (API only) | Requires cron job / scheduler |
| Reliability | High (direct source) | Depends on script uptime |
| Maintenance | Low | Medium (manage CSV updates) |
| Flexibility | High | Medium |
| Cost | $0 (Elite included) | $0 |

**Verdict**: Live API is superior for real-time trading notifications.

## 🚀 Future Enhancements

Potential features to consider:

- [ ] Multi-channel support (different thresholds per channel)
- [ ] Customizable news sources (Finviz news API)
- [ ] Technical indicators (RSI, MACD, Volume)
- [ ] Price alerts (above/below specific price)
- [ ] Portfolio tracking (specific watchlist)
- [ ] Historical trend charts (matplotlib)
- [ ] Email notifications (fallback)
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Multiple threshold levels (minor/major alerts)
- [ ] Market hours awareness (skip off-hours)
- [ ] Sector filtering (healthcare only, tech only, etc.)
- [ ] Volume spike detection
- [ ] Social sentiment integration

## 📚 Additional Resources

### Discord Bot Setup
1. Create bot: https://discord.com/developers/applications
2. Enable intents: Message Content, Server Members
3. Get token: Bot → Token → Copy
4. Invite bot: OAuth2 → URL Generator → bot → permissions → Copy URL
5. Required permissions: Send Messages, Embed Links, Read Message History

### Finviz Elite
- Website: https://elite.finviz.com
- Pricing: Check current rates
- API Access: Included with Elite subscription
- Documentation: Limited (reverse-engineered from web interface)

### Python Resources
- discord.py docs: https://discordpy.readthedocs.io/
- pandas docs: https://pandas.pydata.org/docs/
- requests docs: https://requests.readthedocs.io/

---

**Built with:**
- **discord.py** - Discord API wrapper for async bot operations
- **pandas** - Data processing, CSV parsing, and analysis
- **requests** - HTTP client for Finviz Elite API calls
- **python-dotenv** - Environment variable management

**Version**: 1.0.0 (October 2025)  
**Python**: 3.7+  
**License**: Use as needed for personal trading  
**Disclaimer**: For educational and personal use. Not financial advice.

# stocks-co

# Discord Trading Bot - Finviz Elite Integration

A sophisticated Discord bot that monitors top-performing stocks from Finviz Elite and sends intelligent, automated alerts when significant price changes occur. Built for active traders who need real-time notifications with actionable insights.

## ✨ Features

✅ **Live Finviz Elite API Integration** - Fetches real-time data directly from your Finviz Elite account (no CSV delays)  
✅ **Full Spectrum Momentum Tracking** - Monitors ALL 568+ stocks for +3% momentum gains  
✅ **Smart Context Display** - Shows top 5 daily gainers with momentum alerts highlighted  
✅ **Delta Display** - Shows exact increase amount: "Increased by +3.5% from last check"  
✅ **Before/After Tracking** - Visual comparison: "Previous: 12.02%"  
✅ **Comprehensive Performance Metrics** - Price, YTD Performance, Earnings Date  
✅ **Latest News Integration** - Clickable news titles with publication dates from YahooNews.csv  
✅ **Persistent Tracking** - Tracks all stocks silently for historical comparisons  
✅ **Finviz Chart Links** - Direct links to Finviz Elite chart view for each ticker  
✅ **Discord Commands** - Manual triggers and control commands for testing and management  
✅ **Error Handling** - Gracefully handles missing data, API errors, and network issues  
✅ **Professional UI** - Clean, color-coded displays (green for gains, red for losses)  

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
UPDATE_INTERVAL_MINUTES = 2  # Checks every 2 minutes for momentum gains

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

**Every 2 minutes** (configurable), the bot executes this sequence:

1. **Fetches Live Data** from Finviz Elite API
   - Retrieves ALL 568+ stocks from your Finviz screener
   - Uses your exact screener filters and columns
   - No rate limits (Elite allows unlimited requests)

2. **Tracks ALL Stocks for Momentum Changes**
   - Compares current percentage with last tracked value
   - Identifies stocks that gained +3% or more since last check
   - Maintains persistent tracking for ALL stocks (silent tracking)

3. **Identifies Top 5 Daily Gainers for Context**
   - Sorts all stocks by "Change from Open" (descending)
   - Selects top 5 current performers
   - Highlights which ones also met the momentum threshold

4. **Sends Smart Notifications**
   - **Only sends** when momentum gainers are detected
   - Displays top 5 daily gainers for full market context
   - Uses ▲ icon for momentum alerts, • for others
   - Shows exact increase amount: "Increased by +3.5% from last check"
   - Includes performance metrics and latest news

### Notification Display

**For each ticker in the top 5**, the bot shows:

#### Ticker Header
- **Rank & Status**: ▲ for momentum alerts, • for context
- **Ticker Symbol**: With current price
- **Current Percentage**: Shows gain/loss from open (+25.3%)
- **Finviz Chart Link**: Clickable link to chart view

#### Context Section (Color-Coded)
- **Green**: Increased by +X% from last check
- **Red**: Decreased by X% from last check
- **Explanation**: Shows why it's in the list (momentum alert or top daily gainer)

#### Performance Metrics
- **Previous**: Last tracked percentage value
- **YTD**: Year-to-date performance
- **Earnings**: Upcoming earnings date

#### Latest News (Top 3)
- **Clickable Title**: Direct link to news article
- **Publication Date**: From rssPublished field
- **"Read More"**: Formatted with timestamp

### Smart Momentum Logic

The bot tracks ALL stocks and alerts on momentum, not just position:

| Scenario | Bot Action | Example |
|----------|------------|---------|
| **First Run** | Silent tracking | Establishes baseline for all 568+ stocks |
| **Momentum Gain** | 🔔 Notification | ACRS: 10% → 13.5% (+3.5% gain) |
| **Below Threshold** | Silent check | ACRS: 10% → 10.5% (only +0.5%) |
| **Decrease** | Silent tracking | ACRS: 10% → 9.0% (tracked, no alert) |
| **New Stock** | Silent tracking | First time seen, track silently |

**Example Timeline:**
```
Minute 0: 568 stocks tracked → Silent (first run, baseline)
Minute 2: ACRS 10.0% → 10.5% → Silent (only +0.5%)
Minute 4: ABCD 5.0% → 8.2% → ▲ Notification (+3.2% momentum!)
Minute 6: ACRS 10.5% → 13.8% → ▲ Notification (+3.3% momentum!)
Minute 8: EFGH 15.0% → 14.5% → Silent (decrease tracked, no alert)

Notification shows: Top 5 daily gainers, with ▲ for ACRS & ABCD
```

## 🔧 Recent Improvements & Bug Fixes

### Version 2.0 - Full Spectrum Momentum Tracking (October 2025)

#### Major Overhaul: From Top 5 Tracking to Full Portfolio Monitoring

**What Changed:**
- **Before**: Only tracked the top 5 daily gainers for threshold changes
- **After**: Monitors ALL 568+ stocks from Finviz screener for momentum gains

#### Key Improvements

**1. Universal Momentum Detection**
- Tracks every stock in your Finviz screener (not just top 5)
- Detects +3% momentum gains across entire portfolio
- Never misses a momentum move, even in stocks outside top 5

**2. Smart Context Display**
- Shows top 5 daily gainers when momentum alerts trigger
- Highlights which stocks have momentum (▲) vs. context (•)
- Provides full market picture while focusing on alerts

**3. Simplified News Display**
- New CSV format: `symbol,"title","link","body","rssPublished"`
- Title is now a clickable link (cleaner presentation)
- Shows publication date only (removed redundant summary)

**4. Enhanced Tracking Logic**
- **New stocks**: Tracked silently (no alert on first appearance)
- **Increases +3%**: Momentum alert triggered
- **Decreases**: Tracked silently (no negative alerts)
- **All changes**: Maintained in persistent tracking

**5. UI/UX Improvements**
- Reduced emoji usage for professional appearance
- Color-coded changes (green for gains, red for losses)
- Direct Finviz chart links (added `&p=d` parameter)
- Consistent percentage format with + signs
- Improved spacing and readability
- Separated tickers with visual hierarchy

**6. Performance Updates**
- Update interval: 2 minutes (was 1 minute)
- Removed redundant HOT_THRESHOLD
- Optimized tracking file management

#### Problem Solved

**Previous Limitation:**
```
Check 1: Top 5 = [A, B, C, D, E]
Check 2: Top 5 = [A, B, C, D, E]
Stock F gains +5% (now at rank #8) → ❌ MISSED! Not in top 5
```

**New Approach:**
```
Check 1: Track all 568 stocks
Check 2: Monitor all 568 stocks
Stock F gains +5% → ✅ DETECTED! Momentum alert triggered
Display: Top 5 daily context + Stock F highlighted if in top 5
```

#### Before vs After Display

**Before (v1.1):**
```
Title: "Top 5 Momentum Gainers - Live Data"
- Only shows stocks that met threshold
- Could display 1-2 tickers if only those gained +3%
- No context for other top performers
```

**After (v2.0):**
```
Title: "Top 5 Daily Gainers - Live Data"
▲ #1 - ACRS - $12.50 (+25.3%)   [Momentum alert: +3.2%]
▲ #2 - ABCD - $8.75 (+18.2%)    [Momentum alert: +4.1%]
• #3 - EFGH - $5.30 (+16.5%)    [Top gainer, increased +0.8%]
• #4 - LUNG - $3.45 (+14.2%)    [Top gainer, decreased -0.3%]
• #5 - VTYX - $2.75 (+12.8%)    [Top gainer, increased +0.5%]
```

#### Console Output Example

**Old:**
```
[2025-10-30 10:00] Report sent! 2 ticker(s) met threshold
```

**New:**
```
Tracking 568 stocks for momentum changes...
✓ ACRS increased by +3.20% (threshold: 3.0%)
✓ ABCD increased by +4.10% (threshold: 3.0%)
Found 2 stocks with +3.0% momentum gain
Showing top 5 daily gainers (2 with momentum alerts, 2 total met threshold)
[2025-10-30 10:00] Report sent! 2 momentum alert(s) in top 5 (2 total met threshold).
```

### Version 1.1 - Persistent Tracking Implementation

#### Problem Solved
The original implementation had a critical tracking bug that caused:
- ❌ Stocks repeatedly marked as "NEW" even when already tracked
- ❌ False alerts when stocks temporarily dropped out of top 5 and returned
- ❌ "Previous: Not tracked" showing for previously tracked stocks
- ❌ Notifications sent even when percentage decreased
- ❌ Historical tracking data lost on each check

#### Root Cause
1. **JSON save bug**: `json.dump()` parameters in wrong order (`json.dump(data, indent=2, fp=f)` instead of `json.dump(data, f, indent=2)`)
2. **Tracking reset bug**: Tracking file completely overwritten on each check, losing historical data

#### Solution Implemented
1. **Fixed `json.dump()` syntax** - Tracking data now saves correctly
2. **Persistent tracking** - Historical data preserved forever (never removed)
3. **Added debug logging** - Shows all comparisons: `"TICKER: X% → Y% (ΔZ%) - No alert"`

#### Before vs After

**Before (Buggy):**
```
Check 1: WHWK at 6.08% → 🆕 NEW entry notification
Check 2: WHWK at 6.31% → 🆕 NEW entry notification (WRONG!)
Check 3: TERN at 6.09% → 🆕 NEW entry notification  
Check 4: TERN at 6.22% → 🆕 NEW entry notification (WRONG!)
```

**After (Fixed):**
```
Check 1: WHWK at 6.08% → 🆕 NEW entry notification
Check 2: WHWK at 6.31% → No alert (Δ+0.23%, below 3% threshold)
Check 3: TERN at 6.09% → 🆕 NEW entry notification
Check 4: TERN at 6.22% → No alert (Δ+0.13%, below 3% threshold)
Check 5: WHWK at 9.10% → 🔔 THRESHOLD alert! (Δ+3.02% from 6.08%)
         Display: "Previous: 6.08% → Current: 9.10%"
```

### Data Persistence & Tracking Logic

#### Persistent Tracking System

The bot uses a **persistent tracking approach** that ensures accurate change detection:

- **Tracking File**: `ticker_tracking.json` (auto-created)
- **Stored Data**: Ticker symbol → Last tracked change %
- **Update Strategy**: **Never removes tickers** - once tracked, always tracked
- **Update Frequency**: Every check cycle (updates existing + adds new)
- **Reset**: Use `!reset` command to start fresh

#### How Persistent Tracking Works

**Key Innovation**: The tracking file preserves historical data for ALL tickers that have ever been in the top 5, even after they drop out.

**Example Flow:**
```
Check 1: Top 5 = [IOBT, SABR, UUUU, WHWK, TERN]
Tracking: {IOBT: 19.63, SABR: 18.98, UUUU: 12.53, WHWK: 7.66, TERN: 6.85}

Check 2: Top 5 = [IOBT, SABR, UUUU, GPRO, TERN]  ← WHWK dropped, GPRO new
Tracking: {IOBT: 20.00, SABR: 19.50, UUUU: 13.00, WHWK: 7.66, GPRO: 5.50, TERN: 7.00}
          ↑ WHWK still preserved even though not in current top 5!

Check 3: Top 5 = [IOBT, SABR, WHWK, GPRO, TERN]  ← WHWK returns
Compare: WHWK 7.66% → 10.70% = +3.04% increase
Result: ✅ Threshold alert sent (NOT marked as "NEW")
Display: "Previous: 7.66% → Current: 10.70%"
```

**Why This Matters:**
- ✅ **Accurate comparisons** when stocks re-enter top 5
- ✅ **No false "NEW" alerts** for stocks that temporarily drop out
- ✅ **Reliable threshold detection** based on true historical values
- ✅ **Growing knowledge base** of all significant movers

**Traditional Approach (BAD):**
```python
# Overwrites entire tracking file each time
current_data = {}  # Empty - loses history
for ticker in top_5:
    current_data[ticker] = value
save(current_data)  # Only saves current top 5
```

**Persistent Approach (GOOD):**
```python
# Preserves all historical data
current_data = load_tracking_data()  # Load existing
for ticker in top_5:
    current_data[ticker] = value  # Add/update
save(current_data)  # Saves current + historical
```

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

### Momentum Alert Notification

```
📊 Top 5 Daily Gainers - Live Data
Updated: 2025-10-30 10:15:32

▲ #1 - ACRS - $12.50 (+25.3%)

[View on Finviz](https://elite.finviz.com/quote.ashx?t=ACRS&p=d)

Context:
```ansi
Increased by +3.20% from last check
```

Performance:
Previous: `22.10%`
YTD: `39.58%`
Earnings: 2025-11-15 Before Market Open

Latest News:

`1.` [ACRS Announces Phase 2 Trial Results](https://finance.yahoo.com/news/acrs-announces...)
   Read More • 2025-10-30 08:45

`2.` [Biotech Sector Sees Strong Gains](https://finance.yahoo.com/news/biotech-sector...)
   Read More • 2025-10-30 07:22

`3.` [Analyst Upgrades ACRS Rating](https://finance.yahoo.com/news/analyst-upgrades...)
   Read More • 2025-10-30 06:15

━━━━━━━━━━━━━━━━━━━━━━━━

• #2 - EFGH - $8.75 (+18.2%)

[View on Finviz](https://elite.finviz.com/quote.ashx?t=EFGH&p=d)

Context:
```ansi
Increased by +0.80% from last check
```

Performance:
Previous: `17.40%`
YTD: `52.31%`
Earnings: 2025-12-05 After Market Close

Latest News:
...

━━━━━━━━━━━━━━━━━━━━━━━━

Finviz Elite | Alert Threshold: +3.0%
```

### Manual Check (!top5 command)

```
📊 Top 5 Daily Gainers - Live Data
Updated: 2025-10-30 10:20:15

• #1 - LUNG - $5.30 (+32.1%)

[View on Finviz](https://elite.finviz.com/quote.ashx?t=LUNG&p=d)

Context:
Manual trigger (threshold bypassed)

Performance:
Previous: `31.50%`
YTD: `125.43%`
Earnings: 2025-11-20 Before Market Open

Latest News:
...

Finviz Elite | Alert Threshold: +3.0%
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
├── percentage3cfo.py            # Main bot application (559 lines)
├── requirements.txt             # Python dependencies
├── README.md                    # This file - comprehensive documentation
├── .env                         # Environment variables (YOU CREATE THIS)
├── .gitignore                   # Git ignore file (recommended)
│
├── ticker_tracking.json         # Auto-generated tracking data (all 568+ stocks)
├── YahooNews.csv               # News data source (symbol, title, link, body, rssPublished)
├── finviz_data.csv             # Optional: Local Finviz data cache
│
├── fetch_finviz_data.sh        # Your existing data fetching script (reference only)
└── bot.log                     # Auto-generated log file (if logging enabled)
```

### File Descriptions

#### Core Files (Required)

**`percentage3cfo.py`** (559 lines)
- Main bot application with all logic
- Monitors ALL 568+ stocks for momentum gains
- Fetches live data from Finviz Elite API every 2 minutes
- Tracks all stocks persistently (silent tracking)
- Displays top 5 daily gainers with momentum highlights
- Manages Discord connection and commands
- Includes error handling and comprehensive logging

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
- News data source with columns: symbol, title, link, body, rssPublished
- Updated by your data pipeline
- Bot displays clickable news titles with publication dates
- Format: `symbol,"title","link","body","rssPublished"`

#### Auto-Generated Files

**`ticker_tracking.json`** (Persistent Tracking)
- Created on first run
- Stores last known change % for ALL stocks (568+ from Finviz screener)
- **Never removes tickers** - preserves historical data
- Updated every 2-minute check cycle (adds new + updates existing)
- Enables momentum detection by comparing current vs. previous values
- Format: `{"ACRS": 12.02, "AAOI": 8.35, "WHWK": 7.66, ...}`
- Can be deleted with `!reset` command to start fresh
- Typical size: 568+ tickers after first run, grows if screener expands

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

### Threshold Algorithm (Persistent Tracking)
```python
# Load existing tracking data (preserves history)
current_data = load_tracking_data()  # e.g., {IOBT: 19.63, WHWK: 7.66, ...}

For each ticker in top 5:
    current_change = ticker.change_from_open
    
    If ticker not in tracking:
        # Truly new - never seen before
        → Notify (NEW entry)
        current_data[ticker] = current_change
    Else:
        # Compare with historical value
        previous_change = tracking[ticker]
        delta = current_change - previous_change
        
        If delta >= CHANGE_THRESHOLD:
            → Notify (THRESHOLD met)
        Else:
            → Skip (below threshold)
            → Log: "TICKER: X.XX% → Y.YY% (ΔZ.ZZ%) - No alert"
        
        # Always update the tracked value
        current_data[ticker] = current_change

# Save ALL data (current top 5 + historical tickers)
# This preserves data for tickers that drop out
save_tracking_data(current_data)
```

**Key Difference from Traditional Approach:**
- `current_data` starts with existing historical data (`.copy()`)
- Only updates/adds values for current top 5
- Never removes tickers from tracking
- Result: Historical context preserved forever

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

**Version**: 2.0.0 (October 2025) - Full Spectrum Momentum Tracking  
**Python**: 3.7+  
**License**: Use as needed for personal trading  
**Disclaimer**: For educational and personal use. Not financial advice.

# stocks-co

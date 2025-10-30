import discord
from discord.ext import tasks
import pandas as pd
from datetime import datetime
import os
import json
import requests
from io import StringIO
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID4'))

# Finviz Elite Configuration
FINVIZ_AUTH_TOKEN = os.getenv('FINVIZ_AUTH_TOKEN', '512b187b-b9f5-4762-bed0-661ffd5a71c1')
FINVIZ_PORTFOLIO_PID = os.getenv('FINVIZ_PORTFOLIO_PID', '1000799188')

# News source (keeping YahooNews.csv for now, can switch to Finviz news)
NEWS_CSV = 'YahooNews.csv'

# Tracking file for change detection
TRACKING_FILE = 'ticker_tracking.json'

# Change threshold for notifications (in percentage points)
CHANGE_THRESHOLD = 3.0  # Alert threshold for increases

# Check interval
UPDATE_INTERVAL_MINUTES = 2  # Check every 2 minutes

# User-Agent for API requests
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# Initialize Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Task execution lock to prevent overlapping runs
task_lock = asyncio.Lock()


def parse_percentage(pct_str):
    """Convert percentage string like '1.77%' to float 1.77"""
    try:
        if pd.isna(pct_str) or pct_str == '-':
            return 0.0
        return float(str(pct_str).strip('%').replace(',', ''))
    except:
        return 0.0


def load_tracking_data():
    """Load previous tracking data from JSON file"""
    try:
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, 'r') as f:
                return json.load(f)
        return {}
    except:
        return {}


def save_tracking_data(data):
    """Save current tracking data to JSON file"""
    try:
        with open(TRACKING_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving tracking data: {e}")


def fetch_finviz_elite_data():
    """Fetch live data directly from Finviz Elite API"""
    try:
        print("📡 Fetching live data from Finviz Elite API...")
        
        # Construct the Finviz Elite screener URL (same as in your shell script)
        url = (
            "https://elite.finviz.com/export.ashx?v=152"
            "&f=cap_microover,geo_usa%7Ccanada%7Ceurope,"
            "ind_airlines%7Capparelmanufacturing%7Cautoparts%7Cbusinessequipmentsupplies%7C"
            "computerhardware%7Cconglomerates%7Cconsumerelectronics%7C"
            "drugmanufacturersspecialtygeneric%7Celectricalequipmentparts%7C"
            "engineeringconstruction%7Cfinancialdatastockexchanges%7Cfootwearaccessories%7C"
            "healthcareplans%7Cindustrialdistribution%7Caerospacedefense%7Cairportsairservices%7C"
            "apparelretail%7Cautomanufacturers%7Cautotruckdealerships%7Cbeveragesnonalcoholic%7C"
            "biotechnology%7Ccommunicationequipment%7Ccreditservices%7Cdrugmanufacturersgeneral%7C"
            "educationtrainingservices%7Celectroniccomponents%7Celectronicscomputerdistribution%7C"
            "financialconglomerates%7Cfurnishingsfixturesappliances%7Cgrocerystores%7C"
            "healthinformationservices%7Cinformationtechnologyservices%7Cinternetcontentinformation%7C"
            "leisure%7Cluxurygoods%7Cmedicalcarefacilities%7Cmedicaldistribution%7Cpackagedfoods%7C"
            "pollutiontreatmentcontrols%7Cscientifictechnicalinstruments%7C"
            "semiconductorequipmentmaterials%7Csoftwareinfrastructure%7Cspecialtybusinessservices%7C"
            "specialtyretail%7Ctelecomservices%7Cutilitiesdiversified%7Cutilitiesregulatedelectric%7C"
            "utilitiesregulatedwater%7Cwastemanagement%7Cutilitiesrenewable%7Cutilitiesregulatedgas%7C"
            "utilitiesindependentpowerproducers%7Ctextilemanufacturing%7Cspecialtyindustrialmachinery%7C"
            "solar%7Csoftwareapplication%7Csemiconductors%7Cpharmaceuticalretailers%7C"
            "packagingcontainers%7Cmedicalinstrumentssupplies%7Cmedicaldevices%7Cinternetretail%7C"
            "uranium%7Cintegratedfreightlogistics%7Cdiagnosticsresearch%7Cfooddistribution%7C"
            "householdpersonalproducts%7Crestaurants%7Crecreationalvehicles%7Cpersonalservices,"
            "sec_energy%7Chealthcare%7Ctechnology%7Cutilities%7Cindustrials%7Ccommunicationservices,"
            "sh_avgvol_o750,sh_instown_15to,sh_price_0.5to50,sh_short_to40,ta_volatility_x1.5to"
            "&ft=4&o=ticker&r=341"
            "&c=1,3,4,5,6,16,77,17,18,19,21,23,22,82,78,127,128,26,28,30,31,84,42,43,44,47,46,49,50,57,58,68,70,76,60,63,67,89,81,87,88,65,66,71,72"
            f"&auth={FINVIZ_AUTH_TOKEN}"
        )
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse CSV response
        df = pd.read_csv(StringIO(response.text))
        
        if df.empty:
            print("❌ No data returned from Finviz Elite API")
            return None
        
        print(f"✅ Fetched {len(df)} tickers from Finviz Elite")
        return df
        
    except Exception as e:
        print(f"Error fetching from Finviz Elite API: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_all_tickers():
    """Get all tickers from live Finviz Elite data"""
    try:
        df = fetch_finviz_elite_data()
        
        if df is None or df.empty:
            return None
        
        # Parse Change from Open percentage
        df['Change_Numeric'] = df['Change from Open'].apply(parse_percentage)
        
        # Select relevant columns and return ALL tickers
        return df[[
            'Ticker', 
            'Price',
            'Change from Open', 
            'Performance (Month)',
            'Performance (YTD)',
            'Earnings Date', 
            'Change_Numeric'
        ]]
    
    except Exception as e:
        print(f"Error getting tickers: {e}")
        return None


def check_threshold_change(all_tickers_df):
    """
    Check ALL tickers for momentum gains.
    Returns dict with tickers that gained +3% and their deltas.
    
    Uses persistent tracking - all tickers tracked for historical comparisons.
    """
    previous_data = load_tracking_data()
    
    print(f"\nTracking {len(all_tickers_df)} stocks for momentum changes...")
    
    # First run - track all tickers silently
    if not previous_data:
        current_data = {}
        for idx, row in all_tickers_df.iterrows():
            ticker = row['Ticker']
            current_data[ticker] = row['Change_Numeric']
        save_tracking_data(current_data)
        print("First run - tracking all tickers silently (no alerts)")
        return {}
    
    # Check for threshold changes in ALL tickers
    significant_tickers = {}
    
    # Start with existing tracking data (PRESERVE ALL HISTORICAL DATA)
    current_data = previous_data.copy()
    
    for idx, row in all_tickers_df.iterrows():
        ticker = row['Ticker']
        current_change = row['Change_Numeric']
        
        # If ticker wasn't tracked before
        if ticker not in previous_data:
            current_data[ticker] = current_change
            # Track silently
        else:
            # Calculate the change difference
            change_difference = current_change - previous_data[ticker]
            
            # Update the tracked value
            current_data[ticker] = current_change
            
            # Only alert on INCREASES ≥ threshold
            if change_difference >= CHANGE_THRESHOLD:
                significant_tickers[ticker] = {
                    'delta': change_difference,
                    'reason': 'THRESHOLD_UP',
                    'previous': previous_data[ticker],
                    'current': current_change,
                    'current_gain': current_change  # For sorting
                }
                print(f"✓ {ticker} increased by +{change_difference:.2f}% (threshold: {CHANGE_THRESHOLD}%)")
    
    # Save tracking data (includes ALL tickers)
    save_tracking_data(current_data)
    
    if significant_tickers:
        print(f"\nFound {len(significant_tickers)} stocks with +{CHANGE_THRESHOLD}% momentum gain")
    
    return significant_tickers


def get_ticker_news(ticker, count=3):
    """Get the latest N news items for a specific ticker"""
    try:
        # New CSV format: symbol,"title","link","body","rssPublished"
        df = pd.read_csv(NEWS_CSV)
        
        # Filter for the specific ticker
        ticker_news = df[df['symbol'] == ticker].copy()
        
        if ticker_news.empty:
            return []
        
        # Convert rssPublished column to datetime for sorting
        ticker_news.loc[:, 'rssPublished'] = pd.to_datetime(ticker_news['rssPublished'])
        
        # Get the most recent N news items
        latest_news = ticker_news.sort_values('rssPublished', ascending=False).head(count)
        
        news_list = []
        for idx, news in latest_news.iterrows():
            # Handle NaN or missing values
            title = news['title'] if pd.notna(news['title']) else "No title available"
            link = news['link'] if pd.notna(news['link']) else "#"
            date = news['rssPublished']
            
            news_list.append({
                'title': str(title),
                'link': str(link),
                'date': date.strftime('%Y-%m-%d %H:%M') if pd.notna(date) else "Unknown date"
            })
        
        return news_list
    
    except Exception as e:
        print(f"Error reading news for {ticker}: {e}")
        return []


def create_report_embed(top_5_df, significant_tickers, title="Top 5 Daily Gainers - Live Data"):
    """Create a rich Discord embed with the top 5 tickers info"""
    embed = discord.Embed(
        title=title,
        description=f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        color=discord.Color.gold() if significant_tickers else discord.Color.blue()
    )
    
    # Load tracking data to show deltas for non-alert tickers
    tracking_data = load_tracking_data()
    
    # Check if we have momentum_delta column (from momentum-based display)
    top_5_copy = top_5_df.copy()
    top_5_copy['is_alert'] = top_5_copy['Ticker'].isin(significant_tickers)
    
    if 'momentum_delta' in top_5_copy.columns:
        # Sort by momentum delta (biggest 2-min gains first)
        top_5_sorted = top_5_copy.sort_values(
            by='momentum_delta', 
            ascending=False
        )
    else:
        # Sort by: 1) Alert status (alerts first), 2) Change_Numeric (descending)
        top_5_sorted = top_5_copy.sort_values(
            by=['is_alert', 'Change_Numeric'], 
            ascending=[False, False]
        )
    
    display_rank = 1
    for idx, row in top_5_sorted.iterrows():
        ticker = row['Ticker']
        
        price = row['Price']
        change_from_open = row['Change from Open']
        monthly_perf = row['Performance (Month)']
        ytd_perf = row['Performance (YTD)']
        earnings_date = row['Earnings Date']
        
        # Header with rank and price
        rank = display_rank
        display_rank += 1
        
        # Check if this ticker met the threshold
        is_significant = ticker in significant_tickers
        ticker_info = significant_tickers.get(ticker, {})
        
        # Create Finviz Elite link for the ticker (chart view)
        finviz_url = f"https://elite.finviz.com/quote.ashx?t={ticker}&p=d"
        
        # Determine icon based on significance
        if is_significant:
            if ticker_info.get('reason') == 'THRESHOLD_UP':
                icon = "▲"
            elif ticker_info.get('reason') in ['MANUAL', 'FORCED']:
                icon = "•"
            else:
                icon = "•"
        else:
            icon = "•"
        
        # Consistent format: show current percentage for all tickers
        # For momentum alerts, also show the 2-min momentum gain in title
        if is_significant and ticker_info.get('reason') == 'THRESHOLD_UP':
            momentum_gain = ticker_info['delta']
            if row['Change_Numeric'] > 0:
                field_name = f"{icon} #{rank} - {ticker} - ${price} (+{change_from_open}) [+{momentum_gain:.2f}% momentum]"
            else:
                field_name = f"{icon} #{rank} - {ticker} - ${price} ({change_from_open}) [+{momentum_gain:.2f}% momentum]"
        else:
            # Non-momentum or manual triggers
            if row['Change_Numeric'] > 0:
                field_name = f"{icon} #{rank} - {ticker} - ${price} (+{change_from_open})"
            else:
                field_name = f"{icon} #{rank} - {ticker} - ${price} ({change_from_open})"
        
        # Context section - consistent for all tickers with color coding
        field_value = ""
        field_value += f"\n\n[View on Finviz]({finviz_url})\n"
        
        # Track previous value for Performance section
        previous_value = None
        
        if is_significant:
            if ticker_info.get('reason') == 'THRESHOLD_UP':
                field_value += f"\n**Context:**\n"
                delta = ticker_info['delta']
                # Green for increases
                field_value += f"```ansi\n\u001b[32mIncreased by +{delta:.2f}% from last check\u001b[0m\n```\n"
                previous_value = f"{ticker_info['previous']:.2f}%"
            elif ticker_info.get('reason') in ['MANUAL', 'FORCED']:
                field_value += f"\n**Context:**\n"
                field_value += f"Manual trigger (threshold bypassed)\n\n"
                if ticker in tracking_data:
                    previous_value = f"{tracking_data[ticker]:.2f}%"
        else:
            # Calculate and show delta for non-alert tickers
            if ticker in tracking_data:
                field_value += f"\n**Context:**\n"
                previous_change = tracking_data[ticker]
                current_change = row['Change_Numeric']
                delta = current_change - previous_change
                
                if delta > 0:
                    # Green for increases
                    field_value += f"```ansi\n\u001b[32mIncreased by +{delta:.2f}% from last check\u001b[0m\n```\n"
                elif delta < 0:
                    # Red for decreases
                    field_value += f"```ansi\n\u001b[31mDecreased by {delta:.2f}% from last check\u001b[0m\n```\n"
                else:
                    # No change
                    field_value += f"```ansi\n\u001b[33mNo change from last check (0.00%)\u001b[0m\n```\n"
                
                previous_value = f"{previous_change:.2f}%"
            else:
                field_value += f"\nFirst time tracked (no previous data)\n\n"
                previous_value = "Not tracked"
        
        field_value += f"\n**Performance:**\n"
        if previous_value:
            field_value += f"Previous: `{previous_value}`\n"
        field_value += f"YTD: `{ytd_perf}`\n"
        field_value += f"Earnings: {earnings_date}\n"
     
        # Get top 3 news for this ticker
        news_list = get_ticker_news(ticker, count=3)
        
        if news_list:
            field_value += f"\n**Latest News:**\n"
            news_added = 0
            for i, news in enumerate(news_list, 1):
                # Safely handle title truncation
                title = str(news['title'])
                if len(title) > 100:
                    title = title[:100] + "..."
                
                # Build news item - title as clickable link
                news_item = f"\n`{i}.` [{title}]({news['link']})\n"
                news_item += f"   Read More • {news['date']}\n"
                
                # Check if adding this news item would exceed Discord's limit
                if len(field_value) + len(news_item) > 1020:
                    # Add a note that there are more news items
                    if news_added == 0:
                        field_value += "\n_News content too long to display_\n"
                    break
                
                field_value += news_item
                news_added += 1
        else:
            field_value += "\n**Latest News:** No recent news available"
        
        # Add dash line separator for clear readability between tickers
        field_value += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        embed.add_field(
            name=field_name,
            value=field_value,
            inline=False
        )
    
    embed.set_footer(text=f"Finviz Elite | Alert Threshold: +{CHANGE_THRESHOLD}%")
    return embed


@tasks.loop(minutes=UPDATE_INTERVAL_MINUTES)
async def send_top_tickers():
    """Scheduled task to send top tickers report"""
    # Prevent overlapping executions
    if task_lock.locked():
        print(f"⚠️ [{datetime.now()}] Previous task still running, skipping this cycle")
        return
    
    async with task_lock:
        try:
            print(f"🔄 [{datetime.now()}] Starting scheduled check...")
            
            # Get the channel
            channel = client.get_channel(CHANNEL_ID)
            if not channel:
                print(f"Could not find channel with ID {CHANNEL_ID}")
                return
            
            # Get ALL tickers from live Finviz Elite API
            all_tickers = get_all_tickers()
            
            if all_tickers is None or all_tickers.empty:
                print("⚠️ Unable to fetch ticker data at this time.")
                return
            
            # Check ALL tickers for momentum gainers
            significant_tickers = check_threshold_change(all_tickers)
            
            # Only send notification if there are momentum gainers
            if not significant_tickers:
                print(f"[{datetime.now()}] No significant increases (threshold: +{CHANGE_THRESHOLD}%)")
                return
            
            # Get top momentum gainers (sorted by MOMENTUM DELTA - biggest 2-min gains first!)
            sorted_momentum = sorted(
                significant_tickers.items(),
                key=lambda x: x[1]['delta'],  # Sort by momentum gain, not daily performance
                reverse=True
            )
            
            # Show top 5 momentum gainers (or all if < 5)
            num_to_show = min(5, len(sorted_momentum))
            top_momentum_symbols = [ticker for ticker, _ in sorted_momentum[:num_to_show]]
            
            # Get DataFrame for momentum gainers
            display_df = all_tickers[all_tickers['Ticker'].isin(top_momentum_symbols)].copy()
            
            # Sort by momentum delta (highest momentum first)
            # Add delta for sorting
            display_df['momentum_delta'] = display_df['Ticker'].map(
                lambda t: significant_tickers[t]['delta'] if t in significant_tickers else 0
            )
            display_df = display_df.sort_values('momentum_delta', ascending=False)
            
            # Set title based on count
            if num_to_show >= 5:
                embed_title = "Top 5 Momentum Gainers (Last 2 Minutes)"
            else:
                embed_title = f"Top {num_to_show} Momentum Gainer(s) (Last 2 Minutes)"
            
            print(f"Showing top {num_to_show} momentum gainer(s) sorted by 2-min delta ({len(significant_tickers)} total met threshold)")
            
            # Mark which displayed tickers are momentum gainers (all of them in this case)
            display_significant = {k: v for k, v in significant_tickers.items() if k in top_momentum_symbols}
            
            # Create and send embed
            embed = create_report_embed(display_df, display_significant, title=embed_title)
            await channel.send(embed=embed)
            
            print(f"[{datetime.now()}] Report sent! {len(display_significant)} momentum alert(s) displayed ({len(significant_tickers)} total met threshold).")
        
        except Exception as e:
            print(f"Error in scheduled task: {e}")
            import traceback
            traceback.print_exc()


@client.event
async def on_ready():
    """Called when the bot is ready"""
    # on_ready can be called multiple times (reconnections, etc.)
    # Use a flag to ensure task only starts once
    if hasattr(client, '_ready_fired'):
        print(f'⚠️ on_ready called again (reconnection) - task already running')
        return
    
    client._ready_fired = True
    print(f'Bot logged in as {client.user}')
    print(f'Fetching live data every {UPDATE_INTERVAL_MINUTES} minute(s)')
    print(f'Alert threshold: +{CHANGE_THRESHOLD}%')
    print(f'NEW entries and decreases: Tracked silently (no alerts)')
    
    # Start the scheduled task (only once)
    if not send_top_tickers.is_running():
        send_top_tickers.start()
        print(f'Scheduled task started successfully')
    else:
        print(f'Task already running, skipping start')


# Optional: Manual command to trigger report immediately
@client.event
async def on_message(message):
    """Listen for commands"""
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Manual trigger command (ignores threshold)
    if message.content.lower() == '!top5':
        all_tickers = get_all_tickers()
        if all_tickers is not None and not all_tickers.empty:
            # Get top 5 by current gain
            top_5 = all_tickers.nlargest(5, 'Change_Numeric')
            # Show all top 5 for manual trigger - create dict format
            manual_tickers = {ticker: {'delta': None, 'reason': 'MANUAL', 'previous': None, 'current': None, 'current_gain': 0} 
                          for ticker in top_5['Ticker'].tolist()}
            embed = create_report_embed(top_5, manual_tickers)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("⚠️ Unable to fetch ticker data.")
    
    # Force notification (bypasses threshold)
    elif message.content.lower() == '!force':
        all_tickers = get_all_tickers()
        if all_tickers is not None and not all_tickers.empty:
            # Get top 5 by current gain
            top_5 = all_tickers.nlargest(5, 'Change_Numeric')
            forced_tickers = {ticker: {'delta': None, 'reason': 'FORCED', 'previous': None, 'current': None, 'current_gain': 0} 
                          for ticker in top_5['Ticker'].tolist()}
            embed = create_report_embed(top_5, forced_tickers)
            await message.channel.send("🔧 **Forced Update** (threshold bypassed)")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("⚠️ Unable to fetch ticker data.")
    
    # Reset tracking (start fresh)
    elif message.content.lower() == '!reset':
        if os.path.exists(TRACKING_FILE):
            os.remove(TRACKING_FILE)
            await message.channel.send("🔄 Tracking data reset. Next check will notify all tickers.")
        else:
            await message.channel.send("ℹ️ No tracking data to reset.")
    
    # Show help
    elif message.content.lower() == '!help':
        help_text = """
**Trading Bot Commands:**

`!top5` - Show current top 5 performers (bypasses threshold)
`!force` - Force send notification (bypasses threshold)
`!reset` - Reset change tracking
`!help` - Show this help message

**Auto-notifications:** 
Bot checks every {interval} minute(s) and alerts when a ticker increases by +{threshold}% or more.

NEW entries and decreases are tracked silently (no notifications).
        """.format(interval=UPDATE_INTERVAL_MINUTES, threshold=CHANGE_THRESHOLD)
        await message.channel.send(help_text)


# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file")
    else:
        client.run(DISCORD_TOKEN)
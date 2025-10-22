import discord
from discord.ext import tasks
import pandas as pd
from datetime import datetime
import os
import json
import requests
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Finviz Elite Configuration
FINVIZ_AUTH_TOKEN = os.getenv('FINVIZ_AUTH_TOKEN', '512b187b-b9f5-4762-bed0-661ffd5a71c1')
FINVIZ_PORTFOLIO_PID = os.getenv('FINVIZ_PORTFOLIO_PID', '1000799188')

# News source (keeping YahooNews.csv for now, can switch to Finviz news)
NEWS_CSV = 'YahooNews.csv'

# Tracking file for change detection
TRACKING_FILE = 'ticker_tracking.json'

# Change threshold for notifications (in percentage points)
CHANGE_THRESHOLD = 3.0  # Notify only if change increased by 3% or more

# For testing: 1 minute, Production: 2 minutes for real-time
UPDATE_INTERVAL_MINUTES = 1  # Change to 2 for production

# User-Agent for API requests
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# Initialize Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


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


def get_top_5_tickers():
    """Get top 5 tickers by Change from Open from live Finviz Elite data"""
    try:
        df = fetch_finviz_elite_data()
        
        if df is None or df.empty:
            return None
        
        # Parse Change from Open percentage
        df['Change_Numeric'] = df['Change from Open'].apply(parse_percentage)
        
        # Sort by Change_Numeric descending and get top 5
        top_5 = df.nlargest(5, 'Change_Numeric')
        
        # Select relevant columns
        return top_5[[
            'Ticker', 
            'Price',
            'Change from Open', 
            'Performance (Month)',
            'Performance (YTD)',
            'Earnings Date', 
            'Change_Numeric'
        ]]
    
    except Exception as e:
        print(f"Error getting top 5 tickers: {e}")
        return None


def check_threshold_change(top_5_df):
    """
    Check if any ticker has increased by threshold amount since last check.
    Returns dict with tickers and their change deltas.
    """
    previous_data = load_tracking_data()
    
    # First run - track all tickers
    if not previous_data:
        current_data = {}
        result = {}
        for idx, row in top_5_df.iterrows():
            ticker = row['Ticker']
            current_data[ticker] = row['Change_Numeric']
            result[ticker] = {
                'delta': None,
                'reason': 'NEW',
                'previous': None,
                'current': row['Change_Numeric']
            }
        save_tracking_data(current_data)
        print("📝 First run - tracking all tickers")
        return result
    
    # Check for threshold changes
    significant_tickers = {}
    current_data = {}
    
    for idx, row in top_5_df.iterrows():
        ticker = row['Ticker']
        current_change = row['Change_Numeric']
        current_data[ticker] = current_change
        
        # If ticker wasn't tracked before
        if ticker not in previous_data:
            significant_tickers[ticker] = {
                'delta': None,
                'reason': 'NEW',
                'previous': None,
                'current': current_change
            }
            print(f"🆕 {ticker} is new to top 5: {current_change:.2f}%")
        else:
            # Calculate the change difference
            change_difference = current_change - previous_data[ticker]
            if change_difference >= CHANGE_THRESHOLD:
                significant_tickers[ticker] = {
                    'delta': change_difference,
                    'reason': 'THRESHOLD',
                    'previous': previous_data[ticker],
                    'current': current_change
                }
                print(f"🔔 {ticker} change increased by {change_difference:.2f}% (threshold: {CHANGE_THRESHOLD}%)")
    
    # Update tracking data
    save_tracking_data(current_data)
    
    return significant_tickers


def get_ticker_news(ticker, count=3):
    """Get the latest N news items for a specific ticker"""
    try:
        df = pd.read_csv(NEWS_CSV)
        
        # Filter for the specific ticker
        ticker_news = df[df['symbol'] == ticker].copy()
        
        if ticker_news.empty:
            return []
        
        # Convert date column to datetime for sorting
        ticker_news.loc[:, 'date'] = pd.to_datetime(ticker_news['date'])
        
        # Get the most recent N news items
        latest_news = ticker_news.sort_values('date', ascending=False).head(count)
        
        news_list = []
        for idx, news in latest_news.iterrows():
            # Handle NaN or missing values
            title = news['title'] if pd.notna(news['title']) else "No title available"
            summary = news['summary'] if pd.notna(news['summary']) else "No summary available"
            source = news['source'] if pd.notna(news['source']) else "Unknown"
            link = news['link'] if pd.notna(news['link']) else "#"
            
            news_list.append({
                'title': str(title),
                'summary': str(summary),
                'source': str(source),
                'link': str(link),
                'date': news['date'].strftime('%Y-%m-%d %H:%M UTC')
            })
        
        return news_list
    
    except Exception as e:
        print(f"Error reading news for {ticker}: {e}")
        return []


def create_report_embed(top_5_df, significant_tickers):
    """Create a rich Discord embed with the top 5 tickers info"""
    embed = discord.Embed(
        title="📈 Top Performers - Live from Finviz Elite",
        description=f"🔔 **{len(significant_tickers)} ticker(s)** met the +{CHANGE_THRESHOLD}% threshold\n"
                    f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        color=discord.Color.gold() if significant_tickers else discord.Color.blue()
    )
    
    for idx, row in top_5_df.iterrows():
        ticker = row['Ticker']
        
        # Only include tickers that meet the threshold
        if ticker not in significant_tickers:
            continue
        
        price = row['Price']
        change_from_open = row['Change from Open']
        monthly_perf = row['Performance (Month)']
        ytd_perf = row['Performance (YTD)']
        earnings_date = row['Earnings Date']
        
        # Get threshold delta information
        ticker_info = significant_tickers[ticker]
        
        # Header with rank and price
        rank = list(top_5_df['Ticker']).index(ticker) + 1
        
        # Add threshold indicator to header
        if ticker_info['reason'] == 'NEW':
            field_name = f"🆕 #{rank} - {ticker} - ${price} (New to Top 5)"
        elif ticker_info['reason'] in ['MANUAL', 'FORCED']:
            field_name = f"📊 #{rank} - {ticker} - ${price}"
        else:
            delta = ticker_info['delta']
            field_name = f"🚀 #{rank} - {ticker} - ${price} (+{delta:.2f}% increase)"
        
        # Performance metrics with threshold alert
        field_value = ""
        if ticker_info['reason'] == 'NEW':
            field_value += f"**🔔 Threshold Alert:**\n"
            field_value += f"• **NEW** entry to top 5\n"
            field_value += f"• Previous: `Not tracked` → Current: `{change_from_open}`\n\n"
        elif ticker_info['reason'] == 'THRESHOLD':
            field_value += f"**🔔 Threshold Alert:**\n"
            field_value += f"• Increased by **+{ticker_info['delta']:.2f}%** from last check\n"
            field_value += f"• Previous: `{ticker_info['previous']:.2f}%` → Current: `{change_from_open}`\n\n"
        
        field_value += f"**📊 Performance:**\n"
        field_value += f"• Change from Open: `{change_from_open}`\n"
        field_value += f"• Monthly: `{monthly_perf}`\n"
        field_value += f"• YTD: `{ytd_perf}`\n"
        field_value += f"• Earnings: {earnings_date}\n\n"
        
        # Get top 3 news for this ticker
        news_list = get_ticker_news(ticker, count=3)
        
        if news_list:
            field_value += f"**📰 Latest News:**\n"
            for i, news in enumerate(news_list, 1):
                # Safely handle summary truncation
                summary = str(news['summary'])
                if len(summary) > 250:
                    summary = summary[:250] + "..."
                
                # Safely handle title truncation
                title = str(news['title'])
                if len(title) > 100:
                    title = title[:100]
                
                field_value += f"\n`{i}.` **{title}**\n"
                field_value += f"_{summary}_\n"
                field_value += f"[Read More]({news['link']}) • {news['date']}\n"
        else:
            field_value += "**📰 Latest News:** No recent news available"
        
        # Discord has 1024 character limit per field
        if len(field_value) > 1024:
            field_value = field_value[:1020] + "..."
        
        embed.add_field(
            name=field_name,
            value=field_value,
            inline=False
        )
    
    embed.set_footer(text=f"Live Finviz Elite Data | Threshold: +{CHANGE_THRESHOLD}%")
    return embed


@tasks.loop(minutes=UPDATE_INTERVAL_MINUTES)
async def send_top_tickers():
    """Scheduled task to send top tickers report"""
    try:
        # Get the channel
        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Could not find channel with ID {CHANNEL_ID}")
            return
        
        # Get top 5 tickers from live Finviz Elite API
        top_5 = get_top_5_tickers()
        
        if top_5 is None or top_5.empty:
            print("⚠️ Unable to fetch ticker data at this time.")
            return
        
        # Check which tickers meet the threshold
        significant_tickers = check_threshold_change(top_5)
        
        # Only send notification if there are significant changes
        if not significant_tickers:
            print(f"[{datetime.now()}] No significant changes (threshold: +{CHANGE_THRESHOLD}%)")
            return
        
        # Filter top_5 to only include significant tickers
        filtered_top_5 = top_5[top_5['Ticker'].isin(significant_tickers)]
        
        # Create and send embed
        embed = create_report_embed(filtered_top_5, significant_tickers)
        await channel.send(embed=embed)
        
        print(f"[{datetime.now()}] Report sent! {len(significant_tickers)} ticker(s) met threshold.")
    
    except Exception as e:
        print(f"Error in scheduled task: {e}")
        import traceback
        traceback.print_exc()


@client.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'✅ Bot logged in as {client.user}')
    print(f'📡 Fetching live data from Finviz Elite API every {UPDATE_INTERVAL_MINUTES} minute(s)')
    print(f'🔔 Notification threshold: +{CHANGE_THRESHOLD}% change')
    
    # Start the scheduled task
    if not send_top_tickers.is_running():
        send_top_tickers.start()


# Optional: Manual command to trigger report immediately
@client.event
async def on_message(message):
    """Listen for commands"""
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Manual trigger command (ignores threshold)
    if message.content.lower() == '!top5':
        top_5 = get_top_5_tickers()
        if top_5 is not None and not top_5.empty:
            # Show all top 5 for manual trigger - create dict format
            all_tickers = {ticker: {'delta': None, 'reason': 'MANUAL', 'previous': None, 'current': None} 
                          for ticker in top_5['Ticker'].tolist()}
            embed = create_report_embed(top_5, all_tickers)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("⚠️ Unable to fetch ticker data.")
    
    # Force notification (bypasses threshold)
    elif message.content.lower() == '!force':
        top_5 = get_top_5_tickers()
        if top_5 is not None and not top_5.empty:
            all_tickers = {ticker: {'delta': None, 'reason': 'FORCED', 'previous': None, 'current': None} 
                          for ticker in top_5['Ticker'].tolist()}
            embed = create_report_embed(top_5, all_tickers)
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
**🤖 Discord Trading Bot Commands:**

`!top5` - Show current top 5 performers (bypasses threshold)
`!force` - Force send notification (bypasses threshold)
`!reset` - Reset change tracking (next update will notify all)
`!help` - Show this help message

**Auto-notifications:** Bot checks every {interval} minute(s) and only sends alerts when a ticker's change increases by +{threshold}% or more.
        """.format(interval=UPDATE_INTERVAL_MINUTES, threshold=CHANGE_THRESHOLD)
        await message.channel.send(help_text)


# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file")
    else:
        client.run(DISCORD_TOKEN)
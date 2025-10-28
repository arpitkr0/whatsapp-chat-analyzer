import re
import pandas as pd

def preprocess(data):
    # ✅ Regex pattern for 12-hour format with AM/PM (handles normal or narrow spaces)
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?[APap][Mm]\s-\s'

    # Split messages and dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # ✅ Normalize special spaces like narrow non-breaking space (U+202F)
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ', regex=True)

    # ✅ Adjusted format to match month/day/year with AM/PM
    # WhatsApp on many devices now uses M/D/YY or M/D/YYYY
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ')
    except ValueError:
        # fallback for full 4-digit year
        df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%Y, %I:%M %p - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract user and message
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract date/time components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create hourly periods (e.g., 10-11)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour + 1}")
        else:
            period.append(f"{hour}-{hour + 1}")
    df['period'] = period

    return df

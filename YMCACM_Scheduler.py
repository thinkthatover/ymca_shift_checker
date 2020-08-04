
if __name__ == "__main__":

    import requests
    import datetime as dt
    import time
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    def update_managers(y_schedule):
        #get current time, set API call vars
        now=dt.datetime.today()
        start=now.timestamp()
        end=start+48*3600

        #remove previous days changes from y_schedule (for the following week)
        y_schedule = clean_previous_day(now, y_schedule)

        #Make API call and get shifts that have extra peopole
        result = event_caller(start,end)
        full_shifts = check_upcoming_blocks(result)
        
        for day in full_shifts:
            for shift in full_shifts[day]:
                heavy_blocks = full_shifts[day][shift]
                if len(heavy_blocks) > y_schedule[day][shift]:
                    send_email(day,shift,heavy_blocks)
                    print('email sent for {} {}, heavy_blocks = {}'.format(day,shift,heavy_blocks))
                    y_schedule[day][shift] = len(heavy_blocks)
        return y_schedule

    def clean_previous_day(today, y_schedule):
        """Sets the previous day back to the defaulty_schedule
        This function shares a lot of the default schedule code but I'm not sure how to 
        combine them effectively"""
        
        wk = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        wk_shifts =['shift0','shift1','shift2']
        wke_shifts = ['shift0']
        
        yesterday = wk[today.weekday() - 1]
        
        if yesterday not in wk[5:]:
            y_schedule[yesterday] = {shift:0 for shift in wk_shifts}
            y_schedule[yesterday]['shift1'] = 3
        else:
            y_schedule[yesterday] = {shift:0 for shift in wke_shifts}
        
        return y_schedule

    def check_upcoming_blocks(results):
        """check if upcoming blocks have >7 people, returns those that do
        as a hash table w/ structure: upcoming['day']['shift'] = [[block, attendees]]"""
        upcoming = {}
        
        return_list = []
        for row in results:
            attendees= row['attendees']
            cap = row['max_places']*.7 
                                    
            if attendees > cap and row['activity_id'] == 36: #activity id for gym floor
                time = dt.datetime.strptime(row['start'],'%Y-%m-%d %H:%M:%S')
                day = time.strftime('%A')
                block = time.strftime('%I%p').lstrip('0')
                shift = return_shift(time, day)
                
                #get shifts for populating hash table keys
                if day not in ["Saturday", "Sunday"]:
                    shifts = ['shift0', 'shift1', 'shift2'] 
                else:
                    shifts = ['shift0'] 
            
                if day not in upcoming:
                    #create empty hash w/ all shifts for that day
                    upcoming[day] = {shift:[] for shift in shifts}
                    
                    upcoming[day][shift].append([block, attendees])
                    
                else:
                    upcoming[day][shift].append([block, attendees])
                
                return_list.append([day, shift, block, row['attendees']])
        return upcoming

    def return_shift(time, day):
        """returns the shift each time block falls into"""
        
        #account for different weekend schedule 
        if day not in ["Saturday", "Sunday"]:
            shift_ends_at = [9,13,20] #24-hour end of shift times for picking which shift 
        else:
            shift_ends_at = [13] 
            
        #compare block hour to shift end hour, return
        for index,shift in enumerate(shift_ends_at):
            if time.hour < shift:
                return 'shift{}'.format(index)

    def event_caller(start_time, end_time):
        
        #calls virtuagym API and returns JSON result
        api_key = ##################
        club_key = #################
        club_id= #########
        api_call = 'https://api.virtuagym.com/api/v1/club/{}/events?api_key={}&club_secret={}&timestamp_start={}&timestamp_end={}'.format(
            club_id,api_key,club_key,start_time,end_time)
        response = requests.get(api_call)
        return response.json()['result']

    def send_email(day, shift, blocks):
        """Sends an email to angaw to update on shifts that are full
        """

        #email vars
        port = 465
        password = ##################
        sender_email = ################
        receiver_email = ###################
        context = ssl.create_default_context()
        
        #message info
        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = receiver_email

        #message variables
        sh_dct = {'shift0': 'First Shift',
                    'shift1':'Second Shift',
                    'shift2':'Third Shift'}
        cap = 7

        #Message Logic    
        message["Subject"] = "Attendance Update for {} {}".format(day, sh_dct[shift])
        
        if len(blocks) == 1:
            text = """\
            There's one block for the {} that has more than {} attendees.
            {} block now has {} participants.
            """.format(sh_dct[shift], cap, 
                    blocks[0][0], blocks[0][1])

        elif len(blocks) == 2:
        
            text ="""\
            Two blocks for the {} has more than {} attendees.
            {} block now has {} participants.
            {} block now has {} participants.
            
            Maybe add another employee to this shift?
            """.format(sh_dct[shift], cap, 
                    blocks[0][0], blocks[0][1], 
                    blocks[1][0], blocks[1][1])

        elif len(blocks) == 3:
        
            text ="""\
            Three blocks for the {} has more than {} attendees.
            {} block now has {} participants.
            {} block now has {} participants.
            {} block now has {} participants.
            
            Maybe add another employee to this shift?
            """.format(sh_dct[shift], cap, 
                    blocks[0][0], blocks[0][1], 
                    blocks[1][0], blocks[1][1],
                    blocks[2][0], blocks[2][1]
                    )

            
        #finish formatting the message
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        
        ##send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email,receiver_email, message.as_string())

    def default_schedule():
        """
        This creates our initial schedule that will be updating when we run our function
        Each schedule can :
        0: no email sent
        1: email sent for 1 full block
        2: email sent for 2 full blocks
        3: shift already has two people scheduled
           """
        
        #create weekday shifts
        wkdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        shifts =['shift0','shift1','shift2']
        y_schedule = {day : {shift : 0 for shift in shifts} for day in wkdays}

        #add weekend shifts
        wke_days = ['Saturday', 'Sunday']
        wke_shifts = ['shift0']
        for day in wke_days:
            y_schedule[day] = {shift:0 for shift in wke_shifts}

        #add shifts that have two employees already scheduled
        for day in y_schedule:
            if day in wkdays:
                y_schedule[day]['shift1'] = 3
        return y_schedule

    #instantiate original schedule
    y_schedule = default_schedule()

    interval_min = 15
    interval_sec = interval_min*60

    while True:
        y_schedule = update_managers(y_schedule)
        time.sleep(interval_sec)

import tweepy
import csv
import pandas as pd
import time
import sys

# My Twitter API Authentication Variables
consumer_key = 'kyKR4LNnQmbpjS3YlCJ9rshUh'
consumer_secret = 'UVZDaVnXPRZItfsVKsEQ3twTgUyNRps83OCk1FkBvCu3ttnVia'
access_token = '830477548668715008-B7C8lb0P5AK1EdjOec7q9J7UQkfr60j'
access_token_secret = '65C4wY7FJMwxUzh5dx1rK9XbwCp7dYN9HDsQ1kJr2PiKo'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

sn = []
text = []
timestamp = []
retweet_count = []

for tweet in tweepy.Cursor(api.search, q="#netflix", count=100,
                           lang="en",
                           since="2019-10-30").items():
    if float(tweet.retweet_count) >0:
        # print(tweet.user.screen_name)
        # if ('RT @' not in tweet.text):
        retweet_count.append(tweet.retweet_count)
        sn.append(tweet.user.screen_name)
        # text.append(tweet.text)

# Convert lists to dataframe
df = pd.DataFrame()
df['sn'] = sn
#df['text'] = text
df['retweet_count'] = retweet_count

df.to_csv('netflix.csv', index=False, encoding='utf-8')
df.sort_values(by='retweet_count', ascending=False, inplace=True)

df = pd.read_csv('netflix.csv')

# Create a list of the unique usernames in order to see which users we need to retrieve friends for.
allNames = list(df['sn'].unique())

# Initialize dataframe of users that will hold the edge relationships
dfUsers = pd.DataFrame()
dfUsers['userFromName'] = []
dfUsers['userFromId'] = []
dfUsers['userToId'] = []
count = 0

nameCount = len(allNames)
for name in allNames:
    # Build list of friends
    try:
        currentFriends = []
        for page in tweepy.Cursor(api.friends_ids, screen_name=name).pages():
            currentFriends.extend(page)
        currentId = api.get_user(screen_name=name).id
        currentId = [currentId] * len(currentFriends)
        currentName = [name] * len(currentFriends)
        dfTemp = pd.DataFrame()
        dfTemp['userFromName'] = currentName
        dfTemp['userFromId'] = currentId
        dfTemp['userToId'] = currentFriends
        dfUsers = pd.concat([dfUsers, dfTemp])
        dfUsers.to_csv('netflix_users.csv', index=False, encoding='utf-8')
        # time.sleep(70) # avoids hitting Twitter rate limit
        #print("Sleeping for 70 seconds")
        # Progress bar to track approximate progress
        count += 1
        per = round(count*100.0/nameCount, 1)
        sys.stdout.write("\rTwitter call %s%% complete." % per)
        sys.stdout.flush()
    except:
        pass


# We are not interested in "friends" that are not part of this community.
fromId = dfUsers['userFromId'].unique()
dfChat = dfUsers[dfUsers['userToId'].apply(lambda x: x in fromId)]

# No more Twitter API lookups are necessary. Create a lookup table that we will use to get the verify the userToName
dfLookup = dfChat[['userFromName', 'userFromId']]
dfLookup = dfLookup.drop_duplicates()
dfLookup.columns = ['userToName', 'userToId']
dfCommunity = dfUsers.merge(dfLookup, on='userToId')

dfCommunity.to_csv('dfCommunity.csv', index=False, encoding='utf-8')

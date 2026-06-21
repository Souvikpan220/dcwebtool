import os
import time , requests
from urllib import parse

from Source.Headers import Headers

class AuthUtils:
    def __init__(self , Config: dict , RequestClient: requests.Session) -> None:
        self.RequestClient = RequestClient
        self.ClientToken = Config['BotConfig'].get('BotToken')
        self.ClientId = Config['BotConfig'].get("ClientId")
        self.ClientSecret = Config['BotConfig'].get("ClientSecret")
        self.ClientRedirectUri = Config['BotConfig'].get("RedirectUri")

        #Apis To Perform Operation
        ApiEnd = "https://discord.com/api/v9/"
        EnocodedRedirect = parse.quote_plus(self.ClientRedirectUri)
        EncodedPerms = "%20".join(Config['BotConfig']['Perms'])
        self.FetchLocUri = ApiEnd + 'oauth2/authorize?client_id={}&response_type=code&redirect_uri='.format(self.ClientId) + EnocodedRedirect + '&scope=' + EncodedPerms
        self.FetchAuthUri = ApiEnd + 'oauth2/token'
        self.JoinUri = ApiEnd.split('/v')[0] + '/guilds/{}/members/{}'

        del EncodedPerms , EnocodedRedirect , ApiEnd

    def FetchLocation(self , Token: str):
        Req = self.RequestClient.post(
            url = self.FetchLocUri ,
            headers = Headers.get_headers(self.RequestClient , Token) ,
            json = {
                "permissions": 0 ,
                "authorize": True
            }
        )
        ReqJson = Req.json()
        if Req.status_code == 200 and 'location' in ReqJson:
            return {
                'success' : True ,
                'code' : ReqJson['location'].split("=")[1]
            }
        
        if Req.status_code == 429 and 'retry_after' in ReqJson:
            time.sleep(int(ReqJson['retry_after']))
            return self.FetchLocation(Token = Token)
        
        return {
            'success' : False ,
            'message' : ReqJson.get("message")
        }

    def FetchAuth(self , code: str):
        Rex = self.RequestClient.post(
            url = self.FetchAuthUri , 
            data = {
                'client_id': self.ClientId ,
                'client_secret': self.ClientSecret,
                'grant_type': 'authorization_code',
                'code': code ,
                'redirect_uri': self.ClientRedirectUri
            }, 
            headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        )
        RexJson = Rex.json()
        if Rex.status_code == 200 and 'access_token' in RexJson:
            return {
                'success' : True ,
                'Auth' : {
                    'AccessToken' : RexJson['access_token'] ,
                    'RefreshToken' : RexJson['refresh_token']
                }
            }
        
        if Rex.status_code == 429 and 'retry_after' in RexJson:
            time.sleep(int(RexJson['retry_after']))
            return self.FetchAuth(code = code)
        
        return {
            'success' : False ,
            'message' : RexJson.get("message")
        }
    
    def AuthJoin(self , AccessToken : str , UserId : int , GuildId : int):
        Req = self.RequestClient.put(
            url = self.JoinUri.format( GuildId , UserId ),
            headers = {
                "Authorization": f"Bot {self.ClientToken}",
                "Content-Type": "application/json"
            },
            json = { "access_token": AccessToken }
        )
        if Req.text:
            ReqJson = Req.json()

        if Req.status_code in [204 , 201]:
            return {
                'success' : True ,
                'message' : 'Already Joined' if Req.status_code == 204 else 'Joined'
            }

        if Req.status_code == 429 and 'retry_after' in ReqJson:
            time.sleep(int(Req.json()['retry_after']/1000))
            return self.AuthJoin(AccessToken , UserId , GuildId)

        return {
            'success' : False ,
            'message' : ReqJson.get("message")
        }
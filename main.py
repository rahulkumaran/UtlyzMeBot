from telegram.ext import CommandHandler, Updater
from telegram import *
import requests
import telepot
import re
import wikipedia
from bs4 import BeautifulSoup
import os





################################################################	FEW NECESSARY FUNCTIONS FOR THE BOT HERE	########################################################################


def get_url(args):
        '''
        This function is used to get the required url for the song
        '''
	url='https://search.azlyrics.com/search.php?q='
	for arg in args:			#will extract name from the argument list
		url += arg + "+"		#adding a space between the words
	r=requests.get(url)
	soup=BeautifulSoup(r.content,'html.parser')
	temp=soup.findAll(class_='text-left visitedlyr')     #For the link to the song lyrics
	for i in temp:				#gives the entire url to search
	    i=str(i)
	    i=i.split('href="')[1]
	    i=i.split('"')[0]
	    if '/lyrics/' in i:
	        url=i
	        break
     #Modifications done to get it compatible with requests module
	return url
	

################################################################	CODE FOR BOT FUNCTIONALITIES STARTS HERE	########################################################################


def start(bot,update):
	bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
	#time.sleep(0.2)
	#print update.message.chat_id
	bot.sendMessage(chat_id = update.message.chat_id, text = '''
		Hey %s %s! Welcome to UtlyzMeBot! Type /help for more information regarding the functionalities of this particular bot. In short, this bot will help you search wiki, google, get news bulletins and what not from this particular chat window itself :D 
	''' %(update.message.from_user.first_name,update.message.from_user.last_name))

def news(bot, update):
	bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
	url='https://in.reuters.com/news/top-news'
	bulletins = ""
        r=requests.get(url) # The very old get function
        soup=BeautifulSoup(r.content,'html.parser') #Getting content
        links=soup.find_all(href=re.compile('/article/')) #getting every link which has the word article
        for i in links:
		if(i.text != 'Continue Reading'):
			if(i.text != "" ):
                		bulletins +="->" + i.text + '\n' #printing out text of the blockquote
	bot.sendMessage(chat_id = update.message.chat_id, parse_mode=ParseMode.HTML, text = bulletins)


def lyrics(bot,update,args):
	try:
		s=requests.Session() 			#It is having so many redirects so use of session is helpful or we get an error
		s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36' #Headers
		r=s.get(get_url(args)) 			#Session get similarl to requests.get()
		soup=BeautifulSoup(r.content,'html.parser')
		temp=str(soup.findAll(class_='row'))
		temp=temp.replace('\\n','')
		temp=temp.split('<br/>') 		#Modifications of source code to get our required outcome
		lyrics = temp[2].split('\\r')[-1]
		for i in temp:				#Loop is for modifying each string so that no junk appears except \n
			if '<' in i:
		    		pass
			else:
		    		lyrics+=i + '\n'	#adding a new line character for easy reading purposes

		bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
		bot.sendMessage(chat_id = update.message.chat_id, parse_mode=ParseMode.HTML, text = lyrics)

	except IndexError:
		error = "Can't find the song you asked for, please try another song"
		bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
		bot.sendMessage(chat_id = update.message.chat_id, parse_mode=ParseMode.HTML, text = error)
	except UnboundLocalError:
		error = "Can't find the song you asked for, please try another song"
		bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
		bot.sendMessage(chat_id = update.message.chat_id, parse_mode=ParseMode.HTML, text = error)
	


def football(bot,update):
		r = requests.get('http://www.goal.com/en-in/live-scores')	#Gets HTML of entire page
		soup = BeautifulSoup(r.content,'html.parser')
		score_box = soup.find_all('div',attrs={'class':'match-main-data'})	#Navigating to where the score is available in the page
		scores = "\nThe scores of all matches played recently is displayed below:\n"
		scores+="--------------------------------------------------------------------\n"
		for i in score_box:		#To get the score of all live matches and recently done matches
			if(i.text[3] != 'F'):
				continue
			else:
				scores += i.text + "\n"
				scores+="--------------------------------------------------------------------\n"
		scores+= "\n\nNOTE: ALL THE MATCH TIMINGS ARE IN GMT\n\n"

		bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
		bot.sendMessage(chat_id = update.message.chat_id, text = scores)


def transfers(bot, update):
	r = requests.get('http://www.goal.com/en-us/transfer-rumours/1')
	soup = BeautifulSoup(r.content, 'html.parser')	#Gets HTML of entire page
	rumours = soup.select(".transfer-card__desc p")
	transfer = "\nThe latest Transfer news & rumours are displayed below:\n"
	transfer +="--------------------------------------------------------------------\n"
	for i in rumours:
		transfer += "->"+i.text
		transfer += "\n--------------------------------------------------------------------\n"

	bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
	bot.sendMessage(chat_id = update.message.chat_id, text = transfer)



def help(bot, update):
	bot.sendChatAction(chat_id = update.message.chat_id, action = ChatAction.TYPING)
	bot.sendMessage(chat_id = update.message.chat_id, text = '''
		The following are the avaiable commands with me!\n
		/news				To get news bulletins
		/lyrics <name_of_song>		To get lyrics of songs
		/football			To get latest football scores
		/transfer			To get football transfer updates
	''')




if __name__=='__main__':

	TOKEN = "482353144:AAHEfKVF_ibk2gAMI3T7sSk37u2ZU8P3PKQ"		#Token generated by BotFather

	NAME = 'utlyzmebot'

	ON_HEROKU = os.environ.get('ON_HEROKU')

	if ON_HEROKU:
    		PORT = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995
	else:
    		PORT = 3000

	#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

	#logger = logging.getLogger(__name__)

	updater = Updater(token=TOKEN)
	
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('start',start))

	dispatcher.add_handler(CommandHandler('help',help))

	dispatcher.add_handler(CommandHandler('news',news))

	dispatcher.add_handler(CommandHandler('lyrics',lyrics,pass_args = True))

	dispatcher.add_handler(CommandHandler('football',football))

	dispatcher.add_handler(CommandHandler('transfers',transfers))
	
	updater.start_webhook(listen="0.0.0.0",port=PORT,url_path=TOKEN)

	updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))

	updater.idle()


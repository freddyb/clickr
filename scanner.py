# for email parsing / extracting url
import re
from email import message_from_string
from email.iterators import typed_subpart_iterator
# for redirects:
from twisted.internet import reactor
from twisted.web.client import Agent, RedirectAgent
from twisted.web.http_headers import Headers


http_regex = re.compile("(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&;:/~\+#]*[\w\-\@?^=%&/~\+#])?", 2) # 2 = case-insensitive
id_regex = re.compile("'/.*[a-z0-9]{3,}'", 2) # 2 = //i
verify_regex = re.compile('(confirm|verify)', 2)


def scanMail(bodytext):
    for match in http_regex.finditer(bodytext):
	completeURL =  match.group(0)
	# all kind of URLs
	# now find those with nice token in the or "confirm" / "verify"	    
	if verify_regex.search(completeURL) != None or \
	    id_regex.search(completeURL) != None:
		yield completeURL
	#else: print 'LAME:', completeURL


	
def decodeMail(mailtext):
    ''' expects raw mailtext, returns decoded body '''
    mesg =  message_from_string(mailtext)
    # note: if we give no params, it defaults to text. but we only
    # want text/html and text/plain, maybe ONLY plain
    # but there are other texts we dont want, e.g. text/x-vcard
    # which some idiots include
    for part in typed_subpart_iterator(mesg, 'text','plain'):
	body = part.get_payload(decode=True) # decodes Content-Transfer-Encoding
	yield body
    # skipping html as it will contain the same link probably :p
    
class MailHandler():
    def __init__(self, email):
	for body in decodeMail(email):
	    for url in scanMail(body):
		self.do_http(url)


    def do_http(self, url):
	print "Visiting", url

	#url = "http://127.0.0.1:8000/?" + url.encode("base64").replace("\n","") + '/'
	agent = RedirectAgent(Agent(reactor))
	d = agent.request('GET', url, 
	    Headers({'User-Agent': ['Clickr']}),
	    None)
	def cbResponse(response):
	    from pprint import pformat
	    from twisted.internet.defer import Deferred	    
	    print 'Response version:', response.version
	    print 'Response code:', response.code
	    print 'Response phrase:', response.phrase
	    print 'Response headers:'
	    print pformat(list(response.headers.getAllRawHeaders()))	    
	    print 'Response received'
	    finished = Deferred()
	    response.deliverBody(BeginningPrinter(finished))
	    return finished
	#d.addCallback(cbResponse) # prints full http resp to console
	
	#def errback(err):
	#    print "damn :("
	#    err.printTraceback()
	#d.addErrback(errback)

from twisted.internet.protocol import Protocol
class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print 'Some data received:'
            print display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)

### test below

if __name__ == '__main__':
    print "Running test? [Y/n]"
    x = raw_input()
    if x == 'n':
	import sys; sys.exit(1)
    from os import listdir
    for filename in listdir("tests"):
	try:
	    if filename.startswith("mail"):
		print '-'*40	    
		print 'Testing', filename
    
		mailtext = open("tests/" + filename,"r").read()
	
		for body in decodeMail(mailtext):
		    for url in scanMail(body):
			print url
	
	except IOError:
	    continue
    

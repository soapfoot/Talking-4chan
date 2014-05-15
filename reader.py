import urllib2, subprocess
from bs4 import BeautifulSoup
from contextlib import closing

post_class_name = 'postMessage' #'postContainer replyContainer'

def parse_post(post):
    pass


def get_posts(url):
    parsed_posts = []
    # need to make sure page is closed after reading.
    # not really sure if this works, double check later
    with closing(urllib2.urlopen(url)) as page:
        soup = BeautifulSoup(page.read())
        posts = soup.find_all(class_=post_class_name)
        for post in posts:
            print '\n----------------------\n', post.prettify()
            parsed = parse_post(post)
            parsed_posts.append(parsed)
            # need to ignore quotelinks, and put quotes in their own special greentext context. maybe keep tuples,
            # with one as the content, and the other as content type, then dispatch text to speech on content type.
            # parsing the html itself shouldn't be too tough, unless you want to get fancy with contexts.
            # go line by line through the prettification, throw away all of the <br/>'s, and maybe make spoilers their
            # own thing too. that's about all that you can do i think. spoilers, greentexts, and regular text.
            # can also have a quote context so we can tell if it's a reply to someone.

            # <br/> parsed out
            # <s> </s> mark spoiler tags
            # remember to parse out the &gt; at the beginning of every quote block
            # quotelink classes can be identified with last 4 numbers? just put them in their own context for now,
            # deal with them later

            # text to speech bit:
            # say -f mynovel.txt -o myaudiobook.aiff
            # probably don't want to do txt files though, b/c we're planning on switching speaker tones and stuff.

    return parsed_posts


# vocalize a [(text, context)] array based on the context
def vocalize_in_context(voices):
    for text,context in voices:
        if context == 'normal':
            speaker = 'Kathy' # much better

        elif context == 'spoiler':
            speaker = 'Whisper' # perfect

        elif context == 'greentext':
            speaker = 'Alex' # better. i like how he sounds more aggressive. fits well

        else:
            speaker = 'Zarvox'

        say(text, speaker)
    return

def say(text, voice):
    subprocess.check_call(['say', text, '-v', voice])
    return

def main():
    # while thread has not 404'rd, crank posts.
    # say('Yolo live once negroes','Pipe Organ')
    vocalize_in_context([('implying i will read all of that fucking text', 'greentext')])#, ("pants sluts for ever uguu~", 'spoiler'),
        #('wearing a fedora tunic in winter', 'greentext')])
    #get_posts('https://boards.4chan.org/co/thread/61850685/rip-detective-quentin-the-cross-lance')

if __name__ == '__main__':
    main()
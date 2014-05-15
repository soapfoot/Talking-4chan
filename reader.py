import urllib2, subprocess
from bs4 import BeautifulSoup, Tag
from contextlib import closing

post_class_name = 'postMessage' #'postContainer replyContainer'

def parse_post(post):
    for line in post:
        if line.strip() == '<br/>':
            continue

            # <br/> parsed out
            # <s> </s> mark spoiler tags
            # remember to parse out the &gt; at the beginning of every quote block
            # quotelink classes can be identified with last 4 numbers? just put them in their own context for now,
            # deal with them later
    pass


def get_posts(url):
    parsed_posts = []
    # need to make sure page is closed after reading.
    # not really sure if this works, double check later
    with closing(urllib2.urlopen(url)) as page:
        soup = BeautifulSoup(page.read())
        posts = soup.find_all(class_=post_class_name)
        for post in posts:
            #print '\n--- Post ---\n'#, post.prettify(), '\n'

            for child in post.children:
                if isinstance(child, Tag):
                    if child.text.strip() == '':
                        continue
                    child_class = None
                    if child.get('class') is not None:
                        child_class = child.get('class')[0]
                    if child_class is not None:
                        if child_class == 'quotelink':
                            print 'Quotelink: ', child, '\ntext = ', child.text
                            parsed = (child.text, 'quotelink')
                        elif child_class == 'quote':
                            print 'Greentext: ', child, '\nText = ', child.text
                            parsed = (child.text, 'greentext')
                    elif '<s>' in str(child) and '</s>' in str(child):
                        print 'Spoiler: ', child.text
                        parsed = (child.text, 'spoiler')
                    else:
                        print 'Mystery text:', child
                        parsed = (child.text, 'mystery')
                else:
                    print 'Plain text:', child
                    parsed = (child, 'normal')
                parsed_posts.append(parsed)
    return parsed_posts


# vocalize a [(text, context)] array based on the context
# need to insert blank spots, or add waiting between posts.
# often they flow together uncomfortably.
def vocalize_in_context(voices):
    for text,context in voices:
        if context == 'normal':
            speaker = 'Kathy' # much better

        elif context == 'spoiler':
            speaker = 'Whisper' # perfect

        elif context == 'greentext':
            speaker = 'Alex' # better. i like how he sounds more aggressive. fits well
            text = text[1:] # omit the '>' todo: add text stripping to all of these
        elif context == 'quotelink':
            speaker = 'Kathy'
            text = 'at' + text[-4:] # only say the last 4 digits
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
    #vocalize_in_context([('implying i will read all of that fucking text', 'greentext')])#, ("pants sluts for ever uguu~", 'spoiler'),
        #('wearing a fedora tunic in winter', 'greentext')])
    posts = get_posts('https://boards.4chan.org/co/thread/61850685/rip-detective-quentin-the-cross-lance')

    vocalize_in_context(posts)

    # todo: group everything into a post.
    for text, mode in posts:
        print '--- --- ---'
        print 'Mode = ', mode
        print 'Text = ', text


if __name__ == '__main__':
    main()
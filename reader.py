import urllib2, subprocess, time, csvlogger
from bs4 import BeautifulSoup, Tag
from contextlib import closing

post_class_name = 'postMessage' #'postContainer replyContainer'
pause_between_posts = 1 # seconds
small_pause = .1
read_all = False # read all the posts on the first connection?

thread_url = 'https://boards.4chan.org/co/thread/61926344/homestuck-general'
log_file_name = thread_url.replace('/','_') + '.csv'

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


def get_posts(page):
    parsed_posts = []
    soup = BeautifulSoup(page)

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
                        # print 'Quotelink: ', child, '\ntext = ', child.text
                        parsed = (child.text, 'quotelink')
                    elif child_class == 'quote':
                        # print 'Greentext: ', child, '\nText = ', child.text
                        parsed = (child.text, 'greentext')
                elif '<s>' in str(child) and '</s>' in str(child):
                    # print 'Spoiler: ', child.text
                    parsed = (child.text, 'spoiler')
                else:
                    # print 'Mystery text:', child
                    parsed = (child.text, 'mystery')
            else:
                # print 'Plain text:', child
                parsed = (child, 'normal')
            # sanitize text
            #TODO: make this better
            parsed = (parsed[0].replace('-',' '), parsed[1])
            parsed_posts.append(parsed)
        parsed_posts.append(('', 'post_end'))
    return parsed_posts


# vocalize a [(text, context)] array based on the context
# need to insert blank spots, or add waiting between posts.
# often they flow together uncomfortably.

# having second thoughts about alex. he's kinda jarring and also not very fitting for the tone :/

def vocalize_in_context(voices):
    for text,context in voices:
        if context == 'post_end':
            time.sleep(small_pause)
            #say('e', 'Agnes') # end of post signifier todo: play a tone instead of an awkward letter
            time.sleep(pause_between_posts)
            continue
        elif context == 'normal':
            speaker = 'Kathy' # much better

        elif context == 'spoiler':
            speaker = 'Whisper' # perfect

        elif context == 'greentext':
            speaker = 'Trinoids' # better. i like how he sounds more aggressive. fits well
            text = text[1:] # omit the '>' todo: add text stripping to all of these
        elif context == 'quotelink':
            speaker = 'Kathy'
            tail = text[-3:]
            text = 'at ' + tail[0] + ' ' + tail[1] + ' ' + tail[2]
            #text = 'at' + text[-4:] # only say the last 3 digits
        else:
            speaker = 'Zarvox'

        say(text, speaker)
    return

def say(text, voice):
    subprocess.check_call(['say', text, '-v', voice])
    return

def main():
    # while thread has not 404'rd, crank posts.




    response = urllib2.urlopen(thread_url)

    last_modified = response.info().get('Last-Modified', False)
    print last_modified, 'type = ', type(last_modified)

    # Sun, 18 May 2014 03:52:32 GMT
    # Sun, 18 May 2014 03:55:15 GMT

    # external thread specc'd by:
    # /co/thread/61864382#p61864382
    # so you can probably just blindly copy and paste into the url.

    # laziest possible solution
    posts = get_posts(response.read())
    response.close()

    csvlogger.log(log_file_name, posts) # currently does nothing to prevent duplication of data todo: fix this

    if read_all == True:
        vocalize_in_context(posts)
    while True:
        response = urllib2.urlopen(thread_url)
        modified = response.info().get('Last-Modified', False)
        print 'last modified at:', modified

        if modified != last_modified:
            print 'found a new post'
            last_modified = modified

            new_posts = get_posts(response.read())
            response.close()

            vocalize_in_context(new_posts[len(posts):]) # still too fucking lazy
            csvlogger.log(log_file_name, new_posts)
            posts = new_posts
        else:
            print "Waiting for new replies..."
            time.sleep(10)

    #vocalize_in_context(posts)



if __name__ == '__main__':
    main()
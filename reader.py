import urllib2, subprocess, time, csvlogger
from bs4 import BeautifulSoup, Tag
from contextlib import closing

post_class_name = 'postMessage' # specific to four channel. brittle.
pause_between_posts = 1         # time paused between posts. in seconds
small_pause = .1                # small pause used before playing the post separator tone. also in seconds
read_all = False                # read all the posts out loud on the first connection? will drone on for a while if
                                # it's a long thread
debug = False

thread_url = 'https://boards.4chan.org/co/thread/61926344/homestuck-general'
log_file_name = thread_url.replace('/','_') + '.csv' # sanitizing url because '/' gets read as a directory
                                                     # todo: doublecheck if this is enough

def get_posts(page):
    parsed_posts = []

    # use BeautifulSoup to get all of the posts in the page. Will break if the post_class_name is wrong, so currently
    # this only works for threads on four channel.
    soup = BeautifulSoup(page)
    posts = soup.find_all(class_=post_class_name)
    for post in posts:
        # a single post contains an ordered sequence of various kinds of text: spoiler text, greentext, quotelinks,
        # and regular text. we handle this by parsing each of the post's children in turn, which fall into one of the
        # above categories. note that "for child in post.children" will preserve the original order of the children,
        # which is very convenient.
        if debug:
            print '\n--- Post ---\n', post.prettify(), '\n'
        for child in post.children:
            if isinstance(child, Tag): # used to classify the parts of a post that contain quotes, greentext, or spoiler
                                       # text.
                if child.text.strip() == '':
                    # do nothing for posts without text. this may change if i can thing of anything interesting to do
                    # with posts that are just images
                    continue

                # an awkward workaround to make sure we never call a method of an object that is None.
                # todo: try to think of a nicer way to handle this
                child_class = None
                if child.get('class') is not None:
                    child_class = child.get('class')[0]
                if child_class is not None:
                    if child_class == 'quotelink':
                        if debug:
                            print 'Quotelink: ', child, '\ntext = ', child.text
                        parsed = (child.text, 'quotelink')
                    elif child_class == 'quote':
                        if debug:
                            print 'Greentext: ', child, '\nText = ', child.text
                        parsed = (child.text, 'greentext')
                elif '<s>' in str(child) and '</s>' in str(child):
                    if debug:
                        print 'Spoiler: ', child.text
                    parsed = (child.text, 'spoiler')
                else:
                    if debug:
                        print 'Mystery text:', child
                    parsed = (child.text, 'mystery')
            else: # child is just text so we don't need to extract its text with the .text method
                if debug:
                    print 'Plain text:', child
                parsed = (child, 'normal')
            # sanitize text. passing "-foo" to the say command will cause it to mistake foo for a command line arg
            # so we need to get rid of all the hyphens
            #TODO: make this better. also check for other corner cases.
            parsed = (parsed[0].replace('-',' '), parsed[1])
            parsed_posts.append(parsed)
        parsed_posts.append(('', 'post_end')) # this would be a good spot to put post metadata like poster name.
                                              # putting a post id would also make weeding out duplicates easier
    return parsed_posts


# vocalize a [(text, context)] list based on the context
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
            speaker = 'Trinoids' # better.
            text = text[1:] # omit the '>' at the beginning of greentext posts
        elif context == 'quotelink':
            speaker = 'Kathy'
            tail = text[-3:]
            text = 'at ' + tail[0] + ' ' + tail[1] + ' ' + tail[2] # only say the last 3 digits of the quoted post
                                                                   # number.
        else:
            speaker = 'Zarvox'

        say(text, speaker)

    return

def say(text, voice):
    subprocess.check_call(['say', text, '-v', voice])
    return

def main():

    response = urllib2.urlopen(thread_url)

    # get the last time the page was modified. since the posts are added by appending them to the current page,
    # this allows us to check and see if there are any new posts we should read out
    last_modified = response.info().get('Last-Modified', False)
    print last_modified, 'type = ', type(last_modified)

    posts = get_posts(response.read())
    response.close()

    #csvlogger.log(log_file_name, posts) # currently does nothing to prevent duplication of data todo: fix this

    if read_all == True:
        vocalize_in_context(posts)

    while True: # should really be: while thread hasn't 404'd:
        response = urllib2.urlopen(thread_url)
        modified = response.info().get('Last-Modified', False)
        print 'last modified at:', modified

        # since the only way they might not be equal is if the page has been updated, we assume it has been updated
        # with new posts. we then process these new posts.
        if modified != last_modified:
            if debug:
                print 'found a new post'
            last_modified = modified
            new_posts = get_posts(response.read()) # re-does a lot of work
                                                   # need to cut out only the new posts and only process those
            response.close()
            vocalize_in_context(new_posts[len(posts):]) # still too damn lazy
            csvlogger.log(log_file_name, new_posts) # write the post text and category to a csv file for later use
            posts = new_posts
        else:
            if debug:
                print "Waiting for new replies..."
            time.sleep(10)

    # thread following feature sketch:
    # external thread specc'd by:
    # /co/thread/61864382#p61864382
    # so you can probably just blindly copy and paste into the url.
    # so we look for a quotelink with an external url, then follow the url. if it contains 'hsg', ..., other keywords,
    # switch over to that thread. still have a corner case where thread gets deleted without a link to the new one.
    # we can sit on the archive and look for hsgs. need to keep track of, which threads we've already been in, and
    # only visit more recent ones.



if __name__ == '__main__':
    main()
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from urllib.request import urlretrieve
import os, re, time

def dl_instagram(cmd):
    cmds = cmd.split(' ')
    usr = cmds[1]
    Firefox = webdriver.Firefox()
    profile_url = 'https://www.instagram.com/' + usr + '/'
    Firefox.get(profile_url)
    page_source = Firefox.page_source
    
    if page_source.find('This Account is Private') != -1:
        #login
        Firefox.get('https://www.instagram.com/accounts/login/')
        f = open('logins.txt')
        login_data = f.readlines()
        for line in login_data:
            if line[0:10] == 'instagram:':
                inst,usr,passw = line.split(':')
        WebDriverWait(Firefox, timeout=60).until(lambda d: Firefox.find_element_by_name('username'))
        Firefox.find_element_by_name('username').send_keys(usr)
        Firefox.find_element_by_name('password').send_keys(passw)
        Firefox.find_element_by_css_selector('._o0442').click()
        WebDriverWait(Firefox, timeout=10).until(lambda d: Firefox.find_element_by_css_selector('._vbtk2'))

    if Firefox.current_url != profile_url:
        Firefox.get(profile_url)
    try:
        WebDriverWait(Firefox, timeout=10).until(lambda d: Firefox.find_element_by_css_selector('._oidfu'))
        Firefox.find_element_by_css_selector('._oidfu').click()
    except:
        print('No \'Load more\' button found')

    page_source_orig = Firefox.page_source
    Firefox.execute_script('window.scrollTo(0, 0);')
    time.sleep(0.2)
    Firefox.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    page_source_new = Firefox.page_source
    while True:
        page_source_orig = page_source_new
        Firefox.execute_script('window.scrollTo(0, 0);')
        time.sleep(1)
        Firefox.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        page_source_new = Firefox.page_source
        if page_source_orig == page_source_new:
            break
    
    postNo = int(Firefox.find_element_by_css_selector('._bkw5z').get_attribute('innerHTML'))
    print(str(postNo) + ' images to dl')
    
    links = []
    for link in re.findall('/p/[0-9A-Za-z_-]*/', page_source_new):
        link = 'https://www.instagram.com' + link
        links.append(link)

    # sometimes errors here, solution for now is just restart program
    while postNo != len(links):
        print('Something went wrong! Mismatch between post count and links found')
        print(str(postNo) + ' : ' + str(len(links)))
        Firefox.execute_script('window.scrollTo(0, 0);')
        time.sleep(2)
        Firefox.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        links = []
        for link in re.findall('/p/[0-9A-Za-z_-]*/', page_source_new):
            link = 'https://www.instagram.com' + link
            links.append(link)

    rip_folder = 'rips\\instagram_' + usr
    if not os.path.isdir(rip_folder):
        os.mkdir(rip_folder)

    current_date = time.strftime('%Y.%m.%d')
    fname_profile = rip_folder + '\\instagram.' + usr + '._profile.' + current_date[2:] + '.jpg'
    profile_img = Firefox.find_element_by_css_selector('._r43r5').get_attribute('src')
    s2 = profile_img.find('/', 9)
    s3 = profile_img.find('/', s2 + 1)
    s4 = profile_img.find('/', s3 + 1)
    profile_img = 'https://scontent-atl3-1.cdninstagram.com/' + profile_img[s4:]
    profile_img = re.sub('[a-z][0-9][0-9][0-9][a-z][0-9][0-9][0-9]', '', profile_img)
    print(profile_img)
    urlretrieve(profile_img, fname_profile)

    i = 0
    for link in links:
        i = i + 1
        Firefox.get(link)
        WebDriverWait(Firefox, timeout=60).until(lambda d: Firefox.find_element_by_css_selector('._379kp'))
        date_raw = Firefox.find_element_by_css_selector('._379kp').get_attribute('datetime')
        date = date_raw[2:10].replace('-','.')

        if Firefox.page_source.find('video/mp4') == -1:
            img_src_start = Firefox.page_source.find('https://scontent')
            img_src_end = Firefox.page_source.find('.jpg', img_src_start) + 4
            img_src = Firefox.page_source[img_src_start:img_src_end]
            s2 = img_src.find('/e')
            s3 = img_src.find('/', s2 + 1)
            new_src = 'https://scontent-atl3-1.cdninstagram.com/' + img_src[s3:]
            new_src = re.sub('[a-z][0-9][0-9][0-9][a-z][0-9][0-9][0-9]', '', new_src)
            print('(' + str(i) + '/' + str(postNo) + ') ' + new_src)
            fname = rip_folder + '\\instagram.' + usr + '.' + date + '.' + Firefox.current_url.replace('https://www.instagram.com/p/', '').replace('/', '') + '.jpg'
            if not os.path.exists(fname):
                urlretrieve(new_src, fname)
        else:
            img_src_start = Firefox.page_source.find('https://scontent')
            img_src_start = Firefox.page_source.find('https://scontent', img_src_start + 20)
            img_src_end = Firefox.page_source.find('.mp4', img_src_start) + 4
            img_src = Firefox.page_source[img_src_start:img_src_end]
            print('(' + str(i) + '/' + str(postNo) + ') ' + img_src)
            fname = rip_folder + '\\instagram.' + usr + '.' + date + '.' + Firefox.current_url.replace('https://www.instagram.com/p/', '').replace('/', '') + '.mp4'
            if not os.path.exists(fname):
                urlretrieve(img_src, fname)

    print('\n')
    Firefox.quit()

cmd = '2'
while cmd != '':
    cmd = input('> ')
    if cmd[0:10] == 'instagram ':
        dl_instagram(cmd)

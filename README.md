# dload - Download Library

A python library to simplify your download tasks.


### Requirements:
+ python >= 3.6 

### Dependencies:
+ requests>=2.22.0

Install `dload` on your system : 

```
pip install dload
```

Load `dload` into your code : 

```
import dload
```

## Usage Examples:

#### Download and save a remote file:
```
dload.save('https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Albert_Einstein_Head.jpg/800px-Albert_Einstein_Head.jpg', '~/einstein.jpg')  
```

#### Download and save an FTP file:
```
dload.ftp('ftp://speedtest.tele2.net/5MB.zip', '~/5MB.zip') 
```

#### Returns the remote file as a byte obj:
```
dload.bytes('https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Albert_Einstein_Head.jpg/800px-Albert_Einstein_Head.jpg')
```

#### Returns the remote file as a dict:
```
dload.json("https://support.oneskyapp.com/hc/en-us/article_attachments/202761627/example_1.json")
```

#### Returns the server reply headers as a dict:
```
dload.headers("https://support.oneskyapp.com/hc/en-us/article_attachments/202761627/example_1.json")
```

#### Returns the remote file as a string:
```
dload.text("https://www.w3.org/TR/PNG/iso_8859-1.txt")
```

#### Multi threaded downloader from a python list
```
file_list = ["https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i386-pc-solaris2.8.tar.gz",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i386-unknown-netbsdelf1.6.tar.bz2",
             "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/linux-i686/da-DK/firefox-1.0.6.tar.gz",
             "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/linux-i686/da-DK/firefox-1.0.6.installer.tar.gz",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i686-pc-linux-gnu-ctl-svg.tar.gz",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-sparc-sun-solaris2.8-gtk2.tar.gz",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-os2-0.8.zip",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/FirefoxSetup-0.8.exe",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/Firefox-0.8.zip",
             "https://ftp.mozilla.org/pub/firefox/releases/0.8/firefox-source-0.8.tar.bz2",
             "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/win32/cs-CZ/Firefox%20Setup%201.0.6.exe"]`

save_multi(file_list, "d:/test_dowmload/", max_threads=10)
```


#### Multi threaded downloader from a text file
```
file_list = "d:/file_list.txt"
save_multi(file_list, "d:/test_download_text/", max_threads=10)
```


#### Download Speed Test
```
dload.speed_test()
dload.speed_test(10)
dload.speed_test(50, "ipv6")
dload.speed_test(1024, port=8080)

[==============================] 61.34037 Mbps
100MB = 17.10 seconds
```

#### Save and Extract a remote zip
```
dload.save_unzip("https://file-examples.com/wp-content/uploads/2017/02/zip_2MB.zip")
```

#### Clone a git repo to local computer
```
dload.git_clone("https://github.com/x011/dload.git")
```

### FUNCTIONS

    bytes(url)
        Returns the remote file as a byte obj
        :param url: str - url to download
        :return: bytes
    
    down_speed(size=5, ipv='ipv4', port=80)
        Measures the download speed
        :param size: int -  (optional) 5, 10, 20, 50, 100, 200, 512, 1024 Mb
        :param ipv: str - (optional) ipv4, ipv6
        :param port: int - (optional) 80, 81, 8080
        :return: boolean
    
    ftp(ftp_url, local_path='', overwrite=False)
        Download and save an FTP file
        :param url: str - ftp://ftp.server.tld/path/to/file.ext or ftp://username:password@ftp.server.tld/path/to/file.ext
        :param localpath: str - (optional) local path to save the file, i.e.: /home/myfile.ext or c:/myfile.ext
        :param overwrite: bool - (optional) If True the local file will be overwritten, False will skip the download
        :return: str - local path of the downloaded file
    
    git_clone(git_url, clone_dir='')
        Clones a git repo to local computer
        :param git_url: str - git url, ex: https://github.com/x011/dload.git
        :param clone_dir: str - (optional) local dir to clone the git, ex: /path/to/dload/ or c:/repos/dload/, defaults to repo name on script dir
        :return: str - path to local repo dir or an empty tring
    
    headers(url, redirect=True)
        Returns the reply headers as a dict
        :param url: str - url to retrieve the reply headers
        :param redirect: boolean - (optional) should we follow redirects?
        :return: dict
    
    json(url)
        Returns the remote file as a dict
        :param url: str - url to retrieve the json
        :return: dict
    
    rand_fn()
        provides a random filename when it's impossible to determine the filename, i.e.: http://site.tld/dir/
        :return: str
    
    save(url, path='', overwrite=False, timeout=30, chunk_size=8192)
        Download and save a remote file
        :param url: str - file url to download
        :param path: str - (optional) Full path to save the file, ex: c:/test.txt or /home/test.txt.
        Defaults to script location and url filename
        :param overwrite: bool - (optional)  If True the local file will be overwritten, False will skip the download
        :param chunk_size: int - (optional) streaming chunk size in bytes for writing to disk
        :param raise_on_error: bool - (optional) If True re-raises download errors instead
        of returning an empty string
        :return: str - The full path of the downloaded file or an empty string
    
    save_multi(url_list, dir='', max_threads=1, tsleep=0.05)
        Multi threaded file downloader
        :param url_list: str or list - A python list or a path to a text file containing the urls to be downloaded
        :param dir: str - (optional) Directory to save the files, will be created if it doesn't exist
        :param max_threads: int - (optional)  Max number of parallel downloads
        :param tsleep: int or float - (optional)  time to sleep in seconds when the max_threads value is reached, i.e: 0.05 or 1 is accepted
        :return: boolean
    
    save_unzip(zip_url, extract_path='', delete_after=False)
        Save and Extract a remote zip
        :param zip_url: str - the zip file url to download
        :param extract_path: str - (optional) the path to extract the zip file, defaults to local dir
        :param delete_after: bool - (optional) if the zip file should be deleted after, defaults to False
        :return: str - the extract path or an empty string
    
    text(url, encoding='')
        Returns the remote file as a string
        :param url: str - url to retrieve the text content
        :param encoding: str - (optional) character encoding
        :return: str
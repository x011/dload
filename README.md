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
dload.save(
    "https://example-files.online-convert.com/raster%20image/jpg/example.jpg",
    "~/example.jpg",
    overwrite=True,
)
```

#### Download and save an FTP file:
```
dload.ftp(
    "https://ftp.mozilla.org/pub/firefox/releases/52.9.0esr/firefox-52.9.0esr.win64.sdk.zip",
    "~/firefox-52.9.0esr.win64.sdk.zip",
    overwrite=True,
)
```

#### Return the remote file as bytes:
```
data = dload.bytes("https://example-files.online-convert.com/document/txt/example.txt")
print(len(data))
```

#### Return parsed JSON (dict, list, or scalar):
```
payload = dload.json("https://example-files.online-convert.com/filelist.json")
print(type(payload), payload)
```

#### Return server reply headers as a dict:
```
dload.headers("https://example-files.online-convert.com/filelist.json")
```

#### Return the remote file as a string:
```
text = dload.text("https://example-files.online-convert.com/document/txt/example.txt")
print(text[:60])
```

#### Save and extract a remote zip
```
dload.save_unzip(
    "https://example-files.online-convert.com/archive/zip/example.zip",
    delete_after=True,
)
```

#### Clone a git repo to local computer
```
dload.git_clone("https://github.com/x011/dload.git")
```

#### Multi-threaded downloader from a python list
```
file_list = [
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i386-pc-solaris2.8.tar.gz",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i386-unknown-netbsdelf1.6.tar.bz2",
    "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/linux-i686/da-DK/firefox-1.0.6.tar.gz",
    "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/linux-i686/da-DK/firefox-1.0.6.installer.tar.gz",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i686-pc-linux-gnu-ctl-svg.tar.gz",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-sparc-sun-solaris2.8-gtk2.tar.gz",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-os2-0.8.zip",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/FirefoxSetup-0.8.exe",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/Firefox-0.8.zip",
    "https://ftp.mozilla.org/pub/firefox/releases/0.8/firefox-source-0.8.tar.bz2",
    "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/win32/cs-CZ/Firefox%20Setup%201.0.6.exe",
]

dload.save_multi(file_list, "/tmp/dload-multi/", max_threads=10)
```


#### Multi-threaded downloader from a text file
```
file_list = "/tmp/file_list.txt"
dload.save_multi(file_list, "/tmp/test_download_text/", max_threads=10)
```


#### Download Speed Test
```
dload.down_speed()
dload.down_speed(10)
dload.down_speed(50, "ipv6")
dload.down_speed(1024, port=8080)

[==============================] 61.34037 Mbps
100MB = 17.10 seconds
```

### FUNCTIONS

    bytes(url, timeout=30, raise_on_error=True)
        Returns the remote file as bytes.
        :param url: str - url to download
        :param timeout: int - (optional) request timeout in seconds
        :param raise_on_error: bool - (optional) If True re-raises download errors; otherwise returns b"" on failure
        :return: bytes

    down_speed(size=5, ipv='ipv4', port=80, raise_on_error=True)
        Measures the download speed
        :param size: int -  (optional) 5, 10, 20, 50, 100, 200, 512, 1024 Mb
        :param ipv: str - (optional) ipv4, ipv6
        :param port: int - (optional) 80, 81, 8080
        :param raise_on_error: bool - (optional) If True re-raises download errors; otherwise returns False
        :return: boolean

    ftp(ftp_url, local_path='', overwrite=False, timeout=30, raise_on_error=True)
        Download and save an FTP file
        :param ftp_url: str - ftp://ftp.server.tld/path/to/file.ext or ftp://username:password@ftp.server.tld/path/to/file.ext
        :param local_path: str - (optional) local path to save the file, i.e.: /home/myfile.ext or c:/myfile.ext
        :param overwrite: bool - (optional) If True the local file will be overwritten, False will skip the download
        :param timeout: int - (optional) request timeout in seconds
        :param raise_on_error: bool - (optional) If True re-raises download errors; otherwise returns an empty string
        :return: str - local path of the downloaded file

    git_clone(git_url, clone_dir='', raise_on_error=True)
        Clones a git repo to local computer
        :param git_url: str - git url ending in .git, ex: https://github.com/x011/dload.git
        :param clone_dir: str - (optional) local dir to clone the git, ex: /path/to/dload/ or c:/repos/dload/, defaults to repo name on script dir
        :param raise_on_error: bool - (optional) If True re-raises download or extraction errors; otherwise returns an empty string
        :return: str - path to local repo dir or an empty string

    headers(url, redirect=True, timeout=30, raise_on_error=True)
        Returns the reply headers as a dict
        :param url: str - url to retrieve the reply headers
        :param redirect: boolean - (optional) should we follow redirects?
        :param timeout: int - (optional) request timeout in seconds
        :param raise_on_error: bool - (optional) If True re-raises download errors; otherwise returns an empty dict
        :return: dict

    json(url, timeout=30, raise_on_error=True)
        Returns parsed JSON data (dict, list, etc.)
        :param url: str - url to retrieve the json
        :param timeout: int - (optional) request timeout in seconds
        :param raise_on_error: bool - (optional) If True re-raises download errors; otherwise returns an empty dict
        :return: Parsed JSON or an empty dict on failure

    rand_fn()
        provides a random filename when it's impossible to determine the filename, i.e.: http://site.tld/dir/
        :return: str

    save(url, path='', overwrite=False, timeout=30, chunk_size=8192, raise_on_error=True)
        Download and save a remote file
        :param url: str - file url to download
        :param path: str - (optional) Full path to save the file, ex: c:/test.txt or /home/test.txt.
        Defaults to script location and url filename or Content-Disposition filename
        :param overwrite: bool - (optional)  If True the local file will be overwritten, False will skip the download
        :param timeout: int - (optional) request timeout in seconds
        :param chunk_size: int - (optional) streaming chunk size in bytes for writing to disk
        :param raise_on_error: bool - (optional) If True re-raises download errors instead
        of returning an empty string
        :return: str - The full path of the downloaded file or an empty string

    save_multi(url_list, dir='', max_threads=1, tsleep=0.05, timeout=30, raise_on_error=True)
        Multi threaded file downloader
        :param url_list: str or list - A python list or a path to a text file containing the urls to be downloaded
        :param dir: str - (optional) Directory to save the files, will be created if it doesn't exist
        :param max_threads: int - (optional)  Max number of parallel downloads
        :param tsleep: int or float - (optional)  time to sleep in seconds when the max_threads value is reached, i.e: 0.05 or 1 is accepted
        :param timeout: int - (optional) request timeout in seconds
        :param raise_on_error: bool - (optional) If True re-raises the first download error; otherwise returns False when a download fails
        :return: boolean

    save_unzip(zip_url, extract_path='', delete_after=False, raise_on_error=True)
        Save and Extract a remote zip
        :param zip_url: str - the zip file url to download
        :param extract_path: str - (optional) the path to extract the zip file, defaults to local dir
        :param delete_after: bool - (optional) if the zip file should be deleted after, defaults to False
        :param raise_on_error: bool - (optional) If True re-raises download/extract errors; otherwise returns an empty string
        :return: str - the extract path or an empty string

    text(url, encoding='', timeout=30, raise_on_error=True)
        Returns the remote file as a string
        :param url: str - url to retrieve the text content
        :param encoding: str - (optional) character encoding
        :param timeout: int - (optional) request timeout in seconds
        :param raise_on_error: bool - (optional) If True re-raises download errors; otherwise returns an empty string
        :return: str

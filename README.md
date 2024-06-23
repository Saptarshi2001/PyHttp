# grp
Pyhttp is an http server written from scratch in python to understand the http protocol .As of now what pyhttp does is:-

- Supports GET , HEAD , DELETE
- Supports status codes 200 , 400 , 501
- Capability of handling multiple conections
- Renders images and videos in the browser

## Getting Started

To compile and run the program, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/your-repo.git`
2. Run the httpproto file by running the following the command : `python httpproto.py`
3. For sending GET request,run 127.0.0.1:8080/hello.html
4. For sending HEAD request,use curl -I 127.0.0.1:8080/hello.html
5. For sending DELETE request,use curl -X "DELETE" '127.0.0.1:8080/hello.html'    



## System requirements
- python 3.6 or higher

## Roadmap 
- Adding the http access control
- Adding the http authentication
- Adding the http caching
- Adding the http cookies
- Last but not the least,if everything goes well, i also want to build a framework on top of it. Something similar to [aiohttp](https://github.com/aio-libs/aiohttp) 

## Contributing
- This project is under development.Feel free to contribute to it.
  

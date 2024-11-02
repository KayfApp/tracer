# tracer

Client searches through provider instances and/or servers

Providers essentially just cluster together data and assign identification to it

Providers define a fetch method, that is handled by wrapper to populate a local database
- When searching, the provider signature is used to backtrack where the data came from

Servers consist of providers and servers, and their purpose it to decentralize data
- They may also provide a high-performance environment for service execution
- They may also provide a way to avoid duplicate data (for saving storage) by only storing global company data once
    - Or at least less times than each users saving it locally

Servers consisting of multiple servers act like clients to those servers and will still only produce one *server summary*

A server summary is performed by sumbitting the query and meta data to direct neighbours (servers) and summarizing their results


Receive query -> Translate query -> Search with translated query -> Receive results -> Translate documents back to original language

Fetch data (every x-s for every provider) -> get document -> translate document -> save document to db

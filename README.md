# namesilo python api client

## API request limit
Status code 429 does mean you run into request limit of 60 per 1 minute.

Currently this is resolved by timing out the next request for 65 seconds.

This is not the best solution but this solves the current problem, i might want to rewrite the requests and timeout function.

Since im running this tool on multiple machines for multiple jobs (syncing entries using ansible, dyndns from home, etc..) implementing a cache might work but this might create the issue of not updating records even if some other tool set a record in between updating the cache and setting the same record from another tool.
Then locating the issue might get harder.

i dont know the best solution right now. might come back to this later.

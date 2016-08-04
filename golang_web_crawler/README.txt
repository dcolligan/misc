A web crawler written in golang.

The code consists of three packages: crawl, crawler and urlmatcher.  crawler has the majority of the code, urlmatcher is a helper package for crawler, and crawl is a tiny package that simply executes the crawler.  Both crawler and urlmatcher have tests.  crawler scans the digitalocean.com site and creates a link graph.  It then dumps this graph to a file, results.txt.  Changing the const values in crawler.go (for instance, tweaking the number of worker goroutines) will change the behavior of the crawler.

The code depends on a third party XML parsing library which you can retrieve by running:

$ go get "github.com/moovweb/gokogiri"

Once that is done, to execute the crawler, run (in the crawl directory):

$ go run crawl.go

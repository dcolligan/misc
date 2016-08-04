package crawler

import (
   "fmt"
   "time"
   "github.com/moovweb/gokogiri" // using this since encoding/xml's parser doesn't parse digitalocean's site correctly
   "net/http"
   "log"
   "io/ioutil"
   "github.com/dannycolligan/urlmatcher"
   "sort"
   "os"
   "io"
)

type KV struct {
   K string
   V []string
}

var state *State
type State struct {
   Unvisited map[string]bool
   Visited map[string][]string
   Current map[string]bool
}

var config *Config
type Config struct {
   Start time.Time
   End time.Time
   NumWorkers int
   NumItems int
   BufLen int
   RootUrl string
   UrlMatcherPattern string
   ResultFileName string
   UrlMatcher* urlmatcher.UrlMatcher
}

type CrawlerLogger interface {
   Fatal(v ...interface{})
   Printf(format string, v ...interface{})
   Println(v ...interface{})
}

type CrawlerHttp interface {
   Get(uri string) (http.Response, error)
}

// variables that we mock up in the tests
var logger CrawlerLogger
var network func(uri string) (*http.Response, error)
var byteReader func(r io.Reader) ([]byte, error)

const (
   configBufLen = 10
   configNumWorkers = 10
   rootUrl = "http://digitalocean.com"
   urlMatcherPattern = "^https?://digitalocean.com"
   resultFileName = "results.txt"
)

// logs an unrecoverable error and quits
func checkFatal(e error) {
   if e != nil {
      logger.Fatal(e)
   }
}

// logs a serious error
func logError(e error) {
   logger.Printf("ERROR: %s\n", e)
}

// initializes the crawler configuration
func setup() {
   config = new(Config)
   config.BufLen = configBufLen
   config.NumWorkers = configNumWorkers
   config.Start = time.Now()
   config.RootUrl = rootUrl
   config.UrlMatcherPattern = urlMatcherPattern
   config.ResultFileName = resultFileName
   config.UrlMatcher = new(urlmatcher.UrlMatcher)
   config.UrlMatcher.Pattern = urlMatcherPattern
   config.UrlMatcher.Base = rootUrl
   logger = log.New(os.Stdout, "", log.Ldate | log.Ltime)
   network = http.Get
   byteReader = ioutil.ReadAll
   logger.Printf("Starting with %d worker(s)\n", configNumWorkers)
}

func createChannels() (chan string, chan *KV, chan bool) {
   input := make(chan string, config.BufLen)
   output := make(chan *KV, config.BufLen)
   workerDone := make(chan bool, config.BufLen)
   return input, output, workerDone
}

func Run() {
   setup()
   input, output, workerDone := createChannels()

   // start workers and arbiter
   for i := 0; i < config.NumWorkers; i++ {
      go worker(i, input, output, workerDone)
   }
   go arbiter(input, output)

   // wait for (arbiter, then) workers to finish and close channels
   for i := 0; i < config.NumWorkers; i++ {
      <-workerDone
   }
   close(workerDone)
   close(output)

   report(state)
   reportResults()
   writeResults()
}

// report the results of the crawler run
func reportResults() {
   config.End = time.Now()
   diff := config.End.Unix() - config.Start.Unix()
   logger.Printf("%d, %d, %d\n", config.Start.Unix(), config.End.Unix(), diff)
}

// write the link graph to a file
func writeResults() {
   file, err := os.Create(config.ResultFileName)
   checkFatal(err)
   defer file.Close()

   visitedKeys := make([]string, len(state.Visited))
   i := 0
   for k, _ := range state.Visited {
      visitedKeys[i] = k
      i++
   }
   sort.Strings(visitedKeys)

   for _, k := range visitedKeys {
      file.WriteString(fmt.Sprintf("%s\n", k))
      v := state.Visited[k]
      for _, e := range v {
         file.WriteString(fmt.Sprintf("\t%s\n", e))
      }
   }
}

// report a status update on the crawler state
func report(state *State) {
   logger.Printf("uv: %d v: %d, cur: %d\n", len(state.Unvisited), len(state.Visited), len(state.Current))
}

// ensures that only one of the producer and the consumer
// is called at any one time, so they don't access the
// state at the same time and cause a race condition
func arbiter(input chan<- string, output <-chan *KV) {
   state = new(State)
   state.Unvisited = map[string]bool{rootUrl : true}
   state.Visited = make(map[string][]string)
   state.Current = make(map[string]bool)

   update := true
   for {
      select {
      case kv := <-output:
         consumer(state, kv)
         update = true
      default:
         if(!producer(state, input)) {
            close(input)
            return
         }
         if update {
            report(state)
         }
         update = false
      }
   }
}

// consumes work by the workers and updates the state
func consumer(state *State, kv *KV) {
   for _, e := range kv.V {
      _, vp := state.Visited[e]
      _, up := state.Unvisited[e]
      if !vp && !up {
         state.Unvisited[e] = true
      }
   }
   sort.Strings(kv.V)
   state.Visited[kv.K] = kv.V
   delete(state.Current, kv.K)
   delete(state.Unvisited, kv.K)
}

// get an arbitrary key from the Unvisited map
// (we know that there is at least one since that condition is
// satisfied when the producer calls it)
func getArbitraryUnvisitedKey(state *State) string {
   var item string
   for k, _ := range state.Unvisited {
      _, c := state.Current[k]
      if !c {
         item = k
         break
      }
   }
   return item
}

// signals the workers that work needs to be performed
func producer(state *State, input chan<- string) bool{
   if len(state.Unvisited) > 0 && len(state.Unvisited) > len(state.Current) {
      item := getArbitraryUnvisitedKey(state)
      state.Current[item] = true
      input <- item
   } else if len(state.Unvisited) == 0 && len(state.Current) == 0 {
      return false
   }
   return true
}

// fetches a web page, crawls it, and signals the consumer
func worker(id int, input <-chan string, output chan<- *KV, workerDone chan<- bool) {
   for uri := range input {
      // crawl the page
      links := crawlPage(uri)

      // store the crawled links
      linkArray := make([]string, len(links))
      i := 0
      for k, _ := range links {
         linkArray[i] = k
         i++
      }
      kv := new(KV)
      kv.K = uri
      kv.V = linkArray
      output <- kv
   }
   workerDone <- true
}

// fetch and web page and scan it for links
func crawlPage(uri string) map[string]bool {
   links := map[string]bool{}

   // request page
   logger.Println(uri)
   resp, err := network(uri)
   if err != nil {
      logError(err)
      return links
   }
   logger.Printf("%s %s\n", uri, resp.Status)
   bytes, err := byteReader(resp.Body)
   if err != nil {
      logError(err)
      return links
   }

   // parse links from xml
   doc, _ := gokogiri.ParseHtml(bytes)
   defer doc.Free()
   interf, err := doc.Search("//a[@href]")
   if err != nil {
      logError(err)
      return links
   }
   for _, node := range interf {
      link := node.Attributes()
      href := link["href"]
      s := fmt.Sprintf("%s", href)
      isValid, canonical := config.UrlMatcher.IsValidURL(s)

      if isValid && !links[canonical] {
         links[canonical] = true
      }
   }

   return links
}

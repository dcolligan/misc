package crawler

import (
   "testing"
   "errors"
   "time"
   "os"
   "strings"
   "net/http"
   "github.com/dannycolligan/urlmatcher"
   "io"
)

// mocks

var fatalCalls int
var printfCalls int
var printlCalls int

type MockLogger struct {
}

func (ml *MockLogger) Fatal(v ...interface{}) {
   fatalCalls++
}

func (ml *MockLogger) Printf(format string, v ...interface{}) {
   printfCalls++
}

func (ml *MockLogger) Println(v ...interface{}) {
   printlCalls++
}

func initMockLogger() {
   fatalCalls = 0
   printfCalls = 0
   printlCalls = 0
}

func assertLogCalls(t *testing.T, fatal int, printf int, printl int) {
   if fatalCalls != fatal {
      t.Errorf("fatalCalls was %d instead of %d", fatalCalls, fatal)
   }
   if printfCalls != printf {
      t.Errorf("printfCalls was %d instead of %d", printfCalls, printf)
   }
   if printlCalls != printl {
      t.Errorf("printlCalls was %d instead of %d", printlCalls, printl)
   }
}

// checkFatal
func TestCheckFatal(t *testing.T) {
   logger = &MockLogger{}
   initMockLogger()

   checkFatal(nil)
   assertLogCalls(t, 0, 0, 0)

   e := errors.New("err")
   checkFatal(e)
   assertLogCalls(t, 1, 0, 0)
}

// setup
func TestSetup(t *testing.T) {
   setup()
   if config.ResultFileName != resultFileName {
      t.Errorf("setup did not initialize correctly")
   }
}

// createChannels
func TestCreateChannels(t *testing.T) {
   input, output, workerDone := createChannels()
   input <- ""
   <-input
   output <- new(KV)
   <-output
   workerDone <- true
   <-workerDone
}

// reportResults
func TestReportResults(t *testing.T) {
   config.Start = time.Now()
   logger = &MockLogger{}
   initMockLogger()

   reportResults()
   assertLogCalls(t, 0, 1, 0)
}

// writeResults
func TestWriteResults(t *testing.T) {
   logger = &MockLogger{}
   initMockLogger()
   config = new(Config)
   config.ResultFileName = "test.txt"
   state = new(State)
   state.Visited = make(map[string][]string)
   state.Visited["foo"] = []string{"baz", "bar"}
   state.Visited["aaa"] = []string{}

   writeResults()

   file, err := os.Open(config.ResultFileName)
   if err != nil {
      t.Errorf("file open failed: %s", err)
   }
   data := make([]byte, 100)
   count, err := file.Read(data)
   if err != nil {
      t.Errorf("file read failed: %s", err)
   }
   s := string(data[:count])
   fooIndex := strings.Index(s, "foo")
   barIndex := strings.Index(s, "bar")
   bazIndex := strings.Index(s, "baz")
   aaaIndex := strings.Index(s, "aaa")
   words := []string{"foo", "bar", "baz", "aaa"}
   for _, e := range words {
      if strings.Index(s, e) == -1 {
         t.Errorf("%s not found", e)
      }
   }
   if fooIndex < aaaIndex {
      t.Errorf("foo and aaa out of order")
   }
   if barIndex < bazIndex {
      t.Errorf("bar and baz out of order")
   }
   file.Close()
   os.Remove(config.ResultFileName)
   assertLogCalls(t, 0, 0, 0)
}

// report
func TestReport(t *testing.T) {
   logger = &MockLogger{}
   initMockLogger()
   state = new(State)
   state.Unvisited = make(map[string]bool)
   state.Visited = make(map[string][]string)
   state.Current = make(map[string]bool)

   report(state)

   assertLogCalls(t, 0, 1, 0)
}

// arbiter
func TestArbiter(t *testing.T) {
   logger = &MockLogger{}
   initMockLogger()
   input, output, _ := createChannels()
   go func() {
      kv := new(KV)
      kv.K = "link"
      kv.V = []string{}
      output<-kv
   }()
   go arbiter(input, output)
   s := <-input
   if s != rootUrl {
      t.Errorf("input channel sent %s", s)
   }
   assertLogCalls(t, 0, 1, 0)
}

// consumer
func assertKeyBool(t *testing.T, m map[string]bool, key string) {
   _, ok := m[key]
   if !ok {
      t.Errorf("%s not in map", key)
   }
}

func assertKeyString(t *testing.T, m map[string][]string, key string) {
   _, ok := m[key]
   if !ok {
      t.Errorf("%s not in map", key)
   }
}

func TestConsumer(t *testing.T) {
   state = new(State)
   arr := []string{}
   state.Unvisited = map[string]bool{"two" : true, "link" : true}
   state.Visited = map[string][]string{"one" : arr}
   state.Current = map[string]bool{"two" : true, "link" : true}

   kv := new(KV)
   kv.K = "link"
   kv.V = []string{"one", "two", "three"}

   consumer(state, kv)

   if len(state.Visited) != 2 {
      t.Errorf("len(state.Visited) was %d instead of 2", len(state.Unvisited))
   }
   assertKeyString(t, state.Visited, "one")
   assertKeyString(t, state.Visited, "link")

   if len(state.Unvisited) != 2 {
      t.Errorf("len(state.Unvisited) was %d instead of 2", len(state.Unvisited))
   }
   assertKeyBool(t, state.Unvisited, "two")
   assertKeyBool(t, state.Unvisited, "three")

   if len(state.Current) != 1 {
      t.Errorf("len(state.Current) was %d instead of 1", len(state.Current))
   }
   assertKeyBool(t, state.Current, "two")
}

// getArbitraryUnvisitedKey
func TestGetArbitrary(t *testing.T) {
   foo := "foo"
   state = new(State)
   state.Unvisited = map[string]bool{foo : true}

   item := getArbitraryUnvisitedKey(state)

   if item != foo {
      t.Errorf("foo not gotten")
   }
}

// producer
func TestProducer(t *testing.T) {
   // empty data structures - no work to do
   var retval bool
   input, _, _ := createChannels()
   state = new(State)
   state.Unvisited = make(map[string]bool)
   state.Visited = make(map[string][]string)
   state.Current = make(map[string]bool)
   retval = producer(state, input)
   if retval {
      t.Errorf("producer returned true on empty data structures")
   }

   // signal a worker that there is a link to be processed
   state.Unvisited = map[string]bool{"link" : true}
   inner := func() {
      retval = producer(state, input)
   }
   go inner()
   item := <-input
   if item != "link" {
      t.Errorf("producer sent %s down channel", item)
   }
   if !retval {
      t.Errorf("producer returned false on non-empty data structures")
   }

   // all work that needs to be done is being done already
   state.Current = map[string]bool{"link" : true}
   retval = producer(state, input)
   if !retval {
      t.Errorf("producer returned false on no work done")
   }
}

// worker
func TestWorker(t *testing.T) {
   config = new(Config)
   config.UrlMatcher = new(urlmatcher.UrlMatcher)
   config.UrlMatcher.Pattern = urlMatcherPattern
   config.UrlMatcher.Base = rootUrl
   initMockLogger()
   network = MockGet
   byteReader = MockIoReader
   input, output, workerDone := createChannels()

   go func() {
      input <- "uri"
      close(input)
   }()
   go worker(1, input, output, workerDone)
   kv := <-output
   result := <-workerDone

   if kv.K != "uri" {
      t.Errorf("kv.K wrong value: %s", kv.K)
   }
   if len(kv.V) != 1 {
      t.Errorf("kv.V wrong value: %s", kv.V)
   }
   if kv.V[0] != "http://digitalocean.com/link" {
      t.Errorf("wrong kv.V[0]: %s", kv.V[0])
   }
   if !result {
      t.Errorf("workerDone channel message borked")
   }
}

// crawlPage
func MockGetError(uri string) (*http.Response, error) {
   return nil, errors.New("err")
}

func MockGet(uri string) (*http.Response, error) {
   resp := new(http.Response)
   resp.Status = "200 OK"
   resp.Body = nil
   return resp, nil
}

func MockIoReaderError (r io.Reader) ([]byte, error) {
   return nil, nil
}

func MockIoReaderMalformedXml (r io.Reader) ([]byte, error) {
   html := "$%^@$%^#%^&$%^"
   byteArray := []byte(html)
   return byteArray, nil
}

func MockIoReader(r io.Reader) ([]byte, error) {
   html := "<html><head></head><body><a href=\"link\">txt</a></body></html>"
   byteArray := []byte(html)
   return byteArray, nil
}

func TestCrawlPage(t *testing.T) {
   // network error
   logger = &MockLogger{}
   initMockLogger()
   network = MockGetError
   links := crawlPage("uri")
   if len(links) > 0 {
      t.Errorf("links not empty")
   }
   assertLogCalls(t, 0, 1, 1)

   // byte reading error
   initMockLogger()
   network = MockGet
   byteReader = MockIoReaderError
   links = crawlPage("uri")
   if len(links) > 0 {
      t.Errorf("links not empty")
   }
   assertLogCalls(t, 0, 1, 1)

   // xml parsing error
   config = new(Config)
   config.UrlMatcher = new(urlmatcher.UrlMatcher)
   config.UrlMatcher.Pattern = urlMatcherPattern
   config.UrlMatcher.Base = rootUrl
   initMockLogger()
   network = MockGet
   byteReader = MockIoReaderMalformedXml
   links = crawlPage("uri")
   if len(links) > 0 {
      t.Errorf("links not empty")
   }
   assertLogCalls(t, 0, 1, 1)

   // success
   config = new(Config)
   config.UrlMatcher = new(urlmatcher.UrlMatcher)
   config.UrlMatcher.Pattern = urlMatcherPattern
   config.UrlMatcher.Base = rootUrl
   initMockLogger()
   network = MockGet
   byteReader = MockIoReader
   links = crawlPage("uri")
   if len(links) != 1 {
      t.Errorf("links not populated")
   }
   assertLogCalls(t, 0, 1, 1)
}

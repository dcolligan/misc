// A package for matching URLs against regexes and canonicalizing URLs
package urlmatcher

import (
   "log"
   "regexp"
   "fmt"
   "net/url"
)

const (
   defaultScheme = "http"
)

type UrlMatcher struct {
   Pattern string
   Base string
}

// determines whether str matches the regex
func (matcher *UrlMatcher) isMatch(str string) bool {
   matched, err := regexp.MatchString(matcher.Pattern, str)
   if err != nil {
      log.Fatal(err)
   }
   return matched
}

// canonicalizes the URL
func (matcher *UrlMatcher) canonicalURL(uri *url.URL) string {
   var s string

   // add a default path if implicit
   // or, prepend path with a slash if path doesn't have one
   if len(uri.Path) == 0 || uri.Path[0] != '/' {
      uri.Path = "/" + uri.Path
   }

   // strip out the fragment and opaque data
   if uri.IsAbs() {
      if len(uri.RawQuery) > 0 {
         s = fmt.Sprintf("%s://%s%s?%s", defaultScheme, uri.Host, uri.Path, uri.RawQuery)
      } else {
         s = fmt.Sprintf("%s://%s%s", defaultScheme, uri.Host, uri.Path)
      }
   } else {
      if len(uri.RawQuery) > 0 {
         s = fmt.Sprintf("%s%s?%s", matcher.Base, uri.Path, uri.RawQuery)
      } else {
         s = fmt.Sprintf("%s%s", matcher.Base, uri.Path)
      }
   }

   return s
}

// determines if uri is a valid URL for our purposes
func (matcher *UrlMatcher) IsValidURL(uri string) (bool, string) {
   u, err := url.Parse(uri)
   if err != nil {
      log.Fatal(err)
      return false, ""
   }
   c := matcher.canonicalURL(u)
   return matcher.isMatch(c), c
}

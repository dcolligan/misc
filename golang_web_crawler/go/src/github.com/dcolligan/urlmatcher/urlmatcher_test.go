package urlmatcher

import (
   "testing"
   "net/url"
)

func TestUrlMatcherString(t *testing.T) {

   uris := map[string]bool {
      "http://digitalocean.com" : true,
      "https://digitalocean.com" : true,
      "http://digitalocean.com/index" : true,
      "https://digitalocean.com/index" : true,
      "http://www.digitalocean.com" : false,
      "https://www.digitalocean.com" : false,
      "http://www.facebook.com" : false,
      "https://www.facebook.com" : false,
      "http://facebook.com" : false,
      "https://facebook.com" : false,
      "http://example.com/?q=http://digitalocean.com" : false,
   }

   pattern := "^https?://digitalocean.com"
   um := new(UrlMatcher)
   um.Pattern = pattern

   for uri, result := range uris {
      matched := um.isMatch(uri)
      if result != matched {
         t.Errorf("%s was %s instead of %s", uri, matched, result)
      }
   }
}

func TestCanonicalUrl(t *testing.T) {
   pattern := "^https?://digitalocean.com"
   um := new(UrlMatcher)
   um.Pattern = pattern
   um.Base = "http://digitalocean.com"

   matchingUrl := "http://digitalocean.com/"

   uris := []string{"/", "", um.Base, "#", "http://digitalocean.com/#"}

   for _, u := range uris {
      uri, _ := url.Parse(u)
      can := um.canonicalURL(uri)
      if can != matchingUrl {
         t.Errorf("%s is not equal to %s (%s)", can, matchingUrl, u)
      }
   }

   uriMap := map[string]string{
      "/security/" : um.Base + "/security/",
      "security/" : um.Base + "/security/",
   }

   for k, v := range uriMap {
      uri, _ := url.Parse(k)
      can := um.canonicalURL(uri)
      if can != v {
         t.Errorf("%s is not equal to %s (%s)", can, v, k)
      }
   }

}

func TestUrlMatcherURL(t *testing.T) {

   pattern := "^https?://digitalocean.com"
   um := new(UrlMatcher)
   um.Pattern = pattern
   um.Base = "http://digitalocean.com"

   uris := map[string]bool {
      "http://digitalocean.com" : true,
      "/" : true,
      "" : true,
      "#frag" : true,
      "/path?q=arg#frag#malformed" : true,
      "http://othersite.org" : false,
      "https://othersite.org/path?q=arg#frag" : false,
      "https://othersite.org/path?q=arg#frag#malformed" : false,
   }

   for uri, result := range uris {
      matched, _ := um.IsValidURL(uri)
      if result != matched {
         t.Errorf("%s was %s instead of %s", uri, matched, result)
      }
   }
}

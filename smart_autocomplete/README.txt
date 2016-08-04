=== Match strategy ===

Each diagnosis name is given a score and the smart_autocomplete function returns a
predefined number of lowest-ranking scores.  The scores are computed by, in order of
lowest score to highest:

   - determining if the diagnosis name is the exact match of the query
   - determining if the diagnosis name is a substring of the query, starting at the first character
   - determining if any token of the diagnosis name (token = whitespace-delineated printable characters) is the exact match of the query
   - the edit distance of the diagnosis name and the query

Ties are resolved by the lexicographical order of the diagnosis names.

=== Match improvements ===

- Having a map of common synonyms of ailments (for instance, flu -> influenza) would allow us to return those synonyms with a relatively low score
- Having a map of related conditions (for instance, alzheimer's -> dementia) would allow us to return similar ailments to the caller with a relatively low score

=== Performance improvements ===

- Caching the results of smart_autocomplete arguments and return values, if the method is called often with the same parameters
- Keeping a heap of the top scores as they are computed, rather than sorting the list at the end
- The cost of the repeated edit distance calls can probably be mitigated using more advanced approximate string matching techniques

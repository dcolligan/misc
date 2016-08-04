#!/usr/bin/env python

limit = 5

def edit_distance(x, y):
   num_rows = len(x) + 1
   num_cols = len(y) + 1

   M = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
   for i in range(num_rows):
      M[i][0] = i
   for j in range(num_cols):
      M[0][j] = j

   for i in range(len(x)):
      for j in range(len(y)):
         if x[i] == y[j]: 
            cost = 0
         else:
            cost = 1
         M[i + 1][j + 1] = min(
               M[i + 1][j] + 1, 
               M[i][j + 1] + 1, 
               M[i][j] + cost)
   return M[-1][-1]

def compute_score(name, query):
   # exact match
   if name == query:
      return -3

   # substring starting at first character
   if name.find(query) == 0:
      return -2

   # exact match on token
   if len(query.split()) == 1:
      splits = name.split()
      for split in splits:
         if split == query:
            return -1

   # edit distance
   return edit_distance(name, query)

def smart_autocomplete(diagnosis_names, query):
   score_name = []
   for name in diagnosis_names:
      score = compute_score(name, query)
      score_name.append((score, name))

   score_name.sort()
   return [x[1] for x in score_name][:limit]


if __name__ == '__main__':
   diagnosis_names = ['flu', 'influenza', 'spanish flu', 'ebola', 'headache', 'fever', 'kidney stone', 'food poisoning', 'fungus', 'sars', 'smallpox', 'scarlet fever', 'alzheimer\'s', 'dementia', 'fluid overdose'] # obviously, not all of these are real conditions
   query = 'flu'
   results = smart_autocomplete(diagnosis_names, query)
   for result in results:
      print result

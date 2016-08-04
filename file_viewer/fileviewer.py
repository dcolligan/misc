import web
import os
import mimetypes

urls = (
   '(.*)', 'index'
)

default_path = '/'
base_path = os.getcwd() + '/'
browser_extensions = set(['mp3', 'py'])

class TemplateContext(object): pass


class FileItem(object):

   def __init__(self, filename):
      self.name = os.path.basename(filename)
      self.path = os.path.relpath(filename, base_path)
      if os.path.isdir(filename):
         self.isdir = True
      else:
         self.isdir = False
      self.ext = os.path.splitext(filename)[1][1:]
      if self.ext in browser_extensions:
         self.be = True 
      else:
         self.be = False

def escape(path):
   if path[0] == '/':
      path = path[1:]
   full_path = os.path.join(base_path, path)
   if not os.path.exists(full_path):
      return False
   if os.path.islink(full_path):
      return False
   return os.path.abspath(path)

def dir_list(dirpath):
   filelist = []
   listdir = os.listdir(dirpath)
   listdir.sort()
   for f in listdir:
      full_path = os.path.join(dirpath, f)
      if os.path.islink(full_path):
         continue
      file_item = FileItem(full_path)
      filelist.append(file_item)
   template = web.template.frender('fileviewer.html')
   template_context = TemplateContext()
   template_context.filelist = filelist
   template_context.home_path = '/'
   if dirpath == base_path[:-1]:
      template_context.up_path = '/'
   else:
      template_context.up_path = '/' +  os.path.relpath(os.path.dirname(dirpath), base_path)
   template_context.path = os.path.relpath(dirpath, base_path)
   if template_context.path == '.':
      template_context.path = '/'
   else:
      template_context.path = '/' + template_context.path
   template_context.base_path = base_path
   return template(template_context)

def file_download(filepath):
   content_type = mimetypes.guess_type(filepath)[0]
   filename = os.path.basename(filepath)
   content_disposition = 'attachment; filename=%s' % filename
   web.header('Content-type', content_type)
   web.header('Content-disposition', content_disposition)
   f = file(filepath)
   return f.read()

class index:

   def GET(self, path):
      if not path:
         path = default_path
      else:
         path = escape(path)
         
      if not path:
         return web.webapi.NotFound()

      if os.path.isdir(path):
         return dir_list(path)
      elif os.path.isfile(path):
         return file_download(path)
      else:
         return web.webapi.NotFound()

if __name__ == "__main__": 
   app = web.application(urls, globals())
   app.run() 


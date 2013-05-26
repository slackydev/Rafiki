'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Based on Collin <http://keeyai.com> Greens: DirTreeCtrl
| Modified by Jarl <slacky> Holta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
import wx, os, sys

ICONS = 'src/icons/fileext/'

audio  = ['.mp3','.mp2','.wav','.flac','.raw','.ogg']
video  = ['.mpeg','.mp4','.vp8','.flv','.fla','.avi','.m4v','.mov','.mkv','.3gp']
image  = ['.gif','.bmp','.jpg','.jpeg','.png','.ico','.tiff','.tif','.tga','.psd','.targa', '.pix','.xbm','.svg']
compr  = ['.zip','.rar','.gz','.tar','.jar','.bz2','.7z','.ipg','.tgz']
web    = ['.htm','.html','.asp','.aspx','.js','.css','.style','xml']
java   = ['.java','.class']
php    = ['.php']
python = ['.py','.pyw','.pyx']
ruby   = ['.rb']
shell  = ['.sh','.bat','.cmd','.btm']
text   = ['.dot', '.doc', '.dotx', '.docx', '.txt', '.odt', '.rtf','.c','.h','.o','.d','.r','.pas','.scar','.simba','.pl','.m','.lua','.coffee','.as']
binary = ['.pyc','.pyd','.dll','.so','.exe','.pyo','.egg', '.class', '.bin']

fileext = [audio,video,image,compr,web,java,php,python,ruby,shell,text,binary]
fileextImg = ['audio.png', 'video.png', 'image.png', 'compressed.png', 'web.png',
              'java.png', 'php.png', 'python.png', 'ruby.png', 'shell.png',
              'text.png','binary.png']

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Simple class for using as the data object in the DirTreeCtrl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
class Directory:
    #------------------------------------------------------------------------
    __name__ = 'Directory'
    def __init__(self, directory=''):
        self.directory = directory


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| A wx.TreeCtrl that is used for displaying directory structures.
| Virtually handles paths to help with memory management.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
class DirTreeCtrl(wx.TreeCtrl):
    #------------------------------------------------------------------------
    def __init__(self, parent):
        """Initializes the tree and binds some events we need for
        making this dynamically load its data."""
        wx.TreeCtrl.__init__(self, parent, style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS)

        # bind events
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.TreeItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.TreeItemCollapsing)
        
        # option to delete node items from tree when node is collapsed
        self.DELETEONCOLLAPSE = False
        
        # some hack-ish code here to deal with imagelists
        self.iconentries = {}
        self.imagelist = wx.ImageList(16,16)

        # default = rafiki
        ico = wx.Image(ICONS + "rafiki.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        key = self.imagelist.Add(ico)
        self.iconentries['root'] = key
        
    def addIcon(self, filepath, wxBitmapType, name):
        try:
            if os.path.exists(filepath):
                key = self.imagelist.Add(wx.Bitmap(filepath, wxBitmapType))
                self.iconentries[name] = key
        except Exception, e:
            pass

    def SetDeleteOnCollapse(self, selection):
        """Sets the tree option to delete leaf items when the node is
        collapsed. Will slow down the tree slightly but will probably save memory."""
        if type(selection) == type(True):
            self.DELETEONCOLLAPSE = selection
            
    def SetRootDir(self, directory):
        """Sets the root directory for the tree. Throws an exception
        if the directory is invalid.
        @param directory: directory to load
        """

        # check if directory exists and is a directory
        if not os.path.isdir(directory):
            raise Exception("%s is not a valid directory" % directory)
        
        # delete existing root, if any
        self.DeleteAllItems()
        rootdir = directory.split(os.sep)[-1]

        # add directory as root
        root = self.AddRoot(rootdir)
        self.SetPyData(root, Directory(directory))
        self.SetItemImage(root, self.iconentries['root'])
        
        # load items
        self._loadDir(root, directory)
        self.AssignImageList(self.imagelist)
        self.Expand(root)

    def _loadDir(self, item, directory):
        """Private function that gets called to load the file list
        for the given directory and append the items to the tree.
        Throws an exception if the directory is invalid.

        @note: does not add items if the node already has children"""

        # check if directory exists and is a directory
        if not os.path.isdir(directory):
            raise Exception("%s is not a valid directory" % directory)

        # check if node already has children
        if self.GetChildrenCount(item) == 0:
            files = os.listdir(directory)

            for f in files:
                imagekey = self.getIcon(os.path.join(directory, f))

                if os.path.isdir(os.path.join(directory, f)):
                    child = self.AppendItem(item, f, image=imagekey)
                    self.SetItemHasChildren(child, True)
                    self.SetPyData(child, Directory(os.path.join(directory, f)))

                else:
                    self.AppendItem(item, f, image=imagekey)
      
    def getIcon(self, filedir):
        ico = wx.Image(ICONS + "file.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        if os.path.isdir(filedir):
            ico = wx.Image(ICONS + "folder.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
            key = self.imagelist.Add(ico)
            self.iconentries['directory'] = key
            return key

        name, ext = os.path.splitext(filedir)
        ext = ext.lower()
        for i,exts in enumerate(fileext):
            if ext in exts:
                ico = wx.Image(ICONS + fileextImg[i], wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        return self.imagelist.Add(ico)
        
    def TreeItemExpanding(self, event):
        """Called when a node is about to expand. Loads the node's
        files from the file system."""
        item = event.GetItem()
        
        # check if item has directory data
        if type(self.GetPyData(item)) == type(Directory()):
            d = self.GetPyData(item)
            self._loadDir(item, d.directory)
        else:
           pass
            
        event.Skip()

    def TreeItemCollapsing(self, event):
        """Called when a node is about to collapse. Removes
        the children from the tree if self.DELETEONCOLLAPSE is
        set - see L{SetDeleteOnCollapse}
        """
        item =  event.GetItem()
        
        # delete the node's children if that tree option is set
        if self.DELETEONCOLLAPSE:
            self.DeleteChildren(item)
            
        event.Skip()
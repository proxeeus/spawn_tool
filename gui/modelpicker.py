# This is a small example program for clicking on 3D objects. A panda, a teapot,
# and a cube will be on screen. When you click on the screen the console will
# tell you the nodePath of what you have clicked on. Its basically a watered down
# version of the tutorial included with Panda 3D 1.0.4. However, all the functionality
# for picking 3D objects is encapsulated into the Picker class which you may feel
# free to use in your own code.

import direct.directbase.DirectStart
#for the events
from direct.showbase import DirectObject
#for collision stuff
from pandac.PandaModules import *
from gui.picker import Picker
import globals

class ModelPicker(DirectObject.DirectObject):
   def __init__(self, topNode = None):
      #setup collision stuff
      self.topNode = topNode
      self.picker= CollisionTraverser()
      self.queue=CollisionHandlerQueue()

      self.pickerNode=CollisionNode('mouseRay')
      self.pickerNP=camera.attachNewNode(self.pickerNode)

      self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

      self.pickerRay=CollisionRay()

      self.pickerNode.addSolid(self.pickerRay)

      self.picker.addCollider(self.pickerNP, self.queue)

      #this holds the object that has been picked
      self.pickedObj=None

      self.lastSelectedObject = None

      self.accept('mouse1', self.selectMe)


   def setTopNode(self, topNode):
        """set the topmost node to traverse when detecting collisions"""
        self.topNode = topNode

   #this function is meant to flag an object as being somthing we can pick
   def makePickable(self,newObj):
      newObj.setTag('pickable','true')

   #this function finds the closest object to the camera that has been hit by our ray
   def getObjectHit(self, mpos): #mpos is the position of the mouse on the screen      self.pickedObj=None #be sure to reset this
      self.pickerRay.setFromLens(base.camNode, mpos.getX(),mpos.getY())
      self.picker.traverse(render)
      if self.queue.getNumEntries() > 0:
         self.queue.sortEntries()
         self.pickedObj=self.queue.getEntry(0).getIntoNodePath()

         parent=self.pickedObj.getParent()
         self.pickedObj=None

         while parent != render:
            if parent.getTag('pickable')=='true':
               self.pickedObj=parent
               return parent
            else:
               parent=parent.getParent()
      return None

   def getPickedObj(self):
         return self.pickedObj

   def selectMe(self):

      global picker

      if self.lastSelectedObject is None:
         self.lastSelectedObject = self.getObjectHit( base.mouseWatcherNode.getMouse())
         self.getObjectHit( base.mouseWatcherNode.getMouse())
         print self.lastSelectedObject
      else:
         picker = Picker(render)
         # object already selected so we need to do some shit there and unset it

         namedNode, thePoint, rawNode = picker.pick()
         print thePoint
         print self.lastSelectedObject.getTag("name")
         print "Heading: " ,self.lastSelectedObject.getH()
         self.lastSelectedObject.setPos(thePoint)
         self.lastSelectedObject = None
         globals.spawndialog.SetTitle('lol title')
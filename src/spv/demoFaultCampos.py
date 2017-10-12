#############################################################################
"""
Demo of dynamic warping for automatic picking
Author: Xinming Wu, University of Texas at Austin
Version: 2016.06.01
"""


from utils import * 
setupForSubset("campos")
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count
f1,f2,f3 = s1.getFirst(),s2.getFirst(),s3.getFirst()
d1,d2,d3 = s1.getDelta(),s2.getDelta(),s3.getDelta()
#############################################################################
gxfile = "gx" # input semblance image
epfile = "ep"  # planarity
effile = "ef"  # 1-planarity
fefile = "fe"  # 1-planarity
fpfile = "fp"  # fault strike;
vpfile = "vp"  # fault strike;
vtfile = "vt"  # fault strike;
ftfile = "ft"  # fault dip;
fvfile = "fv"  # fault dip;
ftfile  = "ft" # fault dip (theta)
fetfile = "fet" # fault likelihood thinned
fptfile = "fpt" # fault dip thinned
fttfile = "ftt" # fault dip thinned
fskfile = "skin"

pngDir = getPngDir()
pngDir = None
plotOnly = False
# These parameters control the scan over fault strikes and dips.
# See the class FaultScanner for more information.
minTheta,maxTheta = 65,80
minPhi,maxPhi = 0,360
sigmaPhi,sigmaTheta=4,8

def main(args):
  #goPlanar()
  #goFaultOrientScan()
  #goSurfaceVoting()
  #goFvPlanar()
  goSkins()
def goPlanar():
  gx = readImage3D(gxfile)
  if not plotOnly:
    lof = LocalOrientFilter(4,1,1)
    u1 = zerofloat(n1,n2,n3)
    u2 = zerofloat(n1,n2,n3)
    u3 = zerofloat(n1,n2,n3)
    ep = zerofloat(n1,n2,n3)
    lof.applyForNormalPlanar(gx,u1,u2,u3,ep)
    writeImage(epfile,ep)
  else:
    fp = readImage3D(fpfile)
  ep = pow(ep,8)
  plot3(gx,sub(1,ep),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="fl")

def goFaultOrientScan():
  gx = readImage3D(gxfile)
  ep = readImage3D(epfile)
  fos = FaultOrientScanner3(sigmaPhi,sigmaTheta)
  if not plotOnly:
    fe,fp,ft = fos.scan(minPhi,maxPhi,minTheta,maxTheta,ep)
    fet,fpt,ftt=fos.thin([fe,fp,ft])
    writeImage(fefile,fe)
    writeImage(fpfile,fp)
    writeImage(fetfile,fet)
    writeImage(fptfile,fpt)
    writeImage(fttfile,ftt)
  else:
    fp = readImage3D(fpfile)
    fe = readImage3D(fefile)
  print min(fe) 
  print max(fe) 
  plot3(gx,ep,cmin=0.1,cmax=0.7,cmap=jetRamp(1.0),
      clab="1-planarity",png="fl")
  plot3(gx,fe,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Enhanced",png="fl")
  plot3(gx,fp,cmin=1,cmax=360,cmap=jetFill(1.0),
      clab="Fault strike (degrees)",png="ph")

def goSurfaceVoting():
  gx = readImage3D(gxfile)
  if not plotOnly:
    fet = readImage3D(fetfile)
    fpt = readImage3D(fptfile)
    ftt = readImage3D(fttfile)
    osv = OptimalSurfaceVoterP(10,30,20)
    osv.setStrainMax(0.2,0.2)
    osv.setSurfaceSmoothing(2,2)
    fv,vp,vt = osv.applyVoting(4,0.3,fet,fpt,ftt)
    writeImage(fvfile,fv)
    writeImage(vpfile,vp)
    writeImage(vtfile,vt)
  else:
    fv = readImage3D(fvfile)
  ep = readImage3D(epfile)
  ep = sub(1,pow(ep,8))
  plot3(gx,ep,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="fl")
  plot3(gx,fv,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Surface voting",png="fl")

def goSkins():
  gx = readImage3D(gxfile)
  if not plotOnly:
    osv = OptimalSurfaceVoterP(10,20,30)
    fv = readImage3D(fvfile)
    vp = readImage3D(vpfile)
    vt = readImage3D(vtfile)
    ep = readImage3D("fep")
    ft,pt,tt = osv.thin([fv,vp,vt])
    fsk = FaultSkinner()
    fsk.setMaxDeltaStrike(20)
    fsk.setGrowing(5,0.3)
    seeds = fsk.findSeeds(10,0.9,ep,ft,pt,tt)
    skins = fsk.findSkins(0.8,2000,seeds,fv,vp,vt)
    for skin in skins:
      skin.smooth(5)
    #writeSkins(fskfile,skins)
  else:
    fv = readImage3D(fvfile)
    skins = readSkins(fskfile)
  plot3(gx,clab="Amplitude",png="seis")
  plot3(gx,fv,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Voting score",png="fv")
  plot3(gx,fv,cmin=0.0,cmax=180,cmap=hueFill(1.0),
      clab="Fault strike",png="fp")
  plot3(gx,skinx=skins,png="skinv")

def goFvPlanar():
  fv = readImage3D(fvfile)
  u1 = zerofloat(n1,n2,n3)
  u2 = zerofloat(n1,n2,n3)
  u3 = zerofloat(n1,n2,n3)
  ep = zerofloat(n1,n2,n3)
  lof = LocalOrientFilter(4,2,2)
  lof.applyForNormalPlanar(fv,u1,u2,u3,ep)
  writeImage("fep",ep)

def gain(x):
  g = mul(x,x) 
  ref = RecursiveExponentialFilter(100.0)
  ref.apply1(g,g)
  y = zerofloat(n1,n2)
  div(x,sqrt(g),y)
  return y

def smooth(sig,u):
  v = copy(u)
  rgf = RecursiveGaussianFilterP(sig)
  rgf.apply0(u,v)
  return v

def smooth2(sig1,sig2,u):
  v = copy(u)
  rgf1 = RecursiveGaussianFilterP(sig1)
  rgf2 = RecursiveGaussianFilterP(sig2)
  rgf1.apply0X(u,v)
  rgf2.applyX0(v,v)
  return v


def normalize(e):
  emin = min(e)
  emax = max(e)
  return mul(sub(e,emin),1.0/(emax-emin))

#############################################################################
# graphics

def jetFill(alpha):
  return ColorMap.setAlpha(ColorMap.JET,alpha)
def jetFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.JET,a)
def jetRamp(alpha):
  return ColorMap.setAlpha(ColorMap.JET,rampfloat(0.0,alpha/256,256))
def bwrFill(alpha):
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,alpha)
def bwrNotch(alpha):
  a = zerofloat(256)
  for i in range(len(a)):
    if i<128:
      a[i] = alpha*(128.0-i)/128.0
    else:
      a[i] = alpha*(i-127.0)/128.0
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,a)
def hueFill(alpha):
  return ColorMap.getHue(0.0,1.0,alpha)
def hueFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.getHue(0.0,1.0),a)

def addColorBar(frame,clab=None,cint=None):
  cbar = ColorBar(clab)
  if cint:
    cbar.setInterval(cint)
  cbar.setFont(Font("Arial",Font.PLAIN,32)) # size by experimenting
  cbar.setWidthMinimum
  cbar.setBackground(Color.WHITE)
  frame.add(cbar,BorderLayout.EAST)
  return cbar

def convertDips(ft):
  return FaultScanner.convertDips(0.2,ft) # 5:1 vertical exaggeration

def plot3(f,g=None,cmin=-2,cmax=2,cmap=None,clab=None,cint=None,
          sx=None,sy=None,surf=None,fd=None,cells=None,
          skins=None,skinx=None,smax=0.0,links=False,png=None):
  n3 = len(f)
  n2 = len(f[0])
  n1 = len(f[0][0])
  s1,s2,s3=Sampling(n1),Sampling(n2),Sampling(n3)
  d1,d2,d3 = s1.delta,s2.delta,s3.delta
  f1,f2,f3 = s1.first,s2.first,s3.first
  l1,l2,l3 = s1.last,s2.last,s3.last
  sf = SimpleFrame(AxesOrientation.XRIGHT_YIN_ZDOWN)
  #sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  cbar = None
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      ipg.setClips(-2.0,2.0)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMapListener(cbar)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-2,2)
    if cmin!=None and cmax!=None:
      ipg.setClips2(cmin,cmax)
    if cmap==None:
      cmap = jetFill(0.8)
    ipg.setColorModel2(cmap)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMap2Listener(cbar)
    sf.world.addChild(ipg)
  if cbar:
    cbar.setWidthMinimum(120)
  if cells:
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    cmap = ColorMap(0.0,1.0,ColorMap.JET)
    xyz,uvw,rgb = FaultCell.getXyzUvwRgbForLikelihood(0.7,cmap,cells,False)
    qg = QuadGroup(xyz,uvw,rgb)
    qg.setStates(ss)
    sf.world.addChild(qg)
  if surf:
    tg = TriangleGroup(True,surf)
    sf.world.addChild(tg)
  if skinx:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    #lms.setTwoSide(False)
    lms.setTwoSide(False)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.0))
    ss.add(ms)
    sg.setStates(ss)
    for skin in skinx:
      #cmap = ColorMap(0.0,1.0,ColorMap.JET)
      cmap = ColorMap(0.0,180,ColorMap.HUE)
      #tg = skin.getTriMesh(cmap)
      tg = skin.getTriMeshStrike(cmap)
      #tg = skin.getQuadMeshStrike(cmap)
      sg.addChild(tg)
    sf.world.addChild(sg)
  if skins:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    #lms.setTwoSide(True)
    lms.setTwoSide(False)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    sg.setStates(ss)
    size = 2.0
    if links:
      size = 0.5 
    for skin in skins:
      if smax>0.0: # show fault throws
        cmap = ColorMap(0.0,smax,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForThrow(size,cmap,False)
      else: # show fault likelihood
        cmap = ColorMap(0.25,1.0,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForLikelihood(size,cmap,False)
      qg = QuadGroup(xyz,uvw,rgb)
      qg.setStates(None)
      sg.addChild(qg)
      if links:
        xyz = skin.getCellLinksXyz()
        lg = LineGroup(xyz)
        sg.addChild(lg)
    sf.world.addChild(sg)
  ipg.setSlices(150,5,56)
  #ipg.setSlices(85,5,43)
  #ipg.setSlices(85,5,102)
  #ipg.setSlices(n1,0,n3) # use only for subset plots
  ipg.setSlices(n1,418,20)
  if cbar:
    sf.setSize(1037,700)
  else:
    sf.setSize(900,700)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  ov = sf.getOrbitView()
  zscale = 0.5*max(n2*d2,n3*d3)/(n1*d1)
  #zscale = 1.5*max(n2*d2,n3*d3)/(n1*d1)
  ov.setAxesScale(1.0,1.0,zscale)
  ov.setScale(1.6)
  #ov.setScale(2.5)
  ov.setWorldSphere(BoundingSphere(BoundingBox(f3,f2,f1,l3,l2,l1)))
  ov.setTranslate(Vector3(0.06,0.05,-0.08))
  ov.setAzimuthAndElevation(30.0,35.0)
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(720,1,pngDir+png+"cbar.png")
#############################################################################
# Run the function main on the Swing thread
import sys
class _RunMain(Runnable):
  def __init__(self,main):
    self.main = main
  def run(self):
    self.main(sys.argv)
def run(main):
  SwingUtilities.invokeLater(_RunMain(main)) 
run(main)